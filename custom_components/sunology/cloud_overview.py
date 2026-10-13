"""DataUpdateCoordinator for the Sunology cloud /api/overview endpoint."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .cloud import SunologyCloud, SunologyCloudError
from .const import PACKAGE_NAME

_LOGGER = logging.getLogger(PACKAGE_NAME)


class SunologyOverviewCoordinator(DataUpdateCoordinator):
    """Polls /api/overview every 30 seconds."""

    def __init__(self, hass: HomeAssistant, cloud: SunologyCloud) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Sunology Cloud Overview",
            update_interval=timedelta(seconds=30),
        )
        self._cloud = cloud

    async def _async_update_data(self) -> dict:
        """Fetch /api/overview from the cloud."""
        try:
            return await self._cloud.get_overview()
        except SunologyCloudError as err:
            raise UpdateFailed(f"Overview fetch failed: {err}") from err
