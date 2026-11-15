"""Switch for D-Link DSP-W215 on firmware 2.2x."""
import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_USERNAME, default="admin"): cv.string,
    vol.Optional(CONF_NAME, default="D-Link Smart Plug"): cv.string,
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old YAML config: import it into a UI entry."""
    hass.async_create_task(hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "import"},
        data={k: config[k] for k in (CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_NAME)}))


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([W215Switch(entry.runtime_data)])


class W215Switch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = None  # use the device name

    def __init__(self, coord):
        super().__init__(coord)
        self._attr_unique_id = f"dlink_w215_{coord.host}"
        self._attr_device_info = coord.device_info

    @property
    def is_on(self):
        return self.coordinator.data["is_on"]

    async def _set(self, on: bool):
        await self.hass.async_add_executor_job(self.coordinator.dev.set_state, on)
        self.coordinator.data["is_on"] = on
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs):
        await self._set(True)

    async def async_turn_off(self, **kwargs):
        await self._set(False)
