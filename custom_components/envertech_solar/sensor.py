from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from datetime import timedelta
import requests
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)
DOMAIN = "envertech_solar"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    station_id = entry.data["station_id"]

    async def fetch_data():
        try:
            url = "https://www.envertecportal.com/ApiStations/getStationInfo"
            response = requests.post(url, params={"stationID": station_id}, timeout=10)
            return response.json().get("Data", {})
        except Exception as e:
            _LOGGER.error(f"Error fetching Envertech data: {e}")
            return {}

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="envertech_solar",
        update_method=fetch_data,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_config_entry_first_refresh()

    sensors = [
        EnvertechSensor(coordinator, "Power", "Aktuelle Leistung", "W"),
        EnvertechSensor(coordinator, "UnitEToday", "Tagesenergie", "kWh"),
        EnvertechSensor(coordinator, "UnitETotal", "Gesamtenergie", "kWh"),
        EnvertechSensor(coordinator, "UnitEMonth", "Monatsenergie", "kWh"),
        EnvertechSensor(coordinator, "UnitEYear", "Jahresenergie", "kWh"),
    ]
    async_add_entities(sensors)

class EnvertechSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name, unit):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"Solar{name.replace(' ', '')}"
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        return float(self.coordinator.data.get(self._key, 0))
