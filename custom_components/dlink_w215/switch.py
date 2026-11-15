"""Switch platform for D-Link DSP-W215 on firmware 2.2x."""
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv

from .hnap import W215

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=15)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_USERNAME, default="admin"): cv.string,
    vol.Optional(CONF_NAME, default="D-Link Smart Plug"): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    dev = W215(config[CONF_HOST], config[CONF_PASSWORD], config[CONF_USERNAME])
    add_entities([W215Switch(dev, config[CONF_NAME], config[CONF_HOST])], True)


class W215Switch(SwitchEntity):
    def __init__(self, dev: W215, name: str, host: str):
        self._dev = dev
        self._attr_name = name
        self._attr_unique_id = f"dlink_w215_{host}"
        self._attr_is_on = None
        self._attr_available = False
        self._attr_extra_state_attributes = {}

    def turn_on(self, **kwargs):
        self._dev.set_state(True)
        self._attr_is_on = True

    def turn_off(self, **kwargs):
        self._dev.set_state(False)
        self._attr_is_on = False

    def update(self):
        try:
            self._attr_is_on = self._dev.is_on()
            attrs = {}
            for key, fn in (("current_power_w", self._dev.power),
                            ("temperature_c", self._dev.temperature)):
                try:
                    attrs[key] = fn()
                except Exception:  # optional readings
                    pass
            self._attr_extra_state_attributes = attrs
            self._attr_available = True
        except Exception as err:
            _LOGGER.warning("W215 update failed: %s", err)
            self._attr_available = False
