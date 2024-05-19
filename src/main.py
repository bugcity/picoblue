from bluebot import SwitchBotScanner, SwitchBotTempAndHumidSensorMeter, SwitchBotTempAndHumidSensorOutdoor
from config import COUNTRY, WIFI_SSID, WIFI_PASSWORD, \
    METERS, ZABBIX_SERVER, ZABBIX_PORT, \
    BATTERY_ITEM_KEY, TEMPERATURE_ITEM_KEY, HUMIDITY_ITEM_KEY
import machine
import time
from wifi import WIFI
from zabbix_client import ZabbixClient


switchbot_meters = {
    'meter': SwitchBotTempAndHumidSensorMeter,
    'outdoor-meter': SwitchBotTempAndHumidSensorOutdoor,
}


def main():
    sbs = SwitchBotScanner()
    for meter_conf in METERS:
        macaddr = meter_conf['MACADDR']
        model = meter_conf['MODEL']
        zabbix_host = meter_conf['ZABBIX_HOST']
        meter = switchbot_meters[model](macaddr)
        setattr(meter, 'zabbix_host', zabbix_host)
        sbs.add(meter)

    print('scan start')
    sbs.scan(10000)
    print('scan end')

    with WIFI(COUNTRY, WIFI_SSID, WIFI_PASSWORD):
        for client in sbs.clients.values():
            if client.has_data:
                zabbix_data = {
                    BATTERY_ITEM_KEY: client.battery,
                    TEMPERATURE_ITEM_KEY: client.temperature,
                    HUMIDITY_ITEM_KEY: client.humidity,
                }
                zc = ZabbixClient(ZABBIX_SERVER, ZABBIX_PORT, client.zabbix_host)
                print(client.zabbix_host, zc.send(zabbix_data))


while True:
    try:
        main()
    except Exception:
        continue
    time.sleep(60)
