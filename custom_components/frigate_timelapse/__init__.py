"""The Frigate Timelapse integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .frigate_api import FrigateAPI
from .timelapse_manager import TimelapseManager

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Frigate Timelapse from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Initialize Frigate API
    frigate_api = FrigateAPI(entry.data["frigate_url"])

    # Verify connection
    try:
        cameras = await frigate_api.get_cameras()
        if not cameras:
            _LOGGER.error("No cameras found in Frigate")
            return False
    except Exception as err:
        _LOGGER.error("Failed to connect to Frigate: %s", err)
        return False

    # Initialize Timelapse Manager
    timelapse_manager = TimelapseManager(
        hass=hass,
        frigate_api=frigate_api,
        camera=entry.data["camera"],
        capture_interval=entry.data.get("capture_interval", 60),
        output_path=entry.data.get("output_path", "/media/timelapse"),
        fps=entry.data.get("fps", 30),
        resolution=entry.data.get("resolution", "1920x1080"),
    )

    # Store manager in hass.data
    hass.data[DOMAIN][entry.entry_id] = {
        "frigate_api": frigate_api,
        "timelapse_manager": timelapse_manager,
    }

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await _async_register_services(hass, timelapse_manager)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        timelapse_manager = hass.data[DOMAIN][entry.entry_id]["timelapse_manager"]
        await timelapse_manager.stop_capture()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _async_register_services(
    hass: HomeAssistant, manager: TimelapseManager
) -> None:
    """Register services for the integration."""
    from .const import (
        SERVICE_CAPTURE_IMAGE,
        SERVICE_GENERATE_TIMELAPSE,
        SERVICE_START_CAPTURE,
        SERVICE_STOP_CAPTURE,
    )

    async def handle_capture_image(call):
        """Handle capture image service."""
        await manager.capture_single_image()

    async def handle_generate_timelapse(call):
        """Handle generate timelapse service."""
        start_time = call.data.get("start_time")
        end_time = call.data.get("end_time")
        output_file = call.data.get("output_file")
        await manager.generate_timelapse(start_time, end_time, output_file)

    async def handle_start_capture(call):
        """Handle start capture service."""
        await manager.start_capture()

    async def handle_stop_capture(call):
        """Handle stop capture service."""
        await manager.stop_capture()

    hass.services.async_register(DOMAIN, SERVICE_CAPTURE_IMAGE, handle_capture_image)
    hass.services.async_register(
        DOMAIN, SERVICE_GENERATE_TIMELAPSE, handle_generate_timelapse
    )
    hass.services.async_register(DOMAIN, SERVICE_START_CAPTURE, handle_start_capture)
    hass.services.async_register(DOMAIN, SERVICE_STOP_CAPTURE, handle_stop_capture)
