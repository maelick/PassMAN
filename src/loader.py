#-*- coding: utf-8 -*-
#
# Copyright 2011 Maëlick Claes <himself@maelick.net>
#
# This file is part of PassMAN.
#
# PassMAN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PassMAN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PassMAN.  If not, see <http://www.gnu.org/licenses/>.

import yaml
import subprocess
import shlex
import bz2
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
