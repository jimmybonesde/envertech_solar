import logging
from datetime import timedelta, datetime
import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
API_URL = "https://www.envertecportal.com/ApiStations/getStationInfo"
MANUFACTURER = "JimmyBones"


async def fetch_data(station_id):
    """Ruft die aktuellen Daten von der Envertech API ab."""
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
    """Coordinator für Envertech-Solar-Daten."""

    def __init__(self, hass: HomeAssistant, station_id: str, update_interval: int = 30):
        super().__init__(
            hass,
            _LOGGER,
            name="Envertech Solar Data Coordinator",
            update_interval=timedelta(seconds=update_interval),
        )
        self.station_id = station_id

    async def _async_update_data(self):
        return await fetch_data(self.station_id)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Setzt die Sensoren über einen ConfigEntry auf."""
    station_id = entry.data["station_id"]
    update_interval = entry.options.get("update_interval", 30)

    coordinator = EnvertechDataUpdateCoordinator(hass, station_id, update_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    sensors = [
        ("UnitCapacity", "Capacity", None, "mdi:solar-power"),
        ("Power", "Current Power", "W", "mdi:solar-power"),
        ("UnitEToday", "Daily Energy", "kWh", "mdi:solar-power"),
        ("UnitEMonth", "Monthly Energy", "kWh", "mdi:solar-power"),
        ("UnitEYear", "Yearly Energy", "kWh", "mdi:solar-power"),
        ("UnitETotal", "Total Energy", "kWh", "mdi:solar-power"),
        ("InvModel1", "Inverter Model", None, "mdi:solar-power"),
        ("StrPeakPower", "All-Time Peak Power", None, "mdi:flash"),
        ("StrIncome", "Income", "€", "mdi:cash"),
        ("StrCO2", "Carbon Offset", "ton", "mdi:molecule-co2"),
        ("CreateTime", "Start Date", None, "mdi:view-day"),
    ]

    entities = [
        EnvertechSensor(coordinator, station_id, key, name, unit, icon)
        for key, name, unit, icon in sensors
    ]

    # Peak-Power-Sensor hinzufügen
    entities.append(EnvertechPeakTodaySensor(coordinator, station_id))

    async_add_entities(entities)


class EnvertechSensor(SensorEntity):
    """Einzelner Envertech-Sensor."""

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

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.sensor_key.lower()}_{self.station_id}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.station_id)},
            name="Envertech Solar Station",
            manufacturer=MANUFACTURER,
            model="Envertech API",
            entry_type="service",
            configuration_url="https://github.com/jimmybonesde/envertech_solar",
        )

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data or "Data" not in data:
            return None

        val = data["Data"].get(self.sensor_key)
        if val is None:
            return None

        # Spezieller Fall: CreateTime als dd/mm/yyyy
        if self.sensor_key == "CreateTime":
            try:
                return val.split("GMT")[0].strip()
            except Exception as e:
                _LOGGER.warning("Could not parse CreateTime '%s': %s", val, e)
                return val

        # Sensoren, die String bleiben sollen
        if self.sensor_key in ("UnitCapacity", "StrPeakPower", "InvModel1"):
            return val

        # Alle anderen als Float
        try:
            cleaned = str(val).replace(",", ".").strip()

            units = {"MWh": 1000, "kWh": 1, "kW": 1000, "W": 1, "€": 1, "ton": 1}
            for unit, factor in units.items():
                if unit in cleaned:
                    number = float(cleaned.replace(unit, "").strip()) * factor
                    break
            else:
                number = float(cleaned)

            if self._attr_native_unit_of_measurement == "W" and self.sensor_key in ("UnitETotal", "UnitEYear"):
                number *= 1000

            return number
        except Exception as e:
            _LOGGER.warning(
                "Could not convert value '%s' for sensor '%s': %s", val, self.sensor_key, e
            )
            return val

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


class EnvertechPeakTodaySensor(RestoreEntity, SensorEntity):
    """Berechnet die Tages-Peak-Leistung und speichert sie persistent."""

    def __init__(self, coordinator, station_id):
        self.coordinator = coordinator
        self.station_id = station_id
        self._attr_name = "Daily Peak Power"
        self._attr_native_unit_of_measurement = "W"
        self._attr_icon = "mdi:flash"
        self._attr_device_class = "power"
        self._attr_state_class = "measurement"

        self._peak_today = 0
        self._peak_time = None
        self._last_reset_date = None

    @property
    def unique_id(self):
        return f"{DOMAIN}_peak_power_today_{self.station_id}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.station_id)},
            name="Envertech Solar Station",
            manufacturer=MANUFACTURER,
            model="Envertech API",
            entry_type="service",
            configuration_url="https://github.com/jimmybonesde/envertech_solar",
        )

    @property
    def native_value(self):
        return self._peak_today

    @property
    def extra_state_attributes(self):
        if self._peak_time:
            return {
                "peak_time": self._peak_time.strftime("%H:%M:%S"),
                "last_reset": self._last_reset_date.isoformat() if self._last_reset_date else None,
            }
        return {"peak_time": None, "last_reset": None}

    async def async_update(self):
        await self.coordinator.async_request_refresh()
        data = self.coordinator.data
        if not data or "Data" not in data:
            return

        val = data["Data"].get("Power")
        if val is None:
            return

        try:
            cleaned = str(val).replace(",", ".").replace("W", "").replace("kW", "").strip()
            number = float(cleaned)
            if "kW" in str(val):
                number *= 1000
        except Exception:
            return

        today = datetime.now().date()
        if self._last_reset_date != today:
            self._peak_today = 0
            self._peak_time = None
            self._last_reset_date = today

        if number > self._peak_today:
            self._peak_today = number
            self._peak_time = datetime.now()

    async def async_added_to_hass(self):
        """Restore last state on HA startup."""
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in (None, "unknown", "unavailable"):
            try:
                self._peak_today = float(last_state.state)
            except ValueError:
                self._peak_today = 0

            peak_time_attr = last_state.attributes.get("peak_time")
            if peak_time_attr:
                try:
                    self._peak_time = datetime.strptime(peak_time_attr, "%H:%M:%S")
                except Exception:
                    self._peak_time = None

            last_reset_attr = last_state.attributes.get("last_reset")
            if last_reset_attr:
                try:
                    self._last_reset_date = datetime.fromisoformat(last_reset_attr).date()
                except Exception:
                    self._last_reset_date = None

        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
