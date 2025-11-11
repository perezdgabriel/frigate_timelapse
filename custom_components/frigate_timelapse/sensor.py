"""Sensor platform for Frigate Timelapse."""

from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Frigate Timelapse sensors."""
    timelapse_manager = hass.data[DOMAIN][config_entry.entry_id]["timelapse_manager"]
    camera = config_entry.data["camera"]

    sensors = [
        TimelapseStatusSensor(timelapse_manager, camera, config_entry.entry_id),
        TimelapseImageCountSensor(timelapse_manager, camera, config_entry.entry_id),
        TimelapseLastCaptureSensor(timelapse_manager, camera, config_entry.entry_id),
    ]

    async_add_entities(sensors)


class TimelapseBaseSensor(SensorEntity):
    """Base class for Frigate Timelapse sensors."""

    def __init__(self, manager, camera: str, entry_id: str) -> None:
        """Initialize the sensor."""
        self._manager = manager
        self._camera = camera
        self._entry_id = entry_id
        self._attr_has_entity_name = True

    async def async_added_to_hass(self) -> None:
        """Register state change callback."""
        self._manager.register_state_callback(self.async_write_ha_state)


class TimelapseStatusSensor(TimelapseBaseSensor):
    """Sensor for timelapse status."""

    def __init__(self, manager, camera: str, entry_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(manager, camera, entry_id)
        self._attr_name = "Status"
        self._attr_unique_id = f"{entry_id}_status"
        self._attr_icon = "mdi:camera-timer"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self._manager.state

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        return {
            "camera": self._camera,
            "capture_interval": self._manager.capture_interval,
            "fps": self._manager.fps,
            "resolution": self._manager.resolution,
            "output_path": self._manager.output_path,
        }


class TimelapseImageCountSensor(TimelapseBaseSensor):
    """Sensor for number of captured images."""

    def __init__(self, manager, camera: str, entry_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(manager, camera, entry_id)
        self._attr_name = "Images Captured"
        self._attr_unique_id = f"{entry_id}_images_count"
        self._attr_icon = "mdi:image-multiple"
        self._attr_native_unit_of_measurement = "images"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self._manager.images_count


class TimelapseLastCaptureSensor(TimelapseBaseSensor):
    """Sensor for last capture time."""

    def __init__(self, manager, camera: str, entry_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(manager, camera, entry_id)
        self._attr_name = "Last Capture"
        self._attr_unique_id = f"{entry_id}_last_capture"
        self._attr_icon = "mdi:clock-outline"
        self._attr_device_class = "timestamp"

    @property
    def native_value(self) -> datetime | None:
        """Return the state of the sensor."""
        return self._manager.last_capture
