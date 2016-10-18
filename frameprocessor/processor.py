import logging
import random
import threading
import time

import cv2


class FrameProcessor:
    def __init__(self, frames, ftp_client=None, flickr=None, logger=None):
        self.logger = logger or logging.getLogger()
        self.tmp_dir = '/tmp/'
        self.frames = frames
        self.ftp_client = ftp_client
        self.flickr = flickr
        self.task = threading.Thread(target=self.process)
        self.task.daemon = True
        self.task.start()

    def process(self):
        if self.frames:
            files = self.save_tmp(self.frames)
            self.upload_ftp(files)
            # pick random image and upload to flickr
            filename = random.choice(files)
            self.upload_flickr(filename)
        else:
            self.logger.debug('Noting to save')

    def upload_flickr(self, filename):
        if self.flickr is not None:
            res = self.flickr.upload(filename, open(self.tmp_dir + filename, 'rb'))
            status = res.attrib['stat']
            self.logger.info('Flickr upload: %s. Status %s' % (filename, status))

    def upload_ftp(self, files):
        if self.ftp_client is not None:
            ftp = self.ftp_client.session()
            for filename in files:
                rsp_code = ftp.storbinary("STOR " + filename, open(self.tmp_dir + filename, 'rb'))
                self.logger.info('FTP upload %s. Response code: %s' %(filename, rsp_code))

    def save_tmp(self, frames):
        self.logger.debug('Saving %d images to %s' % (len(frames), self.tmp_dir))
        ts = time.strftime("%Y%m%d%H%M%S")
        files = []
        for i, frame in enumerate(frames):
            filename = 'motion-%s-%02d.jpg' % (ts, i)
            files.append(filename)
            cv2.imwrite(self.tmp_dir + filename, frame)
        return files
