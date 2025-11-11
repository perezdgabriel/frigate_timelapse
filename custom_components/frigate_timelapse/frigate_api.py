"""Frigate API Client."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class FrigateAPI:
    """Class to interact with Frigate API."""

    def __init__(self, base_url: str) -> None:
        """Initialize Frigate API client."""
        self.base_url = base_url.rstrip("/")
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_cameras(self) -> list[str]:
        """Get list of available cameras from Frigate."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/config") as response:
                if response.status == 200:
                    data = await response.json()
                    cameras = list(data.get("cameras", {}).keys())
                    _LOGGER.debug("Found cameras: %s", cameras)
                    return cameras
                else:
                    _LOGGER.error("Failed to get cameras: %s", response.status)
                    return []
        except Exception as err:
            _LOGGER.error("Error getting cameras from Frigate: %s", err)
            return []

    async def get_camera_config(self, camera: str) -> dict[str, Any] | None:
        """Get configuration for a specific camera."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/config") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("cameras", {}).get(camera)
                return None
        except Exception as err:
            _LOGGER.error("Error getting camera config: %s", err)
            return None

    async def get_latest_image(self, camera: str) -> bytes | None:
        """Get latest snapshot from camera."""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/api/{camera}/latest.jpg"
            _LOGGER.debug("Fetching image from: %s", url)

            async with session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    _LOGGER.debug(
                        "Successfully fetched image (%d bytes)", len(image_data)
                    )
                    return image_data
                else:
                    _LOGGER.error("Failed to get image: %s", response.status)
                    return None
        except Exception as err:
            _LOGGER.error("Error getting latest image from %s: %s", camera, err)
            return None

    async def test_connection(self) -> bool:
        """Test connection to Frigate."""
        try:
            cameras = await self.get_cameras()
            return len(cameras) > 0
        except Exception:
            return False
