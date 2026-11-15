"""Power, energy and temperature sensors for D-Link DSP-W215."""
from homeassistant.components.sensor import (
    RestoreSensor, SensorDeviceClass, SensorEntity, SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, UnitOfPower, UnitOfTemperature
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util


async def async_setup_entry(hass, entry, async_add_entities):
    c = entry.runtime_data
    async_add_entities([PowerSensor(c), TemperatureSensor(c), EnergySensor(c)])


class _Base(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, coord, key, name):
        super().__init__(coord)
        self._attr_unique_id = f"dlink_w215_{coord.host}_{key}"
        self._attr_name = name
        self._attr_device_info = coord.device_info


class PowerSensor(_Base, SensorEntity):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(self, c):
        super().__init__(c, "power", "Power")

    @property
    def native_value(self):
        return self.coordinator.data.get("power")


class TemperatureSensor(_Base, SensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_entity_registry_enabled_default = False  # internal plug temperature

    def __init__(self, c):
        super().__init__(c, "temperature", "Temperature")

    @property
    def native_value(self):
        return self.coordinator.data.get("temperature")


class EnergySensor(_Base, RestoreSensor):
    """kWh total, integrated from power readings (the plug keeps no readable total)."""
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 3
    MAX_GAP = 300  # seconds; skip integration across longer outages

    def __init__(self, c):
        super().__init__(c, "energy", "Energy")
        self._total = 0.0
        self._last = None  # (time, watts)

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last = await self.async_get_last_sensor_data()
        if last and last.native_value is not None:
            try:
                self._total = float(last.native_value)
            except (TypeError, ValueError):
                pass
        self._handle_coordinator_update()

    @callback
    def _handle_coordinator_update(self):
        watts = self.coordinator.data.get("power") if self.coordinator.last_update_success else None
        now = dt_util.utcnow()
        if watts is not None:
            if self._last:
                dt = (now - self._last[0]).total_seconds()
                if 0 < dt <= self.MAX_GAP:
                    self._total += (self._last[1] + watts) / 2 * dt / 3_600_000
            self._last = (now, watts)
        else:
            self._last = None
        super()._handle_coordinator_update()

    @property
    def native_value(self):
        return round(self._total, 5)
