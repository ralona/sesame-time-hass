"""Button platform for Sesame Time integration."""
import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
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
    """Set up Sesame Time button entities."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api = data["api"]
    entry_data = data["entry_data"]
    
    entities = [
        SesameTimeCheckButton(
            api=api,
            entry_data=entry_data,
            entry_id=config_entry.entry_id,
        )
    ]
    
    async_add_entities(entities)


class SesameTimeCheckButton(ButtonEntity):
    """Sesame Time check in/out button."""

    def __init__(self, api, entry_data, entry_id):
        """Initialize the button."""
        self._api = api
        self._entry_data = entry_data
        self._entry_id = entry_id
        
        # Entity attributes
        employee_name = entry_data[CONF_EMPLOYEE_NAME]
        company_name = entry_data[CONF_COMPANY_NAME]
        employee_id = entry_data[CONF_EMPLOYEE_ID]
        
        self._attr_name = f"{employee_name} Check In/Out"
        self._attr_unique_id = f"{employee_id}_check"
        self._attr_icon = "mdi:account-clock-outline"
        
        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, employee_id)},
            name=f"{employee_name} ({company_name})",
            manufacturer="Sesame Time",
            model="Employee",
            sw_version="1.0",
        )
    
    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            # Get current status
            status_result = await self._api.get_status()
            
            if not status_result.get("success"):
                raise HomeAssistantError(f"Failed to get status: {status_result.get('error')}")
            
            # Decide action based on current status
            if status_result.get("is_checked_in"):
                # Currently checked in, so check out
                result = await self._api.check_out()
                action = "check-out"
            else:
                # Currently checked out, so check in
                result = await self._api.check_in()
                action = "check-in"
            
            if result.get("success"):
                _LOGGER.info(f"Successfully performed {action} for {self._entry_data[CONF_EMPLOYEE_NAME]}")
                
                # Update the sensor
                await self.hass.async_add_executor_job(
                    self.hass.services.async_call,
                    "homeassistant",
                    "update_entity",
                    {"entity_id": f"sensor.{self._entry_data[CONF_EMPLOYEE_NAME].lower().replace(' ', '_')}_status"}
                )
            else:
                raise HomeAssistantError(f"Failed to {action}: {result.get('error')}")
                
        except Exception as err:
            _LOGGER.error(f"Error performing check action: {err}")
            raise HomeAssistantError(f"Error: {err}")