from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .sensor import EnvertechDataUpdateCoordinator

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Integration via configuration.yaml (optional)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration from config entry."""
    update_interval = entry.options.get("update_interval", 30)
    station_id = entry.data.get("station_id")
    coordinator = EnvertechDataUpdateCoordinator(hass, station_id, update_interval)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])

def async_get_options_flow(config_entry):
    """OptionsFlow Handler für update_interval."""
    from .config_flow import EnvertechOptionsFlowHandler
    return EnvertechOptionsFlowHandler(config_entry)
