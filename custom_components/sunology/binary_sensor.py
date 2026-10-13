"""Binary sensor entities for Sunology hub IoT connectivity."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    ENTITY_ID_FORMAT,
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .cloud_overview import SunologyOverviewCoordinator
from .const import DOMAIN as SUNOLOGY_DOMAIN, PACKAGE_NAME
from .sensor import _overview_slug, _overview_device_info

_LOGGER = logging.getLogger(PACKAGE_NAME)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up binary sensor entities for the Sunology integration."""
    sunology_context = config_entry.runtime_data
    overview_coordinator = sunology_context.overview_coordinator

    entities: list[BinarySensorEntity] = []
    if overview_coordinator is not None and overview_coordinator.data:
        for hub in overview_coordinator.data.get("hubData", []):
            serial = hub.get("serialNumber", "")
            if serial:
                entities.append(SunologyHubConnectedBinarySensor(overview_coordinator, serial))
                _LOGGER.info("Added hub connectivity sensor for serial %s", serial)

    if entities:
        async_add_entities(entities)
    return True


class SunologyHubConnectedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for STREAM Connect hub IoT connectivity."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: SunologyOverviewCoordinator, serial: str) -> None:
        super().__init__(coordinator)
        self._serial = serial
        self._attr_unique_id = f"overview_hub_{serial.lower()}_connected"
        self.entity_id = ENTITY_ID_FORMAT.format(
            f"sunology_hub_{_overview_slug(serial)}_connected"
        )
        self._attr_name = f"Sunology Hub {serial} Connected"
        self._attr_device_info = _overview_device_info(
            f"overview_hub_{serial.lower()}",
            f"Sunology Hub {serial}",
            "STREAM Connect",
        )

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        hubs = (self.coordinator.data or {}).get("hubData", [])
        return any(h.get("serialNumber") == self._serial for h in hubs)

    @property
    def is_on(self) -> bool | None:
        hubs = (self.coordinator.data or {}).get("hubData", [])
        for hub in hubs:
            if hub.get("serialNumber") == self._serial:
                return bool(hub.get("iotStatus", False))
        return None
