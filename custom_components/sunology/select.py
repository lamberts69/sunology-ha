""" select for Sunology objects """

import logging
from typing import Any

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.select import SelectEntity, ENTITY_ID_FORMAT


from .const import (
    FlowWorkingModes,
    PACKAGE_NAME,
    DOMAIN as SUNOLOGY_DOMAIN,
    StoreyPilotMode,
    CLOUD_PARAM_TO_PILOT_MODE,
)
from .device import (
    SunologyAbstractDevice,
    Gateway,
    StoreyMaster,
)

_LOGGER = logging.getLogger(PACKAGE_NAME) 


def _format_devid_mac(mac: str):
    """Format a MAC address to a format that can be used as a device ID."""
    to_test = mac
    if len(to_test) == 12:
        # no : included
        return "_".join(to_test.lower()[i : i + 2] for i in range(0, 12, 2))
    if '#' in to_test:
        return to_test.replace('#', '_')
    return mac


async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up Sunology device based off an entry."""
    sunology_context = config_entry.runtime_data
    coordinated_devices = sunology_context.sunology_devices_coordinated

    known_devices_ids: set[str] = set()

    def _check_device() -> None:
        current_devices_ids = set(coordinated_device['device'].device_id for coordinated_device in coordinated_devices)
        new_devices_ids = current_devices_ids - known_devices_ids
        if new_devices_ids:
            known_devices_ids.update(new_devices_ids)
            entities = []
            for coordinated_device_id in new_devices_ids:
                coordinated_device = next((coordinated_device for coordinated_device in coordinated_devices if coordinated_device['device'].device_id == coordinated_device_id), None)
                device = coordinated_device['device']
                coordinator = coordinated_device['coordinator']
                new_entities = []
                if isinstance(device, Gateway):
                    new_entities.append(SunologFlowWorkingModeSelectEntity(device, hass))
                if isinstance(device, StoreyMaster):
                    new_entities.append(
                        SunologyStoreyPilotModeSelectEntity(device, hass, sunology_context.cloud)
                    )
                if not 'device_entities' in coordinated_device: 
                    coordinated_device['device_entities'] = []
                coordinated_device['device_entities'].extend(new_entities)
                entities.extend(new_entities)
            async_add_entities(entities)
    _check_device()
    return True

class SunologFlowWorkingModeSelectEntity(SelectEntity):
    """Represent a pvpower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologPvPowerSensor entity."""
        
        self._device = device
        self._name = device.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"flowWorkingMode")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
        self._attr_device_info = device.device_info # For automatic device registration
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def hass(self):
        return self._hass

    @hass.setter
    def hass(self, hass):
        pass

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"flowWorkingMode_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def current_option(self):
        """state property"""
        return self.state

    @property
    def state(self):
        """state property"""
        self._state = self._device.flow_working_mode
        return self._state

    @property
    def options(self):
        """options list property"""
        return [e.name for e in FlowWorkingModes]
    

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._state = self._device.flow_working_mode = option
        await self._device._set_flowWorkingMode(option)

    @property
    def name(self):
        """ pvP name """
        return f"{self._name} flow working mode"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:finance"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info

class SunologyStoreyPilotModeSelectEntity(SelectEntity):
    """Battery pilot mode (Manuel / Suncast / Expert) exposed as a SelectEntity.

    Replays the two-request sequence captured from the Sunology mobile app:
      PUT  /api/client               (updates cloudScheduleParameter)
      PATCH /api/storage-battery/... (updates workingMode, clears any pause)
    """

    def __init__(self, device: StoreyMaster, hass, cloud):
        """Set up pilot mode select entity for a STOREY master."""
        self._device = device
        self._name = device.name
        self._cloud = cloud
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f'pilotMode')}_{_format_devid_mac(device.device_id)}".lower()  # pylint: disable=C0301
        self._attr_device_info = device.device_info
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def hass(self):
        return self._hass

    @hass.setter
    def hass(self, hass):
        pass

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"pilotMode_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def current_option(self):
        """Return the current pilot mode (reads device state)."""
        return self._device.pilot_mode

    @property
    def options(self):
        """List the possible pilot modes."""
        return [e.value for e in StoreyPilotMode]

    async def async_added_to_hass(self):
        """Fetch the initial pilot mode once the entity is added to HA."""
        await super().async_added_to_hass()
        if self._cloud is None or self._device.pilot_mode is not None:
            return
        try:
            client = await self._cloud.get_client()
            param = client.get("cloudScheduleParameter")
            self._device.pilot_mode = CLOUD_PARAM_TO_PILOT_MODE.get(param)
            self.async_write_ha_state()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Failed to fetch initial pilot mode from /api/client")

    async def async_select_option(self, option: str) -> None:
        """Change the pilot mode via the cloud (2-request sequence)."""
        if self._cloud is None:
            _LOGGER.error("Cannot set pilot mode: Sunology cloud not configured")
            return
        try:
            await self._device.async_set_pilot_mode(self._cloud, option)
            self.async_write_ha_state()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Failed to set pilot mode to %s", option)

    @property
    def name(self):
        """Entity name."""
        return f"{self._name} pilot mode"

    @property
    def icon(self):
        """Icon."""
        return "mdi:battery-settings"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info