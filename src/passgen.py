#-*- coding: utf-8 -*-

import random, hashlib, yaml

default_symbols = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" + \
                  "0123456789!\"?$%^&*()_-+={}[]:;@'~#|\<,>./"

class PasswordGenerator(yaml.YAMLObject):
    """
    A PasswordGenerator is an object used to generate a pseudo-random
    password which can be secure.
    It allows to generate a simple pseudo-random password or a password
    generated with a seed based on the hash (SHA-512 by default) of a
    passphrase. This is used by Password objects to get a password based
    on a site, username and a master passphrase to retrieve a password without
    storing it anywhere on disk.
    """
    yaml_tag = u'!PasswordGenerator'
    def __init__(self, symbols=default_symbols, algo="sha512"):
        """
        Initializes the generator with a string containing the symbols
        used by the generator and using an algorithm name for the hash
        function.
        The result of the secure password will depend on the order of the
        symbols in the string.
        The default algorithm is SHA-512
        """
        self.symbols = symbols
        self.algo = algo

    def next_symbol(self):
        """
        Returns the next symbol given by the generator.
        """
        return random.choice(self.symbols)

    def get_simple_password(self, n=15):
        """
        Returns the next password given of length n (15 by default) by
        the generator.
        """
        return ''.join((self.next_symbol() for i in xrange(n)))

    def get_secure_password(self, passphrase, n=15):
        """
        Returns the next secure password of length n (15 by default) given
        by the generator depending of the passphrase.
        """
        state = random.getstate()
        seed = hashlib.new(self.algo, passphrase).digest()
        random.seed(seed)
        password = self.get_simple_password(n)
        random.setstate(state)
        return password

    def __eq__(self, other):
        """
        Returns true if both objects are the same PasswordGenerator (using
        the same symbols and same algorithm).
        """
        if isinstance(other, self.__class__):
            return self.symbols == other.symbols and self.algo == other.algo
        else:
            return True

    def __str__(self):
        """
        Returns a string representing this PasswordGenerator.
        The string representation looks like
        PasswordGenerator<algo: symbols> where algo is the algorithm
        naame and symbols is the set of symbols.
        """
        return "PasswordGenerator<{}: {}>".format(self.algo, self.symbols)

def parse(generator):
    """
    Parses a string which represents a PasswordGenerator looking like the
    string representation of the object.
    """
    algo, symbols = generator.split("<", 1)[1].split(":", 1)
    algo = algo.strip()
    symbols = symbols.rsplit(">", 1)[0].strip()
    return PasswordGenerator(symbols, algo)

class Password:
    """
    A Password represents a password used for a username, for a
    given site, a length and using a specified generator.
    It can use a salt which is an additional string (that can be empty)
    used to generate the password.
    The passwordis is retrieved based on a passphrase.
    """
    def __init__(self, site, salt, username, generator, n=15):
        """
        Initializes the password with the site, salt, username, generator
        and length (which is 15 by default).
        """
        self.site = site
        self.salt = salt
        self.username = username
        self.generator = generator
        self.length = n

    def get_password(self, passphrase):
        """
        Returns the password using the passphrase.
        """
        passphrase = self.site + self.salt + self.username + passphrase
        return self.generator.get_secure_password(passphrase, self.length)
