from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

DEFAULT_UPDATE_INTERVAL = 60

class EnvertechConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Envertech Solar", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("station_id"): str
            }),
        )

class EnvertechOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    "update_interval",
                    default=self.config_entry.options.get("update_interval", DEFAULT_UPDATE_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
            }),
        )

def async_get_options_flow(config_entry):
    return EnvertechOptionsFlowHandler(config_entry)
