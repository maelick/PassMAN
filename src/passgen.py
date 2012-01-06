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

import random, hashlib, yaml, math, base64, os.path, re

class PasswordGenerator:
    """
    A PasswordGenerator is an object used to generate a pseudo-random
    password which can be secure.
    It allows to generate a simple pseudo-random password or a password
    generated with a seed based on the hash of a passphrase. This is used by
    Password objects to get a password based on a site, username and a master
    passphrase to retrieve a password without storing it anywhere on disk.
    This class is abstract and subclasses implement different algorithms.
    """
    yaml_tag = u'!PasswordGenerator'

    def get_entropy(self, length):
        """
        Returns the entropy for a given length.
        This is an abstract method that needs to be overriden.
        """
        pass

    def get_minimum_length(self, entropy):
        """
        Returns the length to have password for a minimum entropy.
        """
        return int(math.ceil(self.get_length(entropy)))

    def get_length(self, entropy):
        """
        Returns the length to have password with a given entropy.
        This is an abstract method that needs to be overriden.
        """
        pass

    def get_next_password(self, n=15):
        """
        Returns the next password given of length n (15 by default) by
        the generator.
        This is an abstract method that needs to be overriden.
        """
        pass

    def get_random_password(self, n=15):
        """
        Returns a random password of length n (15 by default).
        This method is cryptographically secure as the random seed used for
        password generation is obtained with os.urandom function to get entropy
        from the system and generates 1024 bits sequence used as seed.
        """
        state = random.getstate()
        seed = os.urandom(1024)
        random.seed(seed)
        password = self.get_next_password(n)
        random.setstate(state)
        return password

    def get_password(self, name, username, nonce, passphrase):
        """
        Returns the next secure password of length n given by the generator
        depending of the passphrase, name, username and nonce.
        This is an abstract method that needs to be overriden.
        """
        pass

class PassmanGenerator(PasswordGenerator):
    """
    A PasswordGenerator is an object used to generate a pseudo-random
    password which can be secure.
    It allows to generate a simple pseudo-random password or a password
    generated with a seed based on the hash (SHA-512 by default) of a
    passphrase. This is used by Password objects to get a password based
    on a site, username and a master passphrase to retrieve a password without
    storing it anywhere on disk.
    """
    yaml_tag = u'!PassmanGenerator'

    def __init__(self, filename, algo="sha512", sep=""):
        """
        Initializes the generator with:
          * the name of the file with each line containing each symbol
          * the hash algorithm name (default is SHA-512)
        The result of the secure password will depend of the symbols order
        in the file.
        """
        self.filename = filename
        with open(filename) as f:
            self.symbols = [l.strip() for l in f.readlines()
                            if len(l.strip()) > 0]
        self.sep = sep
        self.algo = algo

    def get_entropy(self, length):
        """
        Returns the entropy for a given length.
        """
        return math.log(len(self.symbols) ** length, 2)

    def get_length(self, entropy):
        """
        Returns the length to have password for a given entropy.
        """
        return math.log(2 ** entropy, len(self.symbols))

    def next_symbol(self):
        """
        Returns the next symbol given by the generator.
        """
        return random.choice(self.symbols)

    def get_next_password(self, n=15):
        """
        Returns the next password given of length n (15 by default) by
        the generator.
        """
        return self.sep.join((self.next_symbol() for i in xrange(n)))

    def get_password(self, name, username, nonce, passphrase, n):
        """
        Returns the next secure password of length n given by the generator
        depending of the passphrase, name, username and nonce.
        """
        state = random.getstate()
        string = name + username + nonce + passphrase
        seed = hashlib.new(self.algo, string).digest()
        random.seed(seed)
        password = self.get_next_password(n)
        random.setstate(state)
        return password

    def __eq__(self, other):
        """
        Returns true if both objects are the same PasswordGenerator (using
        the same symbols and same algorithm).
        """
        if isinstance(other, self.__class__):
            return self.symbols == other.symbols and \
                   self.sep == other.sep and self.algo == other.algo
        else:
            return True

class OplopGenerator(PasswordGenerator):
    """
    Generates passwords using the Oplop's algorithm
    (http://code.google.com/p/oplop/wiki/HowItWorks).
    The canonical algorithm uses a length of 8 for passwords. This
    implementation can use any arbitrary length/entropy.
    """
    yaml_tag = u'!OplopGenerator'

    def get_entropy(self, length):
        """
        Returns the entropy for a given length.
        """
        return math.log(64 ** (length - 1) * 10, 2)

    def get_length(self, entropy):
        """
        Returns the length to have password for a given entropy.
        """
        return math.log(2 ** entropy / 10., 64) + 1

    def get_next_password(self, n=8):
        """
        Returns the next password given of length n (8 by default) by
        the generator.
        """
        username = "".join([chr(33 + random.randrange(94)) \
                            for i in xrange(n)])
        passphrase = "".join([chr(33 + random.randrange(94)) \
                              for i in xrange(n)])
        return self.get_password("", username, "", passphrase, n)

    def get_password(self, name, username, nonce, passphrase, n=8):
        """
        Returns the next secure password of length n given by the generator
        depending of the passphrase and username.
        """
        md5 = hashlib.md5()
        md5.update(passphrase)
        md5.update(username)
        md5 = base64.urlsafe_b64encode(md5.digest())
        found = re.search(r"\d+", md5)
        if not found:
            md5 = '1' + md5
        elif found.start() >= n:
            md5 = found.group() + md5
        return md5[:n]

class SuperGenPassGenerator(PasswordGenerator):
    yaml_tag = u'!SuperGenPassGenerator'
    pass

class PasswordComposerGenerator(PasswordGenerator):
    yaml_tag = u'!PasswordComposerGenerator'
    pass

class GeneratorManager:
    """
    A GeneratorManager is used to manage the different PasswordGenerators.
    It's main use is for loading into memory only PassmanGenerators that are
    needed. It still loads Oplop, SuperGenPass and PasswordComposer managers.
    """
    yaml_tag = u'!GeneratorManager'

    def __init__(self, directory):
        """
        Initializes the manager with the path name of the directory which
        contains the symbol's size for the PassmanGenerators.
        """
        self.directory = directory
        self.generators = {
            "oplop": OplopGenerator(),
            "supergenpass": SuperGenPassGenerator(),
            "passwordcomposer": PasswordComposerGenerator()
            }

    def get_generator(self, name):
        """
        Returns the generator with his name.
        oplop, supergenpass and passwordcomposer is used for their respective
        generator.
        For PassmanGenerators, the name is the hash algorithm's name and
        the symbol's filename separated by a colon.
        For example, "sha512:ascii" will use SHA-512 as the hash algorithm
        and the ascii file containing 94 usable ASCII characters.
        """
        if name == "oplop" or name == "supergenpass" or \
               name == "passwordcomposer":
            return self.generators[name]
        else:
            if name not in self.generators:
                algo, filename = name.split(":", 1)
                sep = " " if filename.startswith("diceware") else ""
                filename = os.path.join(self.directory, filename)
                self.generators[name] = PassmanGenerator(filename, algo, sep)
            return self.generators[name]
