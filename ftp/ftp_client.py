from ftplib import FTP


class FtpClient:
    def __init__(self, host, user, passwd, dir=None):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dir = dir

    def session(self):
        ftp = FTP(self.host, user=self.user, passwd=self.passwd)
        if dir:
            ftp.cwd(self.dir)
        return ftp
