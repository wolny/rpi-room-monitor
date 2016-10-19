import logging
import threading


class FlickrUploader(threading.Thread):
    TMP_DIR = '/tmp/'

    def __init__(self, filename, filckr, logger=None):
        super().__init__()
        self.daemon = True
        self.filename = filename
        self.flickr = filckr
        self.logger = logger or logging.getLogger()

    def run(self):
        res = self.flickr.upload(self.filename, open(FlickrUploader.TMP_DIR + self.filename, 'rb'))
        status = res.attrib['stat']
        self.logger.info('Flickr upload: %s. Status %s' % (self.filename, status))
