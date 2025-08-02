import logging
from datetime import timedelta
import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

API_URL = "https://www.envertecportal.com/ApiStations/getStationInfo"


async def fetch_data(station_id):
    """Fetch data asynchronously from Envertech Solar Portal."""
    params = {"stationID": station_id}

    async with aiohttp.ClientSession() as session:
        try:
            with async_timeout.timeout(10):
                async with session.post(API_URL, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
        except Exception as err:
            _LOGGER.error("Error fetching data from Envertech: %s", err)
            raise


class EnvertechDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching data from Envertech API."""

    def __init__(self, hass, station_id):
        super().__init__(
            hass,
            _LOGGER,
            name="Envertech Solar Data Coordinator",
            update_interval=timedelta(seconds=30),
        )
        self.station_id = station_id

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            data = await fetch_data(self.station_id)
            return data
        except Exception as err:
            raise UpdateFailed(f"Error fetching Envertech data: {err}")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up Envertech sensors via config entry."""
    station_id = entry.data.get("station_id")
    coordinator = EnvertechDataUpdateCoordinator(hass, station_id)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    sensors = [
        ("Power", "Current Power", "W", "mdi:solar-power"),
        ("UnitEToday", "Daily Energy", "kWh", "mdi:solar-power"),
        ("UnitEMonth", "Monthly Energy", "kWh", "mdi:solar-power"),
        ("UnitEYear", "Yearly Energy", "kWh", "mdi:solar-power"),
        ("UnitETotal", "Total Energy", "kWh", "mdi:solar-power"),
    ]

    entities = [
        EnvertechSensor(coordinator, key, name, unit, icon)
        for key, name, unit, icon in sensors
    ]
    async_add_entities(entities)


class EnvertechSensor(SensorEntity):
    """Representation of an Envertech Solar sensor."""

    def __init__(self, coordinator, sensor_key, name, unit, icon=None):
        self.coordinator = coordinator
        self.sensor_key = sensor_key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.sensor_key}_{self.coordinator.station_id}"

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data or "Data" not in data:
            return None
        values = data["Data"]
        val = values.get(self.sensor_key)
        if val is None:
            return None
        if isinstance(val, str):
            try:
                # Entferne Einheiten wie "kWh" oder "W" aus dem String
                val_cleaned = (
                    val.replace(",", ".")
                       .replace("kWh", "")
                       .replace("W", "")
                       .strip()
                )
                return float(val_cleaned)
            except Exception as e:
                _LOGGER.warning("Could not convert value '%s' for sensor '%s': %s", val, self.sensor_key, e)
                return None
        return val

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
