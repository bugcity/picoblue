import ubluetooth
import ubinascii
from micropython import const
import uasyncio as asyncio
from utime import sleep


_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)


class BLEScanner:
    def __init__(self, ble, owner):
        self.ble = ble
        self.ble.active(True)
        self.ble.irq(self._irq_handler)
        self.target_addr = owner.target_addr
        self.owner = owner

    def _irq_handler(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            addr_str = ':'.join(['{:02x}'.format(b) for b in addr])
            if addr_str == self.target_addr and adv_type == 4:
                self._parseData(adv_data)
                self.stop_scan()

        elif event == _IRQ_SCAN_DONE:
            self.owner.scan_done()

    def _parseData(self, data):
        uuid, service_data = self.get_manufacturer_specific_data(data)
        self.owner.scaned(uuid, service_data)

    def get_manufacturer_specific_data(self, adv_data):

        i = 0
        while i < len(adv_data):
            length = adv_data[i]
            type = adv_data[i + 1]

            if type == 0x16:
                uuid = bytes(reversed(adv_data[i + 2:i + 4])).hex()
                service_data = adv_data[i + 4:i + length + 1]
                return uuid, service_data

            i += length + 1
        return None, None

    def start_scan(self, duration_ms):
        self.ble.gap_scan(duration_ms, 30000, 30000, True)

    def stop_scan(self):
        self.ble.gap_scan(None)


class SwitchBotSensor:

    _scan_end = False

    def __init__(self, target_addr):
        self.target_addr = target_addr
        ble = ubluetooth.BLE()
        self.scanner = BLEScanner(ble, self)

    def scan(self, duration):
        self._scan_end = False
        self.scanner.start_scan(duration)
        remain = int(duration / 0.5)
        while not self._scan_end:
            remain -= 1
            if remain <= 0:
                break
            asyncio.sleep(0.5)
        self.scanner.stop_scan()
        return self._scan_end

    def scaned(self, uuid, service_data):
        self._scan_end = True

    def scan_done(self):
        self._scan_end = True


class SwitchBotTempAndHumidSensor(SwitchBotSensor):

    battery = None
    temperature = None
    humidity = None

    def scaned(self, uuid, service_data):
        battery = service_data[2] & 0b01111111
        temperature = (service_data[3] & 0b00001111) / 10 + (service_data[4] & 0b01111111)
        isTemperatureAboveFreezing = service_data[4] & 0b10000000

        if not isTemperatureAboveFreezing:
            temperature = -temperature

        humidity = service_data[5] & 0b01111111

        self.battery = battery
        self.temperature = temperature
        self.humidity = humidity

        super().scaned(uuid, service_data)
