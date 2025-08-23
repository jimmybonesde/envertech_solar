from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.config_entry_flow import config_entry_only_config_schema
from .const import DOMAIN

# Damit Hassfest weiß, dass YAML nicht unterstützt wird
CONFIG_SCHEMA = config_entry_only_config_schema

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration via configuration.yaml (not used here)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
