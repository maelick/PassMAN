#-*- coding: utf-8 -*-

import yaml, re
import passgen

class PasswordEntry(yaml.YAMLObject):
    """
    A PasswordEntry is an entry for a password in the manager.
    It has a name, a username, a nonce, a length and an optional comment.
    The name, the username and the nonce are used to generate the password,
    so if they change the password will change too.
    Each entry is associated with a set of tags.
    The entry is also identified by the kind of generator (symbols set and
    hash algorithm).
    It is possible to define either the length or the minimum entropy.
    By default uses a length of 15.
    """
    yaml_tag = u'!PasswordEntry'

    def __init__(self, generator, name, username, comment="", nonce="",
                 length=15, entropy=None, tags=set()):
        """
        Initializes the entry with the parameters.
        It is possible to define a minimum entropy, in this case the required
        minimum length will be also computed.
        """
        self.generator = generator
        self.name = name
        self.username = username
        self.nonce = nonce
        self.comment = comment
        self.length = length
        self.entropy = entropy
        self.tags = tags

    def get_password(self, generator_manager, passphrase):
        """
        Returns the Password object that can generate the password for this
        entry using a given generator_manager and a passphrase.
        """
        generator = generator_manager.get_generator(self.generator)
        if self.entropy:
            self.length = max(generator.get_minimum_length(self.entropy),
                              self.length)
            self.entropy = None
        return generator.get_password(self.name, self.username, self.nonce,
                                      passphrase, self.length)

    def get_entropy(self, generator_manager):
        """
        Returns the entropy of the password generated by this entry using
        a given generator_manager.
        """
        generator = generator_manager.get_generator(self.generator)
        return max(generator.get_entropy(self.length), self.entropy)

    def __hash__(self):
        return 0

    def __eq__(self, other):
        return isinstance(other, PasswordEntry) and \
               self.name == other.name

    def match_re(self, regex):
        """
        Returns True if the regular expression passed as parameter matches
        this entry name, username, nonce comment or a tag.
        """
        for s in ([self.name, self.username, self.nonce, self.comment] +
                  list(self.tags)):
            if re.findall(regex, s):
                return True
        return False

    def match(self, keywords):
        """
        Returns True if this entry name, username, nonce, comment or a tag
        matches all of the keywords of the list passed as argument.
        The keywords are treated as regular expressions.
        """
        for k in keywords:
            if not self.match_re(re.compile(k, re.I)):
                return False
        return True

class PasswordManager(yaml.YAMLObject):
    """
    A PasswordManager maintains lists of PasswordEntry objects that can be
    grouped with tags.
    """
    yaml_tag = u'!PasswordManager'

    def __init__(self, directory):
        """
        Initializes an empty manager.
        """
        self.passwords = set()
        self.tags = set()
        self.generator_manager = passgen.GeneratorManager(directory)

    def compute_tags(self):
        """
        Find the tags used associated with at least one entry.
        """
        self.tags.clear()
        for p in self.passwords:
            for t in p.tags:
                self.tags.add(t)

    def get_entries(self, tag=None):
        """
        Returns the list of PasswordEntries. It is possible to specify a tag
        to get only the entries associated with this tag.
        """
        if tag is None:
            return list(self.passwords)
        else:
            return [e for e in self.passwords if tag in e.tags]

    def add_entry(self, entry):
        """
        Adds a PasswordEntry.
        """
        self.passwords.add(entry)

    def remove_entry(self, entry):
        """
        Removes a PasswordEntry.
        """
        self.passwords.remove(entry)
        self.compute_tags()

    def set_entry_tags(self, entry, tags):
        """
        Modifies the tags of an entry.
        """
        entry.tags = tags
        self.compute_tags()

    def get_tags(self):
        """
        Returns the list of all the tags.
        """
        return list(self.tags)

    def filter(self, keywords):
        """
        Returns a subset of the entries where the name, username,
        nonce or tags matches all the keywords (list of regular
        expressions).
        """
        return [e for e in self.passwords if e.match(keywords)]
