"""Constants for the Sesame Time integration."""

DOMAIN = "sesame_time"

# Configuration
CONF_REGION = "region"
CONF_TOKEN = "token"
CONF_EMPLOYEE_ID = "employee_id"
CONF_COMPANY_ID = "company_id"
CONF_EMPLOYEE_NAME = "employee_name"
CONF_COMPANY_NAME = "company_name"

# API
DEFAULT_TIMEOUT = 30
USER_AGENT = "Home Assistant Sesame Time Integration"

# Regions
REGIONS = {
    "eu1": "Europe",
    "us1": "United States",
    "latam1": "Latin America",
}

# States
STATE_CHECKED_IN = "checked_in"
STATE_CHECKED_OUT = "checked_out"

# Attributes
ATTR_LAST_CHECK_IN = "last_check_in"
ATTR_LAST_CHECK_OUT = "last_check_out"
ATTR_EMPLOYEE_NAME = "employee_name"
ATTR_COMPANY_NAME = "company_name"
ATTR_WORK_STATUS = "work_status"