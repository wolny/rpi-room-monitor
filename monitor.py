import argparse
import json
import logging
import time

import arpscanner.scanner as arpscanner
import frameprocessor.processor as frameproc
import motion.detector as motion

# configure logger
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-10s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# parse config
parser = argparse.ArgumentParser(description='Find intruders in my room')
parser.add_argument("-c", help="JSON config file")
args = parser.parse_args()

with open(args.c) as config_file:
    config = json.load(config_file)

logger.info('Config: %s' % config)

# start arp-scanner
arp_interval = config['arp_scanner_interval']
network_prefix = config['network_prefix']
scanner = arpscanner.ArpScanner(network_prefix, arp_interval, logger=logger)
scanner.start()

# start motion detector
resolution = tuple(config['resolution'])
framerate = config['framerate']
detector = motion.MotionDetector(resolution, framerate, logger=logger)
detector.start()

# create frame processor
frame_processor = frameproc.FrameProcessor(config, logger)

trusted_macs = set(config['trusted_macs'])
while True:
    try:
        current_macs = scanner.mac_addresses()
        trusted_device_present = len(trusted_macs.intersection(current_macs)) > 0
        motion_detected = detector.is_motion_detected()
        if motion_detected:
            frames = detector.captured_frames()
            frame_processor.process(frames, trusted_device_present)

        time.sleep(config['state_check_interval'])
    except:
        self.logger.error('Unexpected error in the main processing loop', exc_info=True)
