"""The Sesame Time integration."""
import logging
from typing import Dict, Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .api import SesameTimeAPI
from .const import (
    DOMAIN,
    CONF_REGION,
    CONF_TOKEN,
    CONF_EMPLOYEE_ID,
    CONF_COMPANY_ID,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]

# Service schemas
CHECK_IN_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Optional("latitude"): cv.latitude,
    vol.Optional("longitude"): cv.longitude,
})

CHECK_OUT_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Optional("latitude"): cv.latitude,
    vol.Optional("longitude"): cv.longitude,
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sesame Time from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Create API instance for this employee
    session = async_get_clientsession(hass)
    api = SesameTimeAPI(
        session=session,
        region=entry.data[CONF_REGION],
        token=entry.data[CONF_TOKEN],
        employee_id=entry.data[CONF_EMPLOYEE_ID],
        company_id=entry.data[CONF_COMPANY_ID],
    )
    
    # Store API instance for this entry
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "entry_data": entry.data,
    }
    
    # Register services
    async def async_check_in_service(call: ServiceCall) -> None:
        """Handle check-in service call."""
        entity_id = call.data["entity_id"]
        latitude = call.data.get("latitude")
        longitude = call.data.get("longitude")
        
        # Find the correct API instance based on entity_id
        for entry_id, data in hass.data[DOMAIN].items():
            if entity_id.endswith(data["entry_data"][CONF_EMPLOYEE_ID].replace("-", "_")):
                api = data["api"]
                result = await api.check_in(latitude=latitude, longitude=longitude)
                if result.get("success"):
                    _LOGGER.info(f"Check-in successful for {entity_id}")
                    # Update the sensor
                    await hass.helpers.entity_component.async_update_entity(hass, entity_id.replace("button.", "sensor.").replace("_check", "_status"))
                else:
                    _LOGGER.error(f"Check-in failed for {entity_id}: {result.get('error')}")
                break
    
    async def async_check_out_service(call: ServiceCall) -> None:
        """Handle check-out service call."""
        entity_id = call.data["entity_id"]
        latitude = call.data.get("latitude")
        longitude = call.data.get("longitude")
        
        # Find the correct API instance based on entity_id
        for entry_id, data in hass.data[DOMAIN].items():
            if entity_id.endswith(data["entry_data"][CONF_EMPLOYEE_ID].replace("-", "_")):
                api = data["api"]
                result = await api.check_out(latitude=latitude, longitude=longitude)
                if result.get("success"):
                    _LOGGER.info(f"Check-out successful for {entity_id}")
                    # Update the sensor
                    await hass.helpers.entity_component.async_update_entity(hass, entity_id.replace("button.", "sensor.").replace("_check", "_status"))
                else:
                    _LOGGER.error(f"Check-out failed for {entity_id}: {result.get('error')}")
                break
    
    # Register services (only once)
    if not hass.services.has_service(DOMAIN, "check_in"):
        hass.services.async_register(
            DOMAIN,
            "check_in",
            async_check_in_service,
            schema=CHECK_IN_SCHEMA,
        )
    
    if not hass.services.has_service(DOMAIN, "check_out"):
        hass.services.async_register(
            DOMAIN,
            "check_out",
            async_check_out_service,
            schema=CHECK_OUT_SCHEMA,
        )
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Unregister services if no more entries
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "check_in")
            hass.services.async_remove(DOMAIN, "check_out")
    
    return unload_ok