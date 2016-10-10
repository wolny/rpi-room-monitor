import subprocess
import threading
import time
import sys


class ArpScanner:
    """
    Simple scanner which broadcasts ARP packets on the local network and returns a list of discovered MAC addresses.
    Requires arp-scanner to be installed, e.g. Ubuntu/Debian: 'sudo apt-get install arp-scanner'
    apr-scanner needs to be run as root, so add the following line to you sudoers file (visudo):
    myuser ALL = (root) NOPASSWD: /usr/bin/arp-scan
    """
    CMD = 'sudo arp-scan -l'

    def __init__(self, net_prefix, interval=10):
        self.prefix = net_prefix.encode()
        self.interval = interval
        self.macs = set()
        self.lock = threading.RLock()
        self.task = threading.Thread(target=self.scan)
        self.task.start()


    def run_arp_scan(self):
        p = subprocess.Popen(ArpScanner.CMD.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return iter(p.stdout.readline, b'')

    def is_host(self, line):
        return line.startswith(self.prefix)

    def line_to_mac(self, line):
        return line.split()[1].decode()

    def scan(self):
        while True:
            try:
                results = set(map(self.line_to_mac, filter(self.is_host, self.run_arp_scan())))
                with self.lock:
                    self.macs = results
                time.sleep(self.interval)
            except:
                print("Unexpected error:", sys.exc_info()[0])

    def mac_addresses(self):
        with self.lock:
            return self.macs