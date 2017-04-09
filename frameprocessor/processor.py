import logging
import random
import time

import cv2
import flickrapi

from flickr.flickr_uploader import FlickrUploader
from ftp.ftp_uploader import FtpUploader


class FrameProcessor:
    TMP_DIR = '/tmp/'

    def __init__(self, config, counter, logger=None):
        self.config = config
        self.counter = counter
        self.logger = logger or logging.getLogger()

        self.flickr = None
        if config['flickr_enabled']:
            api_key = config['flickr_api_key']
            api_secret = config['flickr_api_secret']
            self.flickr = flickrapi.FlickrAPI(api_key, api_secret)

    def process(self, frames, trusted_device_present):
        if frames:
            # always save to /tmp
            files = self.save_tmp(frames)

            # upload only if no trusted devices are present
            if not trusted_device_present:
                self.upload_flickr(files)
                self.upload_ftp(files)
        else:
            self.logger.debug('Noting to save')

    def save_tmp(self, frames):
        self.logger.debug('Saving %d images to %s' % (len(frames), FrameProcessor.TMP_DIR))
        ts = time.strftime("%Y%m%d%H%M%S")
        files = []
        for i, frame in enumerate(frames):
            filename = 'motion-%s-%02d.jpg' % (ts, i)
            files.append(filename)
            cv2.imwrite(FrameProcessor.TMP_DIR + filename, frame)
        return files

    def upload_ftp(self, files):
        if self.config['ftp_enabled']:
            host = self.config['ftp_host']
            user = self.config['ftp_user']
            passwd = self.config['ftp_passwd']
            ftp_dir = self.config.get('ftp_dir')
            FtpUploader(files, host, user, passwd, ftp_dir, self.logger).start()
            self.counter.increment("ftp.uploadedFrames", len(files))

    def upload_flickr(self, files):
        if self.flickr:
            # pick random image and upload to flickr
            filename = random.choice(files)
            FlickrUploader(filename, self.flickr, self.logger).start()
            self.counter.increment("flickr.uploadedFrames", 1)
