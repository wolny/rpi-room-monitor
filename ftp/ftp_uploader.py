import logging
import threading
from ftplib import FTP


class FtpUploader(threading.Thread):

    TMP_DIR = '/tmp/'

    def __init__(self, files, host, user, passwd, dir=None, logger=None):
        super().__init__()
        self.daemon = True
        self.files = files
        self.ftp = FTP(host, user=user, passwd=passwd)
        if dir:
            self.ftp.cwd(dir)
        self.logger = logger or logging.getLogger()

    def run(self):
        try:
            for filename in self.files:
                rsp_code = self.ftp.storbinary("STOR " + filename, open(FtpUploader.TMP_DIR + filename, 'rb'))
                self.logger.info('FTP upload %s: %s' % (filename, rsp_code))
        except:
            self.logger.error('Unexpected error', exc_info=True)
        finally:
            self.ftp.close()

