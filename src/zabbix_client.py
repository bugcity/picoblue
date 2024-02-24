import socket
import json
import struct
import time
import re


class ZabbixClient:
    def __init__(self, zabbix_server, zabbix_port, zabbix_host):
        self.zabbix_server = str(zabbix_server)
        self.zabbix_port = int(zabbix_port)
        self.zabbix_host = str(zabbix_host)

    def send(self, data):
        self.status = None
        data = {
            "request": "sender data",
            "data": [
                {
                    'host': self.zabbix_host,
                    'key': key,
                    'value': value,
                }
                for key, value in data.items()
            ]
        }
        data = str(json.dumps(data)).encode('utf-8')
        packet = b"ZBXD\1" + struct.pack("<II", len(data), 0) + data

        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.zabbix_server, self.zabbix_port))
            sock.send(packet)
            time.sleep(0.5)
            status = sock.recv(1024).decode('utf-8')
            re_status = re.compile(r'(\{.*\})')
            status = re_status.search(status).groups()[0]
            self.status = json.loads(status)

        finally:
            if sock:
                sock.close()

        return self.status
