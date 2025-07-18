"""Config flow for Sesame Time integration."""
import logging
from typing import Any, Dict, Optional
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SesameTimeAPI
from .const import (
    DOMAIN,
    REGIONS,
    CONF_REGION,
    CONF_TOKEN,
    CONF_EMPLOYEE_ID,
    CONF_COMPANY_ID,
    CONF_EMPLOYEE_NAME,
    CONF_COMPANY_NAME,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    api = SesameTimeAPI(session, data[CONF_REGION])
    
    # Login
    login_result = await api.login(data[CONF_EMAIL], data[CONF_PASSWORD])
    if not login_result.get("success"):
        raise ValueError(login_result.get("error", "Login failed"))
    
    # Get user info
    user_result = await api.get_me()
    if not user_result.get("success"):
        raise ValueError(user_result.get("error", "Failed to get user info"))
    
    return {
        CONF_TOKEN: login_result.get("token"),
        CONF_EMPLOYEE_ID: user_result.get("employee_id"),
        CONF_COMPANY_ID: user_result.get("company_id"),
        CONF_EMPLOYEE_NAME: user_result.get("employee_name"),
        CONF_COMPANY_NAME: user_result.get("company_name"),
    }


class SesameTimeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sesame Time."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # Create unique ID based on employee ID
                await self.async_set_unique_id(info[CONF_EMPLOYEE_ID])
                self._abort_if_unique_id_configured()
                
                # Store all necessary data
                data = {
                    CONF_REGION: user_input[CONF_REGION],
                    CONF_EMAIL: user_input[CONF_EMAIL],
                    CONF_TOKEN: info[CONF_TOKEN],
                    CONF_EMPLOYEE_ID: info[CONF_EMPLOYEE_ID],
                    CONF_COMPANY_ID: info[CONF_COMPANY_ID],
                    CONF_EMPLOYEE_NAME: info[CONF_EMPLOYEE_NAME],
                    CONF_COMPANY_NAME: info[CONF_COMPANY_NAME],
                }
                
                # Title will be "Employee Name - Company Name"
                title = f"{info[CONF_EMPLOYEE_NAME]} - {info[CONF_COMPANY_NAME]}"
                
                return self.async_create_entry(title=title, data=data)
                
            except ValueError as err:
                errors["base"] = "auth_failed"
                _LOGGER.error(f"Authentication failed: {err}")
            except Exception as err:
                errors["base"] = "unknown"
                _LOGGER.exception(f"Unexpected error: {err}")
        
        # Show form
        data_schema = vol.Schema({
            vol.Required(CONF_REGION, default="eu1"): vol.In(REGIONS),
            vol.Required(CONF_EMAIL): str,
            vol.Required(CONF_PASSWORD): str,
        })
        
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )