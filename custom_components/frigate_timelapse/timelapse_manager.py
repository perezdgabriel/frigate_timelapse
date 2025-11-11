"""Timelapse Manager for Frigate integration."""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import STATE_CAPTURING, STATE_GENERATING, STATE_IDLE, STATE_ERROR
from .frigate_api import FrigateAPI

_LOGGER = logging.getLogger(__name__)


class TimelapseManager:
    """Manage timelapse capture and generation."""

    def __init__(
        self,
        hass: HomeAssistant,
        frigate_api: FrigateAPI,
        camera: str,
        capture_interval: int,
        output_path: str,
        fps: int,
        resolution: str,
    ) -> None:
        """Initialize the timelapse manager."""
        self.hass = hass
        self.frigate_api = frigate_api
        self.camera = camera
        self.capture_interval = capture_interval
        self.output_path = output_path
        self.fps = fps
        self.resolution = resolution

        self._state = STATE_IDLE
        self._last_capture: datetime | None = None
        self._images_count = 0
        self._current_session: str | None = None
        self._capture_task = None
        self._state_callbacks: list[Callable] = []

    @property
    def state(self) -> str:
        """Get current state."""
        return self._state

    @property
    def last_capture(self) -> datetime | None:
        """Get last capture time."""
        return self._last_capture

    @property
    def images_count(self) -> int:
        """Get number of captured images in current session."""
        return self._images_count

    def register_state_callback(self, callback: Callable) -> None:
        """Register a callback for state changes."""
        self._state_callbacks.append(callback)

    def _set_state(self, state: str) -> None:
        """Set state and notify callbacks."""
        self._state = state
        for callback in self._state_callbacks:
            self.hass.async_create_task(callback())

    async def start_capture(self) -> None:
        """Start periodic image capture."""
        if self._state == STATE_CAPTURING:
            _LOGGER.warning("Capture already running")
            return

        # Create new session folder
        self._current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_path = Path(self.output_path) / "captures" / self._current_session
        session_path.mkdir(parents=True, exist_ok=True)

        self._images_count = 0
        self._set_state(STATE_CAPTURING)

        _LOGGER.info("Starting capture session: %s", self._current_session)

        # Schedule periodic captures
        self._capture_task = async_track_time_interval(
            self.hass,
            self._periodic_capture,
            timedelta(seconds=self.capture_interval),
        )

        # Capture first image immediately
        await self.capture_single_image()

    async def stop_capture(self) -> None:
        """Stop periodic image capture."""
        if self._capture_task:
            self._capture_task()
            self._capture_task = None

        self._set_state(STATE_IDLE)
        _LOGGER.info(
            "Stopped capture session: %s (captured %d images)",
            self._current_session,
            self._images_count,
        )

    async def _periodic_capture(self, now) -> None:
        """Periodic capture callback."""
        await self.capture_single_image()

    async def capture_single_image(self) -> bool:
        """Capture a single image from the camera."""
        try:
            image_data = await self.frigate_api.get_latest_image(self.camera)

            if not image_data:
                _LOGGER.error("Failed to get image from camera %s", self.camera)
                return False

            # Ensure session exists
            if not self._current_session:
                self._current_session = datetime.now().strftime("%Y%m%d_%H%M%S")

            session_path = Path(self.output_path) / "captures" / self._current_session
            session_path.mkdir(parents=True, exist_ok=True)

            # Save image with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            image_path = session_path / f"frame_{timestamp}.jpg"

            await self.hass.async_add_executor_job(
                self._save_image, image_path, image_data
            )

            self._last_capture = datetime.now()
            self._images_count += 1

            _LOGGER.debug("Captured image: %s", image_path)
            return True

        except Exception as err:
            _LOGGER.error("Error capturing image: %s", err)
            return False

    def _save_image(self, path: Path, data: bytes) -> None:
        """Save image data to file."""
        with open(path, "wb") as f:
            f.write(data)

    async def generate_timelapse(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        output_file: str | None = None,
    ) -> str | None:
        """Generate timelapse video from captured images."""
        self._set_state(STATE_GENERATING)

        try:
            # Use current session if not specified
            if not self._current_session:
                _LOGGER.error("No capture session available")
                self._set_state(STATE_ERROR)
                return None

            session_path = Path(self.output_path) / "captures" / self._current_session

            if not session_path.exists():
                _LOGGER.error("Session path does not exist: %s", session_path)
                self._set_state(STATE_ERROR)
                return None

            # Get list of images
            images = sorted(session_path.glob("frame_*.jpg"))

            # Filter by time range if specified
            if start_time or end_time:
                filtered_images = []
                for img in images:
                    # Extract timestamp from filename
                    timestamp_str = img.stem.replace("frame_", "")
                    img_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S_%f")

                    if start_time and img_time < start_time:
                        continue
                    if end_time and img_time > end_time:
                        continue
                    filtered_images.append(img)
                images = filtered_images

            if len(images) < 2:
                _LOGGER.error(
                    "Not enough images to create timelapse (found %d)", len(images)
                )
                self._set_state(STATE_ERROR)
                return None

            # Create output directory
            output_dir = Path(self.output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate output filename
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"timelapse_{self.camera}_{timestamp}.mp4"

            output_path = output_dir / output_file

            # Generate timelapse using ffmpeg
            success = await self.hass.async_add_executor_job(
                self._run_ffmpeg, session_path, output_path
            )

            if success:
                _LOGGER.info("Generated timelapse: %s", output_path)
                self._set_state(STATE_IDLE)
                return str(output_path)
            else:
                _LOGGER.error("Failed to generate timelapse")
                self._set_state(STATE_ERROR)
                return None

        except Exception as err:
            _LOGGER.error("Error generating timelapse: %s", err)
            self._set_state(STATE_ERROR)
            return None

    def _run_ffmpeg(self, input_path: Path, output_path: Path) -> bool:
        """Run ffmpeg to create timelapse video."""
        try:
            # Parse resolution
            width, height = self.resolution.split("x")

            # ffmpeg command to create timelapse
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file
                "-framerate",
                str(self.fps),
                "-pattern_type",
                "glob",
                "-i",
                str(input_path / "frame_*.jpg"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-vf",
                f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
                "-preset",
                "medium",
                "-crf",
                "23",
                str(output_path),
            ]

            _LOGGER.debug("Running ffmpeg command: %s", " ".join(cmd))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode == 0:
                _LOGGER.info("ffmpeg completed successfully")
                return True
            else:
                _LOGGER.error("ffmpeg failed: %s", result.stderr)
                return False

        except subprocess.TimeoutExpired:
            _LOGGER.error("ffmpeg timed out")
            return False
        except Exception as err:
            _LOGGER.error("Error running ffmpeg: %s", err)
            return False

    async def cleanup_old_sessions(self, days: int = 7) -> None:
        """Clean up old capture sessions."""
        try:
            captures_path = Path(self.output_path) / "captures"
            if not captures_path.exists():
                return

            cutoff = datetime.now() - timedelta(days=days)

            for session_dir in captures_path.iterdir():
                if not session_dir.is_dir():
                    continue

                # Parse session timestamp
                try:
                    session_time = datetime.strptime(session_dir.name, "%Y%m%d_%H%M%S")
                    if session_time < cutoff:
                        await self.hass.async_add_executor_job(
                            self._remove_directory, session_dir
                        )
                        _LOGGER.info("Cleaned up old session: %s", session_dir.name)
                except ValueError:
                    continue

        except Exception as err:
            _LOGGER.error("Error cleaning up old sessions: %s", err)

    def _remove_directory(self, path: Path) -> None:
        """Remove directory and its contents."""
        import shutil

        shutil.rmtree(path)
