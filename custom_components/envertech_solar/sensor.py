"""Envertech Solar sensor platform."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Mapping
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.components.sensor import SensorEntity
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
MANUFACTURER = "Envertech"
DEFAULT_UPDATE_INTERVAL = 30


async def fetch_data(hass: HomeAssistant, station_id: str) -> Mapping[str, Any]:
    """Fetch the current data from the Envertech API."""
    session = async_get_clientsession(hass)

    async with session.post(
        API_URL,
        params={"stationID": station_id},
        timeout=aiohttp.ClientTimeout(total=10),
    ) as response:
        response.raise_for_status()
        data = await response.json()

    if not isinstance(data, Mapping) or not isinstance(data.get("Data"), Mapping):
        raise ValueError("Envertech API returned an unexpected response")

    return data


class EnvertechDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinate Envertech Solar API updates."""

    def __init__(
        self, hass: HomeAssistant, station_id: str, update_interval: int = DEFAULT_UPDATE_INTERVAL
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Envertech Solar",
            update_interval=timedelta(seconds=update_interval),
        )
        self.station_id = station_id

    async def _async_update_data(self) -> Mapping[str, Any]:
        try:
            return await fetch_data(self.hass, self.station_id)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Error communicating with Envertech: {err}") from err


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Envertech sensors from a config entry."""
    coordinator: EnvertechDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    station_id = entry.data["station_id"]

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
    entities.append(EnvertechPeakTodaySensor(coordinator, station_id))
    async_add_entities(entities)


class EnvertechEntity(CoordinatorEntity):
    """Base entity for an Envertech station."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: EnvertechDataUpdateCoordinator, station_id: str) -> None:
        super().__init__(coordinator)
        self.station_id = station_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.station_id)},
            name="Envertech Solar Station",
            manufacturer=MANUFACTURER,
            model="Envertech API",
            configuration_url="https://github.com/jimmybonesde/envertech_solar",
        )


class EnvertechSensor(EnvertechEntity, SensorEntity):
    """Represent a single Envertech sensor."""

    def __init__(
        self,
        coordinator: EnvertechDataUpdateCoordinator,
        station_id: str,
        sensor_key: str,
        name: str,
        unit: str | None,
        icon: str | None = None,
    ) -> None:
        super().__init__(coordinator, station_id)
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
    def unique_id(self) -> str:
        """Return a unique ID for the sensor."""
        return f"{DOMAIN}_{self.sensor_key.lower()}_{self.station_id}"

    @property
    def native_value(self) -> Any:
        """Return the latest value reported by the API."""
        data = self.coordinator.data
        if not data:
            return None

        value = data["Data"].get(self.sensor_key)
        if value is None:
            return None

        if self.sensor_key == "CreateTime":
            return str(value).split("GMT", maxsplit=1)[0].strip()

        if self.sensor_key in ("UnitCapacity", "StrPeakPower", "InvModel1"):
            return value

        return _parse_number(value, self.sensor_key)


class EnvertechPeakTodaySensor(EnvertechEntity, RestoreEntity, SensorEntity):
    """Track and persist the highest power reported during the current day."""

    _attr_name = "Daily Peak Power"
    _attr_native_unit_of_measurement = "W"
    _attr_icon = "mdi:flash"
    _attr_device_class = "power"
    _attr_state_class = "measurement"

    def __init__(
        self, coordinator: EnvertechDataUpdateCoordinator, station_id: str
    ) -> None:
        super().__init__(coordinator, station_id)
        self._peak_today = 0.0
        self._peak_time = None
        self._last_reset_date = None

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the daily peak sensor."""
        return f"{DOMAIN}_peak_power_today_{self.station_id}"

    @property
    def native_value(self) -> float:
        """Return the daily peak power."""
        return self._peak_today

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        """Return information about the recorded peak."""
        return {
            "peak_time": self._peak_time.isoformat() if self._peak_time else None,
            "last_reset": (
                self._last_reset_date.isoformat() if self._last_reset_date else None
            ),
        }

    async def async_added_to_hass(self) -> None:
        """Restore the last peak and include the initial coordinator data."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in ("unknown", "unavailable"):
            try:
                self._peak_today = float(last_state.state)
            except ValueError:
                pass

            peak_time = last_state.attributes.get("peak_time")
            if peak_time:
                try:
                    self._peak_time = dt_util.parse_datetime(peak_time)
                except (TypeError, ValueError):
                    pass

            last_reset = last_state.attributes.get("last_reset")
            if last_reset:
                try:
                    self._last_reset_date = dt_util.parse_date(last_reset)
                except (TypeError, ValueError):
                    pass

        self._update_peak()
        self.async_write_ha_state()

    def _handle_coordinator_update(self) -> None:
        """Update the peak before publishing coordinator data."""
        self._update_peak()
        super()._handle_coordinator_update()

    def _update_peak(self) -> None:
        """Update or reset the peak using the current coordinator data."""
        data = self.coordinator.data
        if not data:
            return

        power = data["Data"].get("Power")
        if power is None:
            return

        number = _parse_number(power, "Power")
        if not isinstance(number, (int, float)):
            return

        now = dt_util.now()
        if self._last_reset_date != now.date():
            self._peak_today = 0.0
            self._peak_time = None
            self._last_reset_date = now.date()

        if number > self._peak_today:
            self._peak_today = number
            self._peak_time = now


def _parse_number(value: Any, sensor_key: str) -> float | str:
    """Convert an API value with optional unit text to a numeric value."""
    cleaned = str(value).replace(",", ".").strip()
    for unit, factor in (("MWh", 1000), ("kWh", 1), ("kW", 1000), ("W", 1), ("€", 1), ("ton", 1)):
        if cleaned.endswith(unit):
            cleaned = cleaned.removesuffix(unit).strip()
            try:
                return float(cleaned) * factor
            except ValueError:
                break

    try:
        return float(cleaned)
    except ValueError:
        _LOGGER.warning("Could not convert value '%s' for sensor '%s'", value, sensor_key)
        return value
