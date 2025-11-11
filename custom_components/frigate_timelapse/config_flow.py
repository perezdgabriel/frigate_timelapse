"""Config flow for Frigate Timelapse integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_FRIGATE_URL,
    CONF_CAMERA,
    CONF_CAPTURE_INTERVAL,
    CONF_OUTPUT_PATH,
    CONF_FPS,
    CONF_RESOLUTION,
    DEFAULT_CAPTURE_INTERVAL,
    DEFAULT_FPS,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_RESOLUTION,
)
from .frigate_api import FrigateAPI

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    frigate_api = FrigateAPI(data[CONF_FRIGATE_URL])

    try:
        cameras = await frigate_api.get_cameras()
        if not cameras:
            raise CannotConnect("No cameras found in Frigate")
    except Exception as err:
        raise CannotConnect(f"Cannot connect to Frigate: {err}")
    finally:
        await frigate_api.close()

    return {"title": f"Frigate Timelapse - {data[CONF_CAMERA]}", "cameras": cameras}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Frigate Timelapse."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._frigate_url: str | None = None
        self._cameras: list[str] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                frigate_api = FrigateAPI(user_input[CONF_FRIGATE_URL])
                cameras = await frigate_api.get_cameras()
                await frigate_api.close()

                if not cameras:
                    errors["base"] = "no_cameras"
                else:
                    self._frigate_url = user_input[CONF_FRIGATE_URL]
                    self._cameras = cameras
                    return await self.async_step_camera()

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_FRIGATE_URL, default="http://frigate:5000"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_camera(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle camera selection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            camera = user_input[CONF_CAMERA]

            # Check if already configured
            await self.async_set_unique_id(f"{self._frigate_url}_{camera}")
            self._abort_if_unique_id_configured()

            return await self.async_step_options(camera)

        return self.async_show_form(
            step_id="camera",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CAMERA): vol.In(self._cameras),
                }
            ),
            errors=errors,
        )

    async def async_step_options(
        self, camera: str, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options step."""
        if user_input is not None:
            data = {
                CONF_FRIGATE_URL: self._frigate_url,
                CONF_CAMERA: camera,
                CONF_CAPTURE_INTERVAL: user_input[CONF_CAPTURE_INTERVAL],
                CONF_OUTPUT_PATH: user_input[CONF_OUTPUT_PATH],
                CONF_FPS: user_input[CONF_FPS],
                CONF_RESOLUTION: user_input[CONF_RESOLUTION],
            }

            return self.async_create_entry(
                title=f"Frigate Timelapse - {camera}",
                data=data,
            )

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CAPTURE_INTERVAL, default=DEFAULT_CAPTURE_INTERVAL
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
                    vol.Required(CONF_OUTPUT_PATH, default=DEFAULT_OUTPUT_PATH): str,
                    vol.Required(CONF_FPS, default=DEFAULT_FPS): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=60)
                    ),
                    vol.Required(CONF_RESOLUTION, default=DEFAULT_RESOLUTION): vol.In(
                        ["1920x1080", "1280x720", "3840x2160", "2560x1440"]
                    ),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Frigate Timelapse."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CAPTURE_INTERVAL,
                        default=self.config_entry.data.get(
                            CONF_CAPTURE_INTERVAL, DEFAULT_CAPTURE_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
                    vol.Required(
                        CONF_OUTPUT_PATH,
                        default=self.config_entry.data.get(
                            CONF_OUTPUT_PATH, DEFAULT_OUTPUT_PATH
                        ),
                    ): str,
                    vol.Required(
                        CONF_FPS,
                        default=self.config_entry.data.get(CONF_FPS, DEFAULT_FPS),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                    vol.Required(
                        CONF_RESOLUTION,
                        default=self.config_entry.data.get(
                            CONF_RESOLUTION, DEFAULT_RESOLUTION
                        ),
                    ): vol.In(["1920x1080", "1280x720", "3840x2160", "2560x1440"]),
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
