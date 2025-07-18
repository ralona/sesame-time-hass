"""The Sesame Time integration."""
import logging
from typing import Dict, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

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
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok