import random
import time

import cv2


class FrameProcessor:
    def __init__(self, ftp=None, flickr=None):
        self.ftp = ftp
        self.flickr = flickr

    def process(self, frames):
        if frames:
            files = self.save_tmp(frames)
            self.upload_ftp(files)
            # pick random image and upload to flickr
            filename = random.choice(files)
            self.upload_flickr(filename)
        else:
            print('Noting to save')

    def upload_flickr(self, filename):
        if self.flickr is not None:
            res = self.flickr.upload(filename, open(filename, 'rb'))
            status = res.attrib['stat']
            print('Flickr upload: %s. Status %s' % (filename, status))

    def upload_ftp(self, files):
        if self.ftp is not None:
            for filename in files:
                rsp_code = self.ftp.storbinary("STOR " + filename, open(filename, 'rb'))
                print('FTP upload %s. Response code: %s' %(filename, rsp_code))

    def save_tmp(self, frames):
        print('Saving %d images to /tmp' % len(frames))
        ts = time.strftime("%Y%m%d%H%M%S")
        files = []
        for i, frame in enumerate(frames):
            filename = '/tmp/motion-%s-%02d.jpg' % (ts, i)
            files.append(filename)
            cv2.imwrite(filename, frame)
        return files
