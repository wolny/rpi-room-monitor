import argparse
import json
import time
import arpscanner.scanner as arpscanner

parser = argparse.ArgumentParser(description='Find intruders in my room')
parser.add_argument("-c", help="JSON config file")
args = parser.parse_args()

with open(args.c) as config_file:
    config = json.load(config_file)

print('Config: ', config)
s = arpscanner.ArpScanner(config['network_prefix'], config['arp_scanner_interval'])
#s.task.join()

for i in range(10):
    print(s.mac_addresses())
    time.sleep(2)
