import logging
import threading
from ftplib import FTP


class FtpUploader(threading.Thread):
    TMP_DIR = '/tmp/'

    def __init__(self, files, host, user, passwd, ftp_dir=None, logger=None):
        super().__init__()
        self.daemon = True
        self.files = files
        self.host = host
        self.user = user
        self.passwd = passwd
        self.ftp_dir = ftp_dir
        self.logger = logger or logging.getLogger()

    def run(self):
        try:
            ftp = FTP(self.host, user=self.user, passwd=self.passwd)
            if self.ftp_dir:
                ftp.cwd(self.ftp_dir)

            for filename in self.files:
                rsp_code = ftp.storbinary("STOR " + filename, open(FtpUploader.TMP_DIR + filename, 'rb'))
                self.logger.info('FTP upload %s: %s' % (filename, rsp_code))
        except:
            self.logger.error('Unexpected error', exc_info=True)
        finally:
            if ftp:
                ftp.close()
