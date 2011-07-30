#-*- coding: utf-8 -*-

import yaml, subprocess, shlex, re
import passgen

class PasswordEntry(yaml.YAMLObject):
    """
    A PasswordEntry is an entry for a password in the manager.
    It has a username, a site (name and URL), a length
    and an optional comment. The site name and the username are used
    to generate the password, so if they change the password will change too.
    An optional additional salt can also be used to generate the password.
    Each entry is associated with a category of entries.
    The entry is also identified by the kind of generator (symbols set and
    hash algorithm).
    """
    yaml_tag = u'!PasswordEntry'
    def __init__(self, username, site, url, comment="", salt="", length=15,
                 category="Main", generator=None):
        """
        Initializes the entry with the parameters.
        The generator must be a string representation of a
        passgen.PasswordGenerator. If it is None, a default generator will be
        used.
        """
        self.username = username
        self.site = site
        self.url = url
        self.length = length
        self.comment = comment
        self.salt = salt
        self.category = category
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

    def match(self, keywords):
        """
        Returns True if this entry website name, url, username, salt or
        comment match any of the keywords of the list passed as argument.
        The keywords can be regular expressions.
        """
        for k in keywords:
            regex = re.compile(k, re.I)
            if not re.findall(regex, self.username) and \
               not re.findall(regex, self.site) and \
               not re.findall(regex, self.url) and \
               not re.findall(regex, self.comment) and \
               not re.findall(regex, self.salt):
                return False
        return True

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

    def get_entry(self, title, category="Main"):
        """
        Retrieves the PasswordEntry of a given title and category.
        """
        return self.passwords[category][title]

    def get_entries(self, category):
        """
        Retrieves all the PasswordEntries of a given category
        """
        return self.passwords[category]

    def add_entry(self, entry):
        """
        Adds a PasswordEntry.
        """
        category = entry.category
        if self.passwords.has_key(category):
            self.passwords[category][entry.title] = entry
        else:
            self.passwords[category] = {entry.title: entry}

    def delete_entry(self, entry):
        """
        Removes a PasswordEntry.
        """
        category = entry.category
        del self.passwords[category][entry.title]
        if len(self.passwords[category]) == 0:
            del self.passwords[category]

    def change_category(self, entry, category):
        """
        Changes the category of an entry
        """
        self.delete_entry(entry)
        entry.category = category
        self.add_entry(entry)

    def get_catogories(self):
        """
        Returns the list of all the categories of PasswordEntries
        """
        return self.passwords.keys()

    def filter_entries(self, keywords, categories=None):
        """
        Returns a subset of the entries where the site title, username, url,
        salt or comment matches all the keywords (list of regular
        expressions).
        It is possible to filter entries from only a subset of categories.
        """
        if categories is None:
            categories = self.get_categories()
        for cat in categories:
            entries.append(self.get_entries(cat).values())
        return [e for e in entries if e.match(keywords)]

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
