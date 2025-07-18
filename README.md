# Sesame Time for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Custom Home Assistant integration for Sesame Time - Employee time tracking and attendance management.

## Features

- 🔐 Multi-employee support - Add multiple employee accounts
- 📊 Real-time status sensor (checked in/out)
- 🔘 Smart check-in/out button
- 🌍 Multi-region support (EU, US, LATAM)
- 🔄 No token expiration - Login once, use forever
- 🏢 Each employee as separate device

## Testing the API

Before installing, you can test the API connection:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```bash
   SESAME_REGION=eu1
   SESAME_EMAIL=your-email@example.com
   SESAME_PASSWORD=your-password
   ```

3. Install required dependencies:
   ```bash
   pip install aiohttp python-dotenv
   ```

4. Run the test:
   ```bash
   python test_api.py
   ```

## Installation

### HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Search for "Sesame Time" in HACS
3. Install the integration
4. Restart Home Assistant
5. Add integration from Settings → Devices & Services

### Manual Installation

1. Copy the `custom_components/sesame_time` folder to your `custom_components` directory
2. Restart Home Assistant
3. Add integration from Settings → Devices & Services

## Configuration

1. Click "Add Integration"
2. Search for "Sesame Time"
3. Select your region
4. Enter your email and password
5. The integration will create a device for your employee account

## Entities

Each employee device includes:

### Sensor
- **State**: `checked_in` or `checked_out`
- **Attributes**:
  - Last check-in time
  - Last check-out time
  - Employee name
  - Company name
  - Work status

### Button
- **Check In/Out**: Smart button that checks you in or out based on current state

## Services

### `sesame_time.check_in`
Check in an employee.

### `sesame_time.check_out`
Check out an employee.

## Example Automations

### Auto check-in when arriving at work
```yaml
automation:
  - alias: "Auto check-in at work"
    trigger:
      - platform: zone
        entity_id: person.me
        zone: zone.work
        event: enter
    action:
      - service: sesame_time.check_in
        target:
          entity_id: button.ramon_lopez_sesame_check_in_out
```

### Reminder to check out
```yaml
automation:
  - alias: "Reminder to check out"
    trigger:
      - platform: time
        at: "18:00:00"
    condition:
      - condition: state
        entity_id: sensor.ramon_lopez_sesame_status
        state: "checked_in"
    action:
      - service: notify.mobile_app
        data:
          message: "Don't forget to check out!"
```

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/ralona/sesame-time-hass/issues).