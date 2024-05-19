# Raspberry Pi Pico W MicroPython SwitchBot Hub Mini Data Sending Script

This script operates on Raspberry Pi Pico W using MicroPython, fetching temperature and humidity data from SwitchBot Hub Mini via Bluetooth, and sending it to Zabbix.

## Prerequisites

- Raspberry Pi Pico W is set up, and MicroPython is installed.
- Zabbix server is available, and an endpoint to receive data is configured.

## Installation and Configuration

1. Clone this repository:

    ```bash
    git clone https://github.com/bugcity/picoblue.git
    ```

2. Open the `config.py` file and edit the following settings:

    ```python
    # config.py

    # 2.4GHz Wi-fi only
    WIFI_SSID = 'your wifi SSID'
    WIFI_PASSWORD = 'your wifi password'
    COUNTRY = 'your country'  # JP, US, etc.

    # Meter
    METERS = [
        {'MACADDR': '00:11:22:33:44:55', 'MODEL': 'meter', 'ZABBIX_HOST': 'host name meter'},
        {'MACADDR': 'aa:bb:cc:dd:ee:ff', 'MODEL': 'outdoor-meter', 'ZABBIX_HOST': 'host name outdoor-meter'},
    ]

    # Zabbix
    ZABBIX_SERVER = 'your.zabbix.server'
    ZABBIX_PORT = 10051

    # Zabbix item keys
    BATTERY_ITEM_KEY = 'switchbot.meter.battery'
    TEMPERATURE_ITEM_KEY = 'switchbot.meter.temperature'
    HUMIDITY_ITEM_KEY = 'switchbot.meter.humidity'
    ```

    Adjust the values for each item according to the information for your SwitchBot Hub Mini and Zabbix server.

## License

This script is provided under the MIT license.
