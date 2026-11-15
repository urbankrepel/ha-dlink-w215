"""D-Link DSP-W215 (firmware 2.2x) integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant

DOMAIN = "dlink_w215"
PLATFORMS = [Platform.SWITCH, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    from .coordinator import W215Coordinator
    from .hnap import W215

    d = entry.data
    dev = W215(d[CONF_HOST], d[CONF_PASSWORD], d.get(CONF_USERNAME, "admin"))
    coord = W215Coordinator(hass, dev, d[CONF_HOST], d.get(CONF_NAME, entry.title))
    await coord.async_config_entry_first_refresh()
    entry.runtime_data = coord
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
