"""One poll of the plug, shared by the switch and the sensors."""
from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .hnap import W215

_LOGGER = logging.getLogger(__name__)


class W215Coordinator(DataUpdateCoordinator):
    def __init__(self, hass, dev: W215, host: str, name: str):
        super().__init__(hass, _LOGGER, name=f"D-Link W215 {host}", update_interval=timedelta(seconds=15))
        self.dev, self.host, self.dev_name = dev, host, name

    def _fetch(self):
        data = {"is_on": self.dev.is_on()}
        for key, fn in (("power", self.dev.power), ("temperature", self.dev.temperature)):
            try:
                data[key] = fn()
            except Exception:  # optional readings
                data[key] = None
        return data

    async def _async_update_data(self):
        try:
            return await self.hass.async_add_executor_job(self._fetch)
        except Exception as err:
            raise UpdateFailed(err) from err

    @property
    def device_info(self):
        return {
            "identifiers": {("dlink_w215", self.host)},
            "name": self.dev_name, "manufacturer": "D-Link", "model": "DSP-W215",
            "configuration_url": f"http://{self.host}",
        }
