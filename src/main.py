from bluebot import SwitchBotScanner, SwitchBotTempAndHumidSensorMeter, SwitchBotTempAndHumidSensorOutdoor, SwitchBotPlugMini
from config import COUNTRY, WIFI_SSID, WIFI_PASSWORD, \
    METERS, ZABBIX_SERVER, ZABBIX_PORT, \
    BATTERY_ITEM_KEY, TEMPERATURE_ITEM_KEY, HUMIDITY_ITEM_KEY, POWER_ITEM_KEY, \
    ZABBIX_HOST, INTERVAL
import machine
import time
from wifi import WIFI
from zabbix_client import ZabbixClient


switchbot_meters = {
    'meter': SwitchBotTempAndHumidSensorMeter,
    'outdoor-meter': SwitchBotTempAndHumidSensorOutdoor,
    'plug-mini': SwitchBotPlugMini,
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
                if client.model == 'plug-mini':
                    zabbix_data = {
                        POWER_ITEM_KEY: client.power,
                    }
                else:
                    zabbix_data = {
                        BATTERY_ITEM_KEY: client.battery,
                        TEMPERATURE_ITEM_KEY: client.temperature,
                        HUMIDITY_ITEM_KEY: client.humidity,
                    }
                zc = ZabbixClient(ZABBIX_SERVER, ZABBIX_PORT, client.zabbix_host)
                print(client.zabbix_host, zc.send(zabbix_data))

        # rpi temp
        sensor_temp = machine.ADC(4)
        conversion_factor = 3.3 / 65535
        reading = sensor_temp.read_u16() * conversion_factor
        temperature = 27 - (reading - 0.706) / 0.001721
        zabbix_data = {
            TEMPERATURE_ITEM_KEY: temperature,
        }
        zc = ZabbixClient(ZABBIX_SERVER, ZABBIX_PORT, ZABBIX_HOST)
        print(ZABBIX_HOST, zc.send(zabbix_data))


while True:
    try:
        main()
    except Exception:
        continue
    time.sleep(INTERVAL)
