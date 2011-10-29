#-*- coding: utf-8 -*-

import yaml, subprocess, shlex
import passman

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
    An AESLoader stores and retrives the PasswordManager using YAML and
    AES-256-CBC (with OpenSSL) using a passphrase.
    """

    def save(self, manager, filename, passphrase=None):
        """
        Saves the manager from the filename using OpenSSL and YAML.
        Raises a CodingError if OpenSSL was unable to encode the file.
        """
        with open(filename, 'w') as f:
            cmd = "openssl aes-256-cbc -salt -pass pass:{}".format(passphrase)
            p = subprocess.Popen(shlex.split(cmd),
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            result = p.communicate(yaml.dump(manager))
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
                return yaml.load(result[0])
            else:
                raise CodingError

class DistantLoader:
    """
    A DistantLoader is used to save and load a PasswordManager from a distant
    file.
    DistantLoader is an abstract class that should be overriden.
    """

    def __init__(self, filename, loader):
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
        The filename is used is used for the local temporary file.
        """
        self.loader.save(filename, passphrase)
        self.put(filename)

    def load(self, filename, passphrase=None):
        """
        Retrieves, loads and returns a PasswordManager from a distant file
        using an optional passphrase.
        The filename is used is used for the local temporary file.
        """
        self.get(filename)
        return self.load(filename, passphrase)
