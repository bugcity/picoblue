# 2.4GHz Wi-fi only
WIFI_SSID = 'your wifi SSID'
WIFI_PASSWORD = 'your wifi password'
COUNTRY = 'your country'  # JP, US, etc.

# Meter
METERS = [
    {'MACADDR': '00:11:22:33:44:55', 'MODEL': 'meter', 'ZABBIX_HOST': 'host name meter'},
    {'MACADDR': 'aa:bb:cc:dd:ee:ff', 'MODEL': 'outdoor-meter', 'ZABBIX_HOST': 'host name outdoor-meter'},
    {'MACADDR': 'dd:bb:cc:dd:ee:ff', 'MODEL': 'plug-mini', 'ZABBIX_HOST': 'host name plug-mini'},
]

# Zabbix
ZABBIX_SERVER = 'your.zabbix.server'
ZABBIX_PORT = 10051

# Zabbix item keys
BATTERY_ITEM_KEY = 'switchbot.meter.battery'
TEMPERATURE_ITEM_KEY = 'switchbot.meter.temperature'
HUMIDITY_ITEM_KEY = 'switchbot.meter.humidity'
POWER_ITEM_KEY = 'switchbot.plug.power'
