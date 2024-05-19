import ubluetooth
import ubinascii
from micropython import const
import uasyncio as asyncio
from utime import sleep


_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)


class BLEScanner:
    def __init__(self, ble, clients):
        self.clients = clients
        self.ble = ble
        self.ble.active(True)
        self.ble.irq(self._irq_handler)

    def call_client(self, client, adv_type, adv_data):

        i = 0
        while i < len(adv_data):
            length = adv_data[i]
            type = adv_data[i + 1]
            data = adv_data[i + 2:i + length + 1]
            client.scaned(type, adv_type, data)
            i += length + 1

    def _irq_handler(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            addr_str = ':'.join(['{:02x}'.format(b) for b in addr])
            if addr_str in self.clients.keys():
                client = self.clients[addr_str]
                self.call_client(client, adv_type, adv_data)

    def start(self, duration_ms):
        self.ble.gap_scan(duration_ms, 30000, 30000, True)

    def stop(self):
        self.ble.gap_scan(None)


class SwitchBotScanner:
    def __init__(self):
        self.clients = {}
        self.done_clients = 0

    def add(self, client):
        self.clients[client.macaddr] = client

    def clienthas_data(self, macaddr):
        self.done_clients += 1

    def scan(self, duration):
        self.done_clients = 0
        ble = ubluetooth.BLE()
        self.scanner = BLEScanner(ble, self.clients)
        self.scanner.start(duration)
        remain = int(duration / 0.5)
        all_clients = len(self.clients)
        while self.done_clients < all_clients:
            remain -= 1
            if remain <= 0:
                break
            asyncio.sleep(0.5)
        self.scanner.stop()
        del self.scanner
        del ble
        return not (self.done_clients < all_clients)


class SwitchBotSensor:

    def __init__(self, macaddr):
        self.done_callback = None
        self.macaddr = macaddr
        self.clear_data()

    def scan_done(self):
        self.has_data = True
        if self.done_callback:
            self.done_callback(self.macaddr)

    def clear_data(self):
        self.has_data = False


class SwitchBotTempAndHumidSensor(SwitchBotSensor):

    def clear_data(self):
        super().clear_data()
        self.battery = None
        self.humidity = None
        self.temperature = None


class SwitchBotTempAndHumidSensorMeter(SwitchBotTempAndHumidSensor):

    def extract_data(self, data):
        self.battery = data[4] & 0b01111111
        self.humidity = data[7] & 0b01111111
        self.temperature = (data[5] & 0b00001111) / 10 + (data[6] & 0b01111111)
        isTemperatureAboveFreezing = data[6] & 0b10000000
        if not isTemperatureAboveFreezing:
            self.temperature = -self.temperature

    def scaned(self, type, adv_type, data):
        if self.has_data:
            return
        if type == 0x16 and adv_type == 4:
            self.extract_data(data)
            self.scan_done()


class SwitchBotTempAndHumidSensorOutdoor(SwitchBotTempAndHumidSensor):

    def clear_data(self):
        super().clear_data()
        self.scan_finished_service = False
        self.scan_finished_manufacturer = False

    def extract_service_data(self, data):
        self.battery = data[4] & 0b01111111

    def extract_manufacturer_data(self, data):
        self.humidity = data[12] & 0b01111111
        self.temperature = (data[10] & 0b00001111) / 10 + (data[11] & 0b01111111)
        isTemperatureAboveFreezing = (data[11] & 0b10000000)
        if not isTemperatureAboveFreezing:
            self.temperature = -self.temperature

    def scaned(self, type, adv_type, data):
        if self.has_data:
            return
        if not self.scan_finished_service and type == 0x16 and adv_type == 4:
            self.extract_service_data(data)
            self.scan_finished_service = True
        if not self.scan_finished_manufacturer and type == 0xff and adv_type == 0:
            self.extract_manufacturer_data(data)
            self.scan_finished_manufacturer = True
        if self.scan_finished_service and self.scan_finished_manufacturer:
            self.scan_done()
