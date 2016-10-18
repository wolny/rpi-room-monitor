import argparse
import json
import logging
import time

import flickrapi

import arpscanner.scanner as arpscanner
import frameprocessor.processor as frameproc
import ftp.ftp_client as ftp
import motion.detector as motion

# configure logger
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-10s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# parse config
parser = argparse.ArgumentParser(description='Find intruders in my room')
parser.add_argument("-c", help="JSON config file")
args = parser.parse_args()

with open(args.c) as config_file:
    config = json.load(config_file)

logger.info('Config: %s' % config)
trusted_macs = set(config['trusted_macs'])
arp_interval = config['arp_scanner_interval']
scanner = arpscanner.ArpScanner(config['network_prefix'], arp_interval, logger=logger)

resolution = tuple(config['resolution'])
framerate = config['framerate']
detector = motion.MotionDetector(resolution, framerate, logger=logger)

ftp_client = None
if config['ftp_enabled']:
    ftp_client = ftp.FtpClient(config['ftp_host'], config['ftp_user'], config['ftp_passwd'], config.get('ftp_dir'))

flickr = None
if config['flickr_enabled']:
    flickr = flickrapi.FlickrAPI(config['flickr_api_key'], config['flickr_api_secret'])

# warm up
time.sleep(arp_interval)

while True:
    current_macs = scanner.mac_addresses()
    trusted_device_present = len(trusted_macs.intersection(current_macs)) > 0
    motion_detected = detector.is_motion_detected()
    if motion_detected:
        frames = detector.captured_frames()
        if not trusted_device_present:
            frameproc.FrameProcessor(frames, ftp_client, flickr, logger=logger)
    time.sleep(config['state_check_interval'])
