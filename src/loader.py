#-*- coding: utf-8 -*-

import yaml, subprocess, shlex, bz2, paramiko, getpass, shutil, os.path
import passman
from ftplib import FTP

class CodingError(Exception):
    """
    Exceptions raised when an error occured during encoding or decoding
    of a manager.
    """
    pass

class Loader:
    """
    A Loader is used to save and load a PasswordManager from a file.
    Loader is an abstract class that should be overriden.
    """

    def save(self, manager, filename, passphrase=None):
        """
        Saves a PasswordManager in a file using an optional passphrase.
        This method is abstract and must be overriden.
        """
        pass

    def load(self, filename, passphrase=None):
        """
        Loads and returns a PasswordManager from a file using an optional
        passphrase.
        This method is abstract and must be overriden.
        """
        pass

class YAMLLoader(Loader):
    """
    A YAMLLoader stores and retrives the PasswordManager using YAML in a
    plain text file.
    """

    def save(self, manager, filename, passphrase=None):
        with open(filename, 'w') as f:
            yaml.dump(manager, f)

    def load(self, filename, passphrase=None):
        with open(filename) as f:
            return yaml.load(f)

class AESLoader(Loader):
    """
    An AESLoader stores and retrives the PasswordManager using YAML, bzip2 and
    AES-256-CBC (with OpenSSL) using a passphrase.
    """

    def save(self, manager, filename, passphrase=None):
        """
        Saves the manager from the filename using OpenSSL, bzip2 and YAML.
        Raises a CodingError if OpenSSL was unable to encode the file.
        """
        with open(filename, 'w') as f:
            cmd = "openssl aes-256-cbc -salt -pass pass:{}".format(passphrase)
            p = subprocess.Popen(shlex.split(cmd),
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            result = p.communicate(bz2.compress(yaml.dump(manager)))
            if not result[1]:
                f.write(result[0])
            else:
                raise CodingError

    def load(self, filename, passphrase=None):
        """
        Loads the manager from the filename using OpenSSL and YAML.
        Raises a CodingError if OpenSSL was unable to decode the file.
        """
        with open(filename) as f:
            cmd = "openssl aes-256-cbc -d -salt " + \
                  "-pass pass:{}".format(passphrase)
            p = subprocess.Popen(shlex.split(cmd),
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            result = p.communicate(f.read())
            if not result[1]:
                return yaml.load(bz2.decompress(result[0]))
            else:
                raise CodingError

class DistantLoader(Loader):
    """
    A DistantLoader is used to save and load a PasswordManager from a distant
    file.
    DistantLoader is an abstract class that should be overriden.
    """

    def __init__(self, loader):
        """
        Initializes the DistantLoader with the Loader to use to decode/encode
        the distant file.
        """
        self.loader = loader

    def get(self, filename):
        """
        Retrieves a distant file.
        This method is abstract and must be overriden.
        """
        pass

    def put(self, filename):
        """
        Uploads a distant file.
        This method is abstract and must be overriden.
        """
        pass

    def save(self, manager, filename, passphrase=None):
        """
        Saves a PasswordManager to a distant file using an optional passphrase
        and upload it to the distant location.
        The filename is used for the local temporary file.
        """
        self.loader.save(manager, filename, passphrase)
        self.put(filename)

    def load(self, filename, passphrase=None):
        """
        Retrieves, loads and returns a PasswordManager from a distant file
        using an optional passphrase.
        The filename is used for the local temporary file.
        """
        self.get(filename)
        return self.loader.load(filename, passphrase)


class FTPLoader(DistantLoader):
    """
    A FTPLoader is used to save and load a PasswordManager from a distant
    file stored on a FTP server.
    """

    def __init__(self, loader, dist_filename, host, user=None, passwd=""):
        """
        Initializes the DistantLoader with the Loader to use to decode/encode
        the distant file, a distant filename and with the connections
        parameters to use.
        """
        DistantLoader.__init__(self, loader)
        self.dist_filename = dist_filename
        self.host = host
        self.user = user
        self.passwd = passwd

    def connect(self):
        """
        Establish the connection with the remote server.
        """
        self.ftp = FTP(self.host, self.user, self.passwd)

    def get(self, filename):
        self.connect()
        with open(filename, 'w') as f:
            self.ftp.retrbinary('RETR {}'.format(self.dist_filename), f.write)
        self.ftp.close()

    def put(self, filename):
        self.connect()
        with open(filename) as f:
            self.ftp.storbinary('STOR {}'.format(self.dist_filename), f)
        self.ftp.close()

class SFTPLoader(DistantLoader):
    """
    A SFTPLoader is used to save and load a PasswordManager from a distant
    file stored on a SFTP (FTP over SSH) server.
    """

    def __init__(self, loader, dist_filename, host, port=22, user=None,
                 passwd=""):
        """
        Initializes the DistantLoader with the Loader to use to decode/encode
        the distant file, a distant filename and with the connections
        parameters to use.
        """
        DistantLoader.__init__(self, loader)
        self.dist_filename = dist_filename
        self.host = host
        self.port = port
        self.user = user if user else getpass.getuser()
        self.passwd = passwd
        self.get_hostkey()

    def get_hostkey(self):
        """
        Try to get the hostkey from ~/.ssh/known_hosts or ~/ssh/known_hosts.
        """
        self.hostkeytype = None
        self.hostkey = None
        try:
            path = os.path.expanduser("~")
            file = "known_hosts"
            join = os.path.join
            host_keys = paramiko.util.load_host_keys(join(path, ".ssh", file))
        except IOError:
            try:
                # for Windows
                host_keys = paramiko.util.load_host_keys(join(path, "ssh",
                                                              file))
            except IOError:
                host_keys = {}

        if host_keys.has_key(self.host):
            self.hostkeytype = host_keys[self.host].keys()[0]
            self.hostkey = host_keys[self.host][hostkeytype]

    def connect(self):
        """
        Establish the connection with the remote server.
        """
        t = paramiko.Transport((self.host, self.port))
        t.connect(username=self.user, password=self.passwd,
                  hostkey=self.hostkey)
        self.sftp = paramiko.SFTPClient.from_transport(t)

    def get(self, filename):
        self.connect()
        with open(filename, 'w') as f:
            fdist = self.sftp.open(self.dist_filename)
            shutil.copyfileobj(fdist, f)
            fdist.close()
        self.sftp.close()

    def put(self, filename):
        self.connect()
        with open(filename) as f:
            fdist = self.sftp.open(self.dist_filename, 'w')
            shutil.copyfileobj(f, fdist)
            fdist.close()
        self.sftp.close()
