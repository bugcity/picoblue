from bluebot import SwitchBotTempAndHumidSensor
from config import COUNTRY, WIFI_SSID, WIFI_PASSWORD, MACADDR, \
    ZABBIX_SERVER, ZABBIX_PORT, ZABBIX_HOST, \
    BATTERY_ITEM_KEY, TEMPERATURE_ITEM_KEY, HUMIDITY_ITEM_KEY
import machine
import time
from wifi import WIFI
from zabbix_client import ZabbixClient


def main():
    sb = SwitchBotTempAndHumidSensor(MACADDR)
    sb.scan(10000)

    zabbix_data = {
        BATTERY_ITEM_KEY: sb.battery,
        TEMPERATURE_ITEM_KEY: sb.temperature,
        HUMIDITY_ITEM_KEY: sb.humidity,
    }

    with WIFI(COUNTRY, WIFI_SSID, WIFI_PASSWORD):
        zc = ZabbixClient(ZABBIX_SERVER, ZABBIX_PORT, ZABBIX_HOST)
        print(zc.send(zabbix_data))


while True:
    try:
        main()
    except Exception:
        continue
    time.sleep(60)
