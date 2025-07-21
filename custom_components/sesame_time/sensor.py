"""Sensor platform for Sesame Time integration."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    STATE_CHECKED_IN,
    STATE_CHECKED_OUT,
    ATTR_LAST_CHECK_IN,
    ATTR_LAST_CHECK_OUT,
    ATTR_EMPLOYEE_NAME,
    ATTR_COMPANY_NAME,
    ATTR_WORK_STATUS,
    CONF_EMPLOYEE_ID,
    CONF_EMPLOYEE_NAME,
    CONF_COMPANY_NAME,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sesame Time sensor entities."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api = data["api"]
    entry_data = data["entry_data"]
    
    entities = [
        SesameTimeStatusSensor(
            api=api,
            entry_data=entry_data,
            entry_id=config_entry.entry_id,
        )
    ]
    
    async_add_entities(entities)


class SesameTimeStatusSensor(SensorEntity):
    """Sesame Time status sensor."""

    def __init__(self, api, entry_data, entry_id):
        """Initialize the sensor."""
        self._api = api
        self._entry_data = entry_data
        self._entry_id = entry_id
        self._state = None
        self._attributes = {}
        
        # Entity attributes
        employee_name = entry_data[CONF_EMPLOYEE_NAME]
        company_name = entry_data[CONF_COMPANY_NAME]
        employee_id = entry_data[CONF_EMPLOYEE_ID]
        
        self._attr_name = f"{employee_name} Status"
        self._attr_unique_id = f"{employee_id}_status"
        
        _LOGGER.info(f"Creating sensor - Name: {self._attr_name}, Unique ID: {self._attr_unique_id}")
        self._attr_icon = "mdi:account-clock"
        
        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, employee_id)},
            name=f"{employee_name} ({company_name})",
            manufacturer="Sesame Time",
            model="Employee",
            sw_version="1.0",
        )
    
    @property
    def state(self) -> Optional[str]:
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return self._attributes
    
    async def async_update(self) -> None:
        """Update the sensor."""
        try:
            result = await self._api.get_status()
            
            if result.get("success"):
                # Update state
                if result.get("is_checked_in"):
                    self._state = STATE_CHECKED_IN
                else:
                    self._state = STATE_CHECKED_OUT
                
                # Update attributes
                self._attributes = {
                    ATTR_LAST_CHECK_IN: result.get("last_check_in"),
                    ATTR_LAST_CHECK_OUT: result.get("last_check_out"),
                    ATTR_EMPLOYEE_NAME: self._entry_data[CONF_EMPLOYEE_NAME],
                    ATTR_COMPANY_NAME: self._entry_data[CONF_COMPANY_NAME],
                    ATTR_WORK_STATUS: result.get("work_status"),
                }
            else:
                _LOGGER.error(f"Failed to update status: {result.get('error')}")
                
        except Exception as err:
            _LOGGER.error(f"Error updating sensor: {err}")