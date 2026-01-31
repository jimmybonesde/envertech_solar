from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN

DEFAULT_UPDATE_INTERVAL = 30


class EnvertechConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="Envertech Solar",
                data=user_input,
                options={"update_interval": DEFAULT_UPDATE_INTERVAL},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("station_id"): str,
                }
            ),
            description_placeholders={
                "example_url": "https://www.envertecportal.com/terminal/systemhistory/YOUR_ID?sn=...",
                "id_placeholder": "YOUR_ID",
            },
        )


class EnvertechOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow handler for update_interval."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
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


def async_get_options_flow(
    config_entry: config_entries.ConfigEntry,
) -> EnvertechOptionsFlowHandler:
    return EnvertechOptionsFlowHandler(config_entry)
