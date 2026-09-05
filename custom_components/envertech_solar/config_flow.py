"""Configuration flow for Envertech Solar."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

DEFAULT_UPDATE_INTERVAL = 30


class EnvertechConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an Envertech Solar configuration flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> EnvertechOptionsFlowHandler:
        """Return the options flow handler."""
        return EnvertechOptionsFlowHandler()

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        errors = {}

        if user_input is not None:
            station_id = user_input["station_id"].strip()
            if not station_id:
                errors["station_id"] = "invalid_station_id"
            else:
                await self.async_set_unique_id(station_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Envertech Solar",
                    data={"station_id": station_id},
                    options={"update_interval": DEFAULT_UPDATE_INTERVAL},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("station_id"): str}),
            errors=errors,
            description_placeholders={
                "example_url": (
                    "https://www.envertecportal.com/terminal/systemhistory/YOUR_ID?sn=..."
                ),
                "id_placeholder": "YOUR_ID",
            },
        )


class EnvertechOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Envertech Solar options."""

    async def async_step_init(self, user_input=None):
        """Handle the options step."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "update_interval",
                        default=self.config_entry.options.get(
                            "update_interval", DEFAULT_UPDATE_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
                }
            ),
        )
