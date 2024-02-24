import network
import rp2
import ubinascii
import time


class WIFI:
    _wifi = None

    def __init__(self, country: str, ssid: str, password: str):
        self.country = country
        self.ssid = ssid
        self.password = password

    def __enter__(self):
        return self._connect()

    def __exit__(self, exc_type, exc_value, traceback):
        self._disconnect()

    def _connect(self):
        rp2.country(self.country)
        self._wifi = network.WLAN(network.STA_IF)
        if not self._wifi.isconnected():
            self._wifi.active(True)
            self._wifi.connect(self.ssid, self.password)
            cnt = 10
            while not self._wifi.isconnected():
                cnt -= 1
                if cnt <= 0:
                    raise Exception('can not connect wifi')
                time.sleep(1)

    def _disconnect(self):
        if self._wifi:
            self._wifi.disconnect()
            self._wifi.active(False)
            del self._wifi
            self._wifi = None
