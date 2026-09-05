import logging
import re
from datetime import datetime, timedelta

import aiohttp
import async_timeout

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

API_URL = "https://www.envertecportal.com/ApiStations/getStationInfo"
MANUFACTURER = "JimmyBones"

# Order matters: longer units must be checked before their shorter variants.
UNITS = (
    ("MWh", 1000),
    ("kWh", 1),
    ("kKh", 1),  # Envertech API typo; treat as kWh
    ("kW", 1000),
    ("W", 1),
    ("EUR", 1),
    ("PLN", 1),
    ("€", 1),
    ("zł", 1),
    ("ton", 1),
)


def parse_numeric_value(value) -> float:
    """Convert Envertech API values with units into numeric values."""
    cleaned = str(value).replace("\xa0", " ").strip()
    factor = 1

    for unit, unit_factor in UNITS:
        if unit.casefold() in cleaned.casefold():
            cleaned = re.sub(re.escape(unit), "", cleaned, flags=re.IGNORECASE).strip()
            factor = unit_factor
            break

    # Supports:
    # 2,223.20 -> 2223.20
    # 2.223,20 -> 2223.20
    # 17,46     -> 17.46
    # 17.46     -> 17.46
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")

    return float(cleaned) * factor


async def fetch_data(session: aiohttp.ClientSession, station_id: str):
    """Fetch current data from the Envertech API."""
    params = {"stationID": station_id}

    async with async_timeout.timeout(10):
        async with session.post(API_URL, params=params) as response:
            response.raise_for_status()
            return await response.json()


class EnvertechDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinate Envertech Solar data updates."""

    def __init__(self, hass: HomeAssistant, station_id: str, update_interval: int = 30):
        super().__init__(
            hass,
            _LOGGER,
            name="Envertech Solar Data Coordinator",
            update_interval=timedelta(seconds=update_interval),
        )
        self.station_id = station_id
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self):
        try:
            return await fetch_data(self._session, self.station_id)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Error fetching Envertech data: {err}") from err


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up Envertech Solar sensors from a config entry."""
    station_id = entry.data["station_id"]
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        ("UnitCapacity", "Capacity", None, "mdi:solar-power"),
        ("Power", "Current Power", "W", "mdi:solar-power"),
        ("UnitEToday", "Daily Energy", "kWh", "mdi:solar-power"),
        ("UnitEMonth", "Monthly Energy", "kWh", "mdi:solar-power"),
        ("UnitEYear", "Yearly Energy", "kWh", "mdi:solar-power"),
        ("UnitETotal", "Total Energy", "kWh", "mdi:solar-power"),
        ("InvModel1", "Inverter Model", None, "mdi:solar-power"),
        ("StrPeakPower", "All-Time Peak Power", None, "mdi:flash"),
        ("StrIncome", "Income", "EUR", "mdi:cash"),
        ("StrCO2", "Carbon Offset", "ton", "mdi:molecule-co2"),
        ("CreateTime", "Start Date", None, "mdi:view-day"),
    ]

    entities = [
        EnvertechSensor(coordinator, station_id, key, name, unit, icon)
        for key, name, unit, icon in sensors
    ]
    entities.append(EnvertechPeakTodaySensor(coordinator, station_id))

    async_add_entities(entities)


class EnvertechSensor(CoordinatorEntity, SensorEntity):
    """Representation of a single Envertech sensor."""

    def __init__(self, coordinator, station_id, sensor_key, name, unit, icon=None):
        super().__init__(coordinator)

        self.station_id = station_id
        self.sensor_key = sensor_key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon

        if unit == "kWh":
            self._attr_device_class = SensorDeviceClass.ENERGY
            # Month/year totals reset periodically — TOTAL_INCREASING would warn.
            if sensor_key in ("UnitEMonth", "UnitEYear"):
                self._attr_state_class = SensorStateClass.MEASUREMENT
            else:
                self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        elif unit == "W":
            self._attr_device_class = SensorDeviceClass.POWER
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif sensor_key == "StrIncome":
            self._attr_device_class = SensorDeviceClass.MONETARY

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
    def native_unit_of_measurement(self):
        """Return the detected ISO 4217 currency for the income sensor."""
        if self.sensor_key != "StrIncome":
            return self._attr_native_unit_of_measurement

        data = self.coordinator.data or {}
        value = str(data.get("Data", {}).get("StrIncome", "")).casefold()

        if "zł" in value or "pln" in value:
            return "PLN"

        return "EUR"

    @property
    def native_value(self):
        """Return the current native sensor value."""
        data = self.coordinator.data
        if not data or "Data" not in data:
            return None

        value = data["Data"].get(self.sensor_key)
        if value is None:
            return None

        if self.sensor_key == "CreateTime":
            try:
                return value.split("GMT")[0].strip()
            except (AttributeError, TypeError) as err:
                _LOGGER.warning("Could not parse CreateTime '%s': %s", value, err)
                return None

        if self.sensor_key in ("UnitCapacity", "StrPeakPower", "InvModel1"):
            return value

        try:
            return parse_numeric_value(value)
        except (TypeError, ValueError) as err:
            _LOGGER.warning(
                "Could not convert value '%s' for sensor '%s': %s",
                value,
                self.sensor_key,
                err,
            )
            return None


class EnvertechPeakTodaySensor(CoordinatorEntity, RestoreEntity, SensorEntity):
    """Calculate and persist the daily peak power."""

    def __init__(self, coordinator, station_id):
        super().__init__(coordinator)

        self.station_id = station_id
        self._attr_name = "Daily Peak Power"
        self._attr_native_unit_of_measurement = "W"
        self._attr_icon = "mdi:flash"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT

        self._peak_today = 0.0
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
        return {
            "peak_time": self._peak_time.strftime("%H:%M:%S")
            if self._peak_time
            else None,
            "last_reset": self._last_reset_date.isoformat()
            if self._last_reset_date
            else None,
        }

    def _update_peak_from_coordinator(self):
        """Update the daily peak value from coordinator data."""
        data = self.coordinator.data
        if not data or "Data" not in data:
            return

        power_value = data["Data"].get("Power")
        if power_value is None:
            return

        try:
            power = parse_numeric_value(power_value)
        except (TypeError, ValueError):
            return

        today = dt_util.now().date()

        if self._last_reset_date != today:
            self._peak_today = 0.0
            self._peak_time = None
            self._last_reset_date = today

        if power > self._peak_today:
            self._peak_today = power
            self._peak_time = dt_util.now()

    def _handle_coordinator_update(self):
        """Handle coordinator updates before writing the new state."""
        self._update_peak_from_coordinator()
        super()._handle_coordinator_update()

    async def async_added_to_hass(self):
        """Restore peak data after Home Assistant restarts."""
        last_state = await self.async_get_last_state()

        if last_state and last_state.state not in ("unknown", "unavailable"):
            try:
                self._peak_today = float(last_state.state)
            except (TypeError, ValueError):
                self._peak_today = 0.0

            peak_time = last_state.attributes.get("peak_time")
            if peak_time:
                try:
                    self._peak_time = datetime.strptime(peak_time, "%H:%M:%S")
                except ValueError:
                    self._peak_time = None

            last_reset = last_state.attributes.get("last_reset")
            if last_reset:
                try:
                    self._last_reset_date = datetime.fromisoformat(last_reset).date()
                except ValueError:
                    self._last_reset_date = None

        await super().async_added_to_hass()
        self._update_peak_from_coordinator()
