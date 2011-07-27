#-*- coding: utf-8 -*-

import yaml, subprocess, shlex
import passgen

class PasswordEntry(yaml.YAMLObject):
    """
    A PasswordEntry is an entry for a password in the manager.
    It has a username, a site (name and URL), a length
    and an optional comment. The site name and the username are used
    to generate the password, so if they change the password will change too.
    An optional additional salt can also be used to generate the password.
    The entry is also identified by the kind of generator (symbols set and
    hash algorithm).
    """
    yaml_tag = u'!PasswordEntry'
    def __init__(self, username, site, url, length=15,
                 comment="", salt="", generator=None):
        """
        Initializes the entry with the parameters.
        """
        self.username = username
        self.site = site
        self.url = url
        self.length = length
        self.comment = comment
        self.salt = salt
        if generator is None:
            self.generator = passgen.PasswordGenerator()
        else:
            self.generator = passgen.parse(generator)

    def get_password(self):
        """
        Returns the Password object that can generate the password for this
        entry.
        """
        return passgen.Password(self.site, self.salt, self.username,
                                self.generator, self.length)

    def __str__(self):
        return "PasswordEntry<{} on site {}>".format(self.username, self.site)

class PasswordManager(yaml.YAMLObject):
    """
    A PasswordManager maintains lists of PasswordEntry objects that can be
    grouped in categories and identified by a title for a better organisation.
    """
    yaml_tag = u'!PasswordManager'
    def __init__(self):
        """
        Initializes an empty manager.
        """
        self.passwords = {}

    def get_password(self, title, category="Main"):
        """
        Retrieves the PasswordEntry of a given title and category.
        """
        return self.passwords[category][title]

    def set_password(self, password, title, category="Main"):
        """
        Modifies the PasswordEntry of a given title and category.
        """
        if self.passwords.has_key(category):
            self.passwords[category][title] = password
        else:
            self.passwords[category] = {title: password}

    def delete_password(self, password, title, category="Main"):
        """
        Removes the PasswordEntry of a given title and category.
        """
        del self.passwords[category][title]
        if len(self.passwords[category]) == 0:
            del self.passwords[category]

def save(manager, filename, passphrase):
    """
    Saves a PasswordManager in a file with YAML and AES-256-CBC (with openssl)
    using a passphrase.
    """
    cmd = "openssl aes-256-cbc -salt -out {} -pass pass:{}".format(filename,
                                                                   passphrase)
    p = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE)
    p.communicate(yaml.dump(manager))

def load(filename, passphrase):
    """
    Loads and returns a PasswordManager from a file with YAML and AES-256-CBC
    (with openssl) using a passphrase.
    """
    cmd = "openssl aes-256-cbc -d -salt " + \
          "-in {} -pass pass:{}".format(filename, passphrase)
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
    result = p.communicate()[0]
    return yaml.load(result)
