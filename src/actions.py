#-*- coding: utf-8 -*-
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

import getpass
import subprocess
import shlex
import os.path
import sys
import yaml

import loader
import passman
import diceware

def load_config(filename=None):
    """Load the configuration."""
    if not filename:
        directory = os.path.join(os.path.expanduser("~"), ".passman")
        if sys.platform == "win32" and not os.path.exists(dir):
            directory = os.path.join(os.path.expanduser("~"), "passman")
        filename = os.path.join(directory, "passman.yml")
    with open(filename) as f:
        conf = yaml.load(f)
    db_filename = os.path.expanduser(conf["db"]["filename"])
    conf["db"]["filename"] = db_filename
    conf["symbols_dir"] = os.path.expanduser(conf["symbols_dir"])
    return conf


def load_loader(conf):
    """Load the database loader."""
    if conf["db"]["format"] == "gpg":
        return loader.GPGLoader()
    elif conf["db"]["format"] == "aes":
        return loader.AESLoader()
    elif conf["db"]["format"] == "yaml":
        return loader.YAMLLoader()
    else:
        raise ValueError("Unknown database format")


def get_password(conf):
    """Get the password's password database"""
    if conf["db"]["format"] in ["yaml"]:
        return None
    elif "passphrase" in conf["db"]:
        return conf["db"]["passphrase"]
    prompt = "Please enter the password's password database: "
    passphrase = getpass.getpass(prompt)
    conf["db"]["passphrase"] = passphrase
    return passphrase


def create_database(conf):
    """Create a new password database"""
    conf["database"] = passman.PasswordManager(conf["symbols_dir"])


def load_database(conf, loader):
    """Load the password database."""
    if "database" not in conf:
        filename = conf["db"]["filename"]
        if not os.path.exists(filename):
            raise ValueError("password database does not exist")
        if os.path.isdir(filename):
            raise ValueError("password database is not a regular file")
        passphrase = get_password(conf)
        entries = loader.load(conf["db"]["filename"], passphrase)
        create_database(conf)
        conf["database"].passwords = entries
        conf["database"].compute_tags()


def save_database(conf, loader):
    """Save the password database."""
    passphrase = get_password(conf)
    loader.save(conf["database"].passwords,
                conf["db"]["filename"], passphrase)


def list_entries(conf, filter=None, tag=None, verbose=False,
                 print_entropy=False):
    """List entries of a password database.
    - *conf* is a configuration dict
    - *filter* is an optional non empty list of regexp
    - *tag* is a tag (not used if filter is given)
    - *verbose* and *print_entropy* are booleans flag"""
    if filter:
        if type(filter) != list:
            raise TypeError, "filter must be a list of regexp"
        entries = conf["database"].filter(filter)
    else:
        if tag and not isinstance(tag, basestring):
            raise TypeError, "tag must be a string"
        entries = conf["database"].get_entries(tag)

    if verbose:
        print "i) name (generator): username [(nonce)]: " + \
              "[(comment)] length/entropy (tag list)"
    for i, e in enumerate(entries):
        if print_entropy:
            entropy = e.get_entropy(conf["database"].generator_manager)
            s = "{}) {} (entropy={:.2f})".format(i, e, entropy)
        else:
            s = "{}) {}".format(i, e)
        if e.tags:
            print "{} ({})".format(s, ", ".join(e.tags))
        else:
            print s


def get_entropy_length(conf, generator, entropy, length):
    if entropy:
        manager = conf["database"].generator_manager
        generator_inst = manager.get_generator(generator)
        return max(generator_inst.get_minimum_length(entropy), length)
    elif length:
        return length
    elif conf["default_password_length"].has_key(generator):
        return conf["default_password_length"][generator]
    elif generator.split(":")[1].startswith("diceware"):
        return conf["default_password_length"]["diceware"]
    else:
        return conf["default_password_length"]["normal"]


def add(conf, name, username, comment="", nonce="",
        length=0, entropy=0., generator=None):
    """Add an entry to a password database.
    - *conf* is a configuration dict
    - *name* is the entry name
    - *username* is the user name
    - *comment* is an optional entry comment
    - *nonce* is the optional nonce
    - *length* is the minimum length (if 0, retrieved from configuration)
    - *generator* is the generator (if None, retrieved from configuration)"""
    generator = generator if generator else conf["default_generator"]
    length = get_entropy_length(conf, generator, entropy, length)
    entry = passman.PasswordEntry(generator, name,
                                  username, comment,
                                  nonce, length)
    conf["database"].set_entry(entry)
    entry.get_password(conf["database"].generator_manager, "")


def remove(conf, filter=None, tag=None):
    """Remove a set of entries from a password database
    - *conf* is a configuration dict
    - *filter* is an optional non empty list of regexp
    - *tag* is a tag (not used if filter is given)"""
    if filter:
        if type(filter) != list:
            raise TypeError, "filter must be a list of regexp"
        entries = conf["database"].filter(filter)
    else:
        if tag and not isinstance(tag, basestring):
            raise TypeError, "tag must be a string"
        entries = conf["database"].get_entries(tag)

    for e in entries:
        conf["database"].remove_entry(e)


def add_tag(conf, filter=None, tag=None):
    """Add a tag to a set of password entries.
    - *conf* is a configuration dict
    - *filter* is an optional non empty list of regexp"""
    if filter:
        if type(filter) != list:
            raise TypeError, "filter must be a list of regexp"
        entries = conf["database"].filter(filter)
    else:
        entries = conf["database"].get_entries()

    for e in entries:
        conf["database"].add_tag(e, tag)


def remove_tag(conf, filter=None, tag=None):
    """Remove a tag to a set of password entries.
    - *conf* is a configuration dict
    - *filter* is an optional non empty list of regexp"""
    if filter:
        if type(filter) != list:
            raise TypeError, "filter must be a list of regexp"
        entries = conf["database"].filter(filter)
    else:
        entries = conf["database"].get_entries()

    for e in entries:
        conf["database"].remove_tag(e, tag)


def copy2clipboard(conf, password):
    """
    Copies a password into the system clipboard using a third party
    tool like xclip or xsel.
    """
    p = subprocess.Popen(shlex.split(conf["clipboard_cmdline"]),
                         stdin=subprocess.PIPE)
    p.communicate(password)


def gen_password(conf, entry, clipboard=False, verbose=False):
    if verbose:
        print "Password for entry: {}".format(entry)
    prompt = "Please enter the master passphrase: "
    passphrase = getpass.getpass(prompt)
    password = entry.get_password(conf["database"].generator_manager,
                                  passphrase)

    if clipboard:
        copy2clipboard(conf, password)
    else:
        print password


def password(conf, filter=None, tag=None, index=0,
             clipboard=False, verbose=False):
    """Get the password of an entry
    - *conf* is a configuration dict
    - *filter* is an optional non empty list of regexp
    - *tag* is a tag (not used if filter is given)
    - *index* the index of the entry in the set of entries
    - *clipboard* if True will store password in clipboard
    - *verbose* verbose mode if True"""
    if filter:
        if type(filter) != list:
            raise TypeError, "filter must be a list of regexp"
        entries = conf["database"].filter(filter)
    else:
        if tag and not isinstance(tag, basestring):
            raise TypeError, "tag must be a string"
        entries = conf["database"].get_entries(tag)

    entry = entries[index]
    gen_password(conf, entry, clipboard, verbose)


def quick_password(conf, generator, name, username, comment, nonce,
                   length, entropy, clipboard=False, verbose=False):
    """Make an entry (without saving it) and generates a password
    - *conf* is a configuration dict
    - *generator*, *name*, *username*, *comment*, *nonce*, *length* and
      *entropy* are directly passed to the PasswordEntry constructor
    - *clipboard* if True will store password in clipboard
    - *verbose* verbose mode if True"""
    generator = generator if generator else conf["default_generator"]
    length = get_entropy_length(conf, generator, entropy, length)
    entry = passman.PasswordEntry(generator, name,
                                  username, comment,
                                  nonce, length)
    gen_password(conf, entry, clipboard, verbose)
    if verbose:
        manager = conf["database"].generator_manager
        generator = manager.get_generator(generator)
        entropy = generator.get_entropy(length)
        print "Entropy: {}".format(entropy)


def generate(conf, generator, length=0, entropy=0,
             clipboard=False, verbose=False):
    """Generate a password
    - *conf* is a configuration dict
    - *generator* is the generator (if None, retrieved from configuration)
    - *length* is the minimum length (if 0, retrieved from configuration)
    - *clipboard* if True will store password in clipboard
    - *verbose* if True verbose mode"""
    manager = conf["database"].generator_manager
    generator_name = generator if generator else conf["default_generator"]
    generator = manager.get_generator(generator_name)

    length = get_entropy_length(conf, generator, entropy, length)
    entropy = generator.get_entropy(length)
    password = generator.get_random_password(length)
    if verbose:
        print "Random password of length {} (entropy={}):".format(length,
                                                                  entropy)

    if clipboard:
        copy2clipboard(conf, password)
    else:
        print password


def make_diceware(src_filename, n, min_length, out_filename=None):
    """Make a diceware using a source text and choosing most frequent
    words
    - *src_filename* is the name of the source file
    - *n* is the maximal number of words of the diceware
    - *min_length* is the minimal length of each words
    - *out_filename* if given, the diceware is written to this file"""
    text = diceware.load_file(src_filename)
    wc = diceware.make_word_count(diceware.filter_text(text))
    dw = diceware.make_diceware(wc, n, min_length)
    dw.sort(key=len)
    print len(dw)
    if out_filename:
        diceware.write_diceware(dw, out_filename)
    return dw
