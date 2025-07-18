"""Sesame Time API client."""
import logging
from typing import Dict, Any, Optional
import aiohttp
import json

try:
    from .const import DEFAULT_TIMEOUT, USER_AGENT
except ImportError:
    # For standalone testing
    from const import DEFAULT_TIMEOUT, USER_AGENT

_LOGGER = logging.getLogger(__name__)


class SesameTimeAPI:
    """Handle communication with Sesame Time API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        region: str,
        token: Optional[str] = None,
        employee_id: Optional[str] = None,
        company_id: Optional[str] = None,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._region = region
        self._token = token
        self._employee_id = employee_id
        self._company_id = company_id
        self._base_url = f"https://back-{region}.sesametime.com/api/v3"
        
    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get common headers for API requests."""
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": "https://app.sesametime.com",
            "referer": "https://app.sesametime.com/",
            "user-agent": USER_AGENT,
            "rsrc": "31",
        }
        
        if include_auth and self._employee_id and self._company_id:
            headers.update({
                "esid": self._employee_id,
                "csid": self._company_id,
            })
            
        return headers
    
    def _get_cookies(self) -> Dict[str, str]:
        """Get cookies for authenticated requests."""
        if self._token:
            return {"USID": self._token}
        return {}
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login to Sesame Time and get token."""
        url = f"{self._base_url}/security/login"
        data = {
            "platformData": {
                "platformName": "Home Assistant",
                "platformSystem": "Integration",
                "platformVersion": "1.0"
            },
            "email": email,
            "password": password
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
            async with self._session.post(
                url,
                headers=self._get_headers(include_auth=False),
                data=json.dumps(data),
                timeout=timeout,
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self._token = result.get("data")
                    _LOGGER.debug("Login successful")
                    return {"success": True, "token": self._token}
                else:
                    text = await response.text()
                    _LOGGER.error(f"Login failed: {response.status} - {text}")
                    return {"success": False, "error": f"Login failed: {response.status}"}
                    
        except Exception as err:
            _LOGGER.error(f"Login error: {err}")
            return {"success": False, "error": str(err)}
    
    async def get_me(self) -> Dict[str, Any]:
        """Get current user information."""
        if not self._token:
            return {"success": False, "error": "Not authenticated"}
            
        url = f"{self._base_url}/security/me"
        
        try:
            timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
            
            # First try without auth headers
            cookies = self._get_cookies()
            async with self._session.get(
                url,
                headers=self._get_headers(include_auth=False),
                cookies=cookies,
                timeout=timeout,
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    data = result.get("data", [])
                    if data and len(data) > 0:
                        user_data = data[0]
                        self._employee_id = user_data.get("id")
                        self._company_id = user_data.get("companyId")
                        
                        return {
                            "success": True,
                            "employee_id": self._employee_id,
                            "company_id": self._company_id,
                            "employee_name": f"{user_data.get('firstName', '')} {user_data.get('lastName', '')}".strip(),
                            "company_name": user_data.get("companyName"),
                            "last_check": user_data.get("lastCheck"),
                            "work_status": user_data.get("workStatus"),
                        }
                else:
                    text = await response.text()
                    _LOGGER.error(f"Get me failed: {response.status} - {text}")
                    return {"success": False, "error": f"Get me failed: {response.status}"}
                    
        except Exception as err:
            _LOGGER.error(f"Get me error: {err}")
            return {"success": False, "error": str(err)}
    
    async def check_in(self) -> Dict[str, Any]:
        """Perform check-in."""
        if not all([self._token, self._employee_id, self._company_id]):
            return {"success": False, "error": "Missing authentication data"}
            
        url = f"{self._base_url}/employees/{self._employee_id}/check-in"
        data = {
            "origin": "web",
            "coordinates": {},
            "workCheckTypeId": None
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
            cookies = self._get_cookies()
            
            async with self._session.post(
                url,
                headers=self._get_headers(),
                cookies=cookies,
                data=json.dumps(data),
                timeout=timeout,
            ) as response:
                if response.status == 200:
                    _LOGGER.info("Check-in successful")
                    return {"success": True}
                else:
                    text = await response.text()
                    _LOGGER.error(f"Check-in failed: {response.status} - {text}")
                    return {"success": False, "error": f"Check-in failed: {response.status}"}
                    
        except Exception as err:
            _LOGGER.error(f"Check-in error: {err}")
            return {"success": False, "error": str(err)}
    
    async def check_out(self) -> Dict[str, Any]:
        """Perform check-out."""
        if not all([self._token, self._employee_id, self._company_id]):
            return {"success": False, "error": "Missing authentication data"}
            
        url = f"{self._base_url}/employees/{self._employee_id}/check-out"
        data = {
            "origin": "web",
            "coordinates": {},
            "workCheckTypeId": None
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
            cookies = self._get_cookies()
            
            async with self._session.post(
                url,
                headers=self._get_headers(),
                cookies=cookies,
                data=json.dumps(data),
                timeout=timeout,
            ) as response:
                if response.status == 200:
                    _LOGGER.info("Check-out successful")
                    return {"success": True}
                else:
                    text = await response.text()
                    _LOGGER.error(f"Check-out failed: {response.status} - {text}")
                    return {"success": False, "error": f"Check-out failed: {response.status}"}
                    
        except Exception as err:
            _LOGGER.error(f"Check-out error: {err}")
            return {"success": False, "error": str(err)}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current check-in status."""
        result = await self.get_me()
        if result.get("success"):
            last_check = result.get("last_check", {})
            if last_check:
                has_check_out = last_check.get("checkOutDatetime") is not None
                return {
                    "success": True,
                    "is_checked_in": not has_check_out,
                    "last_check_in": last_check.get("checkInDatetime"),
                    "last_check_out": last_check.get("checkOutDatetime"),
                    "work_status": result.get("work_status"),
                }
        
        return result