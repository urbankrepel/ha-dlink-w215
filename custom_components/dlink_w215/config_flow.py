"""UI setup for D-Link DSP-W215."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME

from . import DOMAIN
from .hnap import W215

_LOGGER = logging.getLogger(__name__)

SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Optional(CONF_NAME, default="D-Link Smart Plug"): str,
    vol.Optional(CONF_USERNAME, default="admin"): str,
})


class W215ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()
            dev = W215(user_input[CONF_HOST], user_input[CONF_PASSWORD], user_input[CONF_USERNAME])
            try:
                await self.hass.async_add_executor_job(dev.is_on)
            except PermissionError:
                errors["base"] = "invalid_auth"
            except Exception as err:
                _LOGGER.warning("Can't connect to %s: %s", user_input[CONF_HOST], err)
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(SCHEMA, user_input or {}),
            errors=errors,
        )

    async def async_step_import(self, import_data):
        """Turn an existing YAML entry into a UI entry."""
        await self.async_set_unique_id(import_data[CONF_HOST])
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=import_data.get(CONF_NAME, "D-Link Smart Plug"), data=import_data)
