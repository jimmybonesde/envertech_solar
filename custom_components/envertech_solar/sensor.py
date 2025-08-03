import logging
from datetime import timedelta
import aiohttp
import async_timeout

MANUFACTURER = "JimmyBones"

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
API_URL = "https://www.envertecportal.com/ApiStations/getStationInfo"


async def fetch_data(station_id):
    params = {"stationID": station_id}
    async with aiohttp.ClientSession() as session:
        try:
            with async_timeout.timeout(10):
                async with session.post(API_URL, params=params) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as err:
            _LOGGER.error("Error fetching data from Envertech: %s", err)
            raise


class EnvertechDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, station_id):
        super().__init__(
            hass,
            _LOGGER,
            name="Envertech Solar Data Coordinator",
            update_interval=timedelta(seconds=60),
        )
        self.station_id = station_id

    async def _async_update_data(self):
        return await fetch_data(self.station_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    station_id = entry.data["station_id"]
    coordinator = EnvertechDataUpdateCoordinator(hass, station_id)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    sensors = [
        ("UnitCapacity", "Capacity", None, "mdi:solar-power"),
        ("Power", "Current Power", "W", "mdi:solar-power"),
        ("UnitEToday", "Daily Energy", "kWh", "mdi:solar-power"),
        ("UnitEMonth", "Monthly Energy", "kWh", "mdi:solar-power"),
        ("UnitEYear", "Yearly Energy", "kWh", "mdi:solar-power"),
        ("UnitETotal", "Total Energy", "kWh", "mdi:solar-power"),
        ("StrPeakPower", "Peak Power", None, "mdi:flash"),
        ("InvModel1", "Inverter Model", None, "mdi:solar-power"),
    ]

    entities = [
        EnvertechSensor(coordinator, station_id, key, name, unit, icon)
        for key, name, unit, icon in sensors
    ]

    async_add_entities(entities)


class EnvertechSensor(SensorEntity):
    def __init__(self, coordinator, station_id, sensor_key, name, unit, icon=None):
        self.coordinator = coordinator
        self.station_id = station_id
        self.sensor_key = sensor_key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon

        if unit == "kWh":
            self._attr_device_class = "energy"
            self._attr_state_class = "total_increasing"
        elif unit == "W":
            self._attr_device_class = "power"
            self._attr_state_class = "measurement"
        else:
            self._attr_device_class = None
            self._attr_state_class = None

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.sensor_key}_{self.station_id}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.station_id)},
            name="Envertech Solar Station",
            manufacturer=MANUFACTURER,
            model="Envertech API",
            entry_type="service",
            configuration_url="https://github.com/jimmybonesde/envertech_solar"
        )

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data or "Data" not in data:
            return None

        val = data["Data"].get(self.sensor_key)
        if val is None:
            return None

        # Direkt zurückgeben, keine Konvertierung, für diese Keys:
        if self.sensor_key in ("UnitCapacity", "StrPeakPower", "InvModel1"):
            return val

        if isinstance(val, str):
            try:
                cleaned = val.replace(",", ".").replace("kWh", "").replace("W", "").replace("kW", "").strip()
                number = float(cleaned)
                if "kW" in val and self._attr_native_unit_of_measurement == "W":
                    number *= 1000
                return number
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
