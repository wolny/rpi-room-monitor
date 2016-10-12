import argparse
import json
import time
import arpscanner.scanner as arpscanner
import motion.detector as motion
import frameprocessor.processor as frameproc

parser = argparse.ArgumentParser(description='Find intruders in my room')
parser.add_argument("-c", help="JSON config file")
args = parser.parse_args()

with open(args.c) as config_file:
    config = json.load(config_file)

print('Config: ', config)
trusted_macs = set(config['trusted_macs'])
arp_interval = config['arp_scanner_interval']
scanner = arpscanner.ArpScanner(config['network_prefix'], arp_interval)

resolution = tuple(config['resolution'])
framerate = config['framerate']
detector = motion.MotionDetector(resolution, framerate)

frame_processor = frameproc.FrameProcessor()

# warm up
time.sleep(arp_interval)

while True:
    current_macs = scanner.mac_addresses()
    trusted_device_present = len(trusted_macs.intersection(current_macs)) > 0
    motion_detected = detector.is_motion_detected()
    if not trusted_device_present and motion_detected:
        frame_processor.process(detector.captured_frames())
    time.sleep(config['state_check_interval'])


