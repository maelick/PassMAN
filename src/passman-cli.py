#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright 2011 Maëlick Claes <himself@maelick.net>
#
# This file is part of PassML.
#
# PassML is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PassML is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PassML.  If not, see <http://www.gnu.org/licenses/>.

import argparse, sys, yaml, os.path, getpass, subprocess, shlex
import loader, passman

class CLI:
    """
    This class is the command line interface with PassMAN.
    It parses command line arguments to manipulate PassMAN and to open
    the curses and GTK UI.
    """
    def __init__(self):
        self.loader = None
        self.init_parser()

    def init_parser(self):
        """
        Initialize the parser global options.
        """
        desc = "PassMAN Command Line Interface."
        parser = argparse.ArgumentParser(description=desc)
        parser.add_argument("-n", "--newdb",
                            action="store_true",
                            help="Creates a new password database file " + \
                            "instead of opening a new one.")
        parser.add_argument("-c", "--conf",
                            help="The configuration file to use (default " + \
                            "is ~/.passman/passman.conf).")
        self.parser = parser
        self.init_commands()

    def init_commands(self):
        """
        Initializes the commands subparsers.
        """
        title = "PassMAN-CLI Action"
        desc = "The action to do on the password database."
        help = "Use -h or --help with the action for more details."
        self.cmd_parsers = self.parser.add_subparsers(title=title,
                                                      description=desc,
                                                      help=help,
                                                      metavar="action_name")

        self.init_generate()
        self.init_retrieve()
        self.init_push()
        self.init_list()
        self.init_add()
        self.init_add_tag()
        self.init_remove_tag()
        self.init_remove()
        self.init_password()
        self.init_curses()
        self.init_gtk()

    def distant_options(self, parser):
        """
        Initializes the distant transfer options for a specified parser.
        """
        dtype_group = parser.add_mutually_exclusive_group()
        dtype_group.add_argument("--ftp",
                                 action="store_const",
                                 const="ftp",
                                 dest="dist_type",
                                 help="Retrieves/push the passwords " + \
                                 "database file from/to a FTP.")
        dtype_group.add_argument("--ssh",
                                 action="store_const",
                                 const="ssh",
                                 dest="dist_type",
                                 help="Retrieves/push the passwords " + \
                                 "database file using SSH.")

    def init_retrieve(self):
        """
        Initializes the retireve command subparser options.
        """
        help="Retrieves the distant passwords database."
        cmd_parser = self.cmd_parsers.add_parser("retrieve", help=help)
        cmd_parser.set_defaults(action=self.retrieve_action)
        self.distant_options(cmd_parser)

    def retrieve_action(self):
        """
        Function called when the retrieve command is passed as argument.
        """
        distant_loader = self.load_distant_loader()
        passphrase = self.conf["db"]["passphrase"] \
                     if self.conf["db"].has_key("passphrase") else None
        distant_loader.load(self.conf["db"]["filename"], passphrase)
        print "Database retrieved."

    def init_push(self):
        """
        Initializes the push command subparser options.
        """
        help="Pushes the distant passwords database."
        cmd_parser = self.cmd_parsers.add_parser("push", help=help)
        cmd_parser.set_defaults(action=self.push_action)
        self.distant_options(cmd_parser)

    def push_action(self):
        """
        Function called when the push command is passed as argument.
        """
        self.load_database()
        distant_loader = self.load_distant_loader()
        passphrase = self.conf["db"]["passphrase"] \
                     if self.conf["db"].has_key("passphrase") else None
        distant_loader.save(self.manager, self.conf["db"]["filename"],
                            passphrase)
        print "Database pushed."

    def init_list(self):
        """
        Initializes the list command subparser options.
        """
        help="Lists the entries of the database."
        cmd_parser = self.cmd_parsers.add_parser("list", help=help)
        cmd_parser.set_defaults(action=self.list_action)
        group = cmd_parser.add_mutually_exclusive_group()
        group.add_argument("-t", "--tag",
                           help="The tag of the entries to list.")
        group.add_argument("-f", "--filter",
                           help="Regexp used to filter the list to print.")
        cmd_parser.add_argument("--sep", default="|",
                                help="The separator used to define " +
                                "multiple regexp.")
        cmd_parser.add_argument("--entropy",
                                action="store_true",
                                help="Computes the entries entropy.")

    def list_action(self):
        """
        Function called when the list command is passed as argument.
        """
        self.load_database()
        if self.args.filter:
            keywords = self.args.filter.split(self.args.sep)
            entries = self.manager.filter(keywords)
        else:
            entries = self.manager.get_entries(self.args.tag)

        print "i) name (generator): username [(nonce)] [(comment)]: " + \
              "minimum length/entropy (tag list)"
        for i, e in enumerate(entries):
            if self.args.entropy:
                entropy = e.get_entropy(self.manager.generator_manager)
                s = "{}) {}/{}".format(i, e, entropy)
            else:
                s = "{}) {}".format(i, e)
            if e.tags:
                print "{} ({})".format(s, ", ".join(e.tags))
            else:
                print s

    def init_add(self):
        """
        Initializes the add command subparser options.
        """
        help="Adds an entry to the passwords database."
        cmd_parser = self.cmd_parsers.add_parser("add", help=help)
        cmd_parser.set_defaults(action=self.add_action)
        cmd_parser.add_argument("--generator", default=None,
                                help="The generator's name.")
        cmd_parser.add_argument("--name", required=True,
                                help="The entry's name.")
        cmd_parser.add_argument("--username", required=True)
        cmd_parser.add_argument("--comment", default="")
        cmd_parser.add_argument("--nonce", default="")
        cmd_parser.add_argument("--length", type=int, default=15)
        cmd_parser.add_argument("--entropy", type=int, default=None)

    def add_action(self):
        """
        Function called when the add command is passed as argument.
        """
        self.load_database()
        default_generator = self.conf["default_generator"]
        generator = self.args.generator if self.args.generator \
                    else default_generator
        entry = passman.PasswordEntry(generator, self.args.name,
                                      self.args.username, self.args.comment,
                                      self.args.nonce, self.args.length,
                                      self.args.entropy)
        self.manager.set_entry(entry)
        entry.get_password(self.manager.generator_manager, "")
        self.save_database()

    def init_add_tag(self):
        """
        Initializes the add_tag command subparser options.
        """
        help="Adds a tag to the matching entries."
        cmd_parser = self.cmd_parsers.add_parser("add_tag", help=help)
        cmd_parser.set_defaults(action=self.add_tag_action)
        group = cmd_parser.add_mutually_exclusive_group()
        group.add_argument("-f", "--filter",
                           help="Regexp used to filter the list to print.")
        cmd_parser.add_argument("--sep", default="|",
                                help="The separator used to define " +
                                "multiple regexp.")
        cmd_parser.add_argument("-t", "--tag", required=True,
                                help="The tag to add.")

    def add_tag_action(self):
        """
        Function called when the add_tag command is passed as argument.
        """
        self.load_database()
        if self.args.filter:
            keywords = self.args.filter.split(self.args.sep)
            entries = self.manager.filter(keywords)
        else:
            entries = self.manager.get_entries()

        for e in entries:
            self.manager.add_tag(e, self.args.tag)
        self.save_database()

    def init_remove_tag(self):
        """
        Initializes the remove_tag command subparser options.
        """
        help="Removes a tag from the matching entries."
        cmd_parser = self.cmd_parsers.add_parser("remove_tag", help=help)
        cmd_parser.set_defaults(action=self.remove_tag_action)
        group = cmd_parser.add_mutually_exclusive_group()
        group.add_argument("-f", "--filter",
                           help="Regexp used to filter the list to print.")
        cmd_parser.add_argument("--sep", default="|",
                                help="The separator used to define " +
                                "multiple regexp.")
        cmd_parser.add_argument("-t", "--tag", required=True,
                                help="The tag to add.")

    def remove_tag_action(self):
        """
        Function called when the remove_tag command is passed as argument.
        """
        self.load_database()
        if self.args.filter:
            keywords = self.args.filter.split(self.args.sep)
            entries = self.manager.filter(keywords)
        else:
            entries = self.manager.get_entries()

        for e in entries:
            self.manager.remove_tag(e, self.args.tag)
        self.save_database()

    def init_remove(self):
        """
        Initializes the remove command subparser options.
        """
        help="Removes one entry of the database."
        cmd_parser = self.cmd_parsers.add_parser("remove", help=help)
        cmd_parser.set_defaults(action=self.remove_action)
        group = cmd_parser.add_mutually_exclusive_group()
        group.add_argument("-t", "--tag",
                           help="The tag of the entries to list.")
        group.add_argument("-f", "--filter",
                           help="Regexp used to filter the list to print.")
        cmd_parser.add_argument("--sep", default="|",
                                help="The separator used to define " +
                                "multiple regexp.")

    def remove_action(self):
        """
        Function called when the remove command is passed as argument.
        """
        self.load_database()
        if self.args.filter:
            keywords = self.args.filter.split(self.args.sep)
            entries = self.manager.filter(keywords)
        else:
            entries = self.manager.get_entries(self.args.tag)
        for e in entries:
            self.manager.remove_entry(e)
        self.save_database()

    def copy2clipboard(self, password):
        """
        Copies a password into the system clipboard using a third party
        tool like xclip or xsel.
        """
        p = subprocess.Popen(shlex.split(self.conf["clipboard_cmdline"]),
                             stdin=subprocess.PIPE)
        p.communicate(password)

    def init_password(self):
        """
        Initializes the password command subparser options.
        """
        help="Gets the associated password of an entry."
        cmd_parser = self.cmd_parsers.add_parser("password", help=help)
        cmd_parser.set_defaults(action=self.password_action)
        group = cmd_parser.add_mutually_exclusive_group()
        group.add_argument("-t", "--tag",
                           help="The tag of the entries to list.")
        group.add_argument("-f", "--filter",
                           help="Regexp used to filter the list to print.")
        cmd_parser.add_argument("--sep", default="|",
                                help="The separator used to define " +
                                "multiple regexp.")
        cmd_parser.add_argument("-i", "--index", type=int, default=0,
                                help="The index of the entry in the " + \
                                "filtered list.")
        cmd_parser.add_argument("--clipboard", action="store_true",
                                help="Copy password to system clipboard " + \
                                "instead of printing it to stdout.")

    def password_action(self):
        """
        Function called when the password command is passed as argument.
        """
        self.load_database()
        if self.args.filter:
            keywords = self.args.filter.split(self.args.sep)
            entries = self.manager.filter(keywords)
        else:
            entries = self.manager.get_entries()

        entry = entries[self.args.index]
        print "Password for entry: {}".format(entry)
        prompt = "Please enter the master passphrase: "
        passphrase = getpass.getpass(prompt)
        password = entry.get_password(self.manager.generator_manager,
                                      passphrase)

        if self.args.clipboard:
            self.copy2clipboard(password)
        else:
            print password

    def init_generate(self):
        """
        Initializes the generate command subparser options.
        """
        help="Generates a random strong password."
        cmd_parser = self.cmd_parsers.add_parser("generate", help=help)
        cmd_parser.set_defaults(action=self.generate_action)
        cmd_parser.add_argument("-g", "--generator",
                                default=None,
                                help="The separator used to define " +
                                "multiple regexp.")
        cmd_parser.add_argument("--length", type=int, default=12,
                                help="The minimum password's length " +
                                "(default: 12).")
        cmd_parser.add_argument("--entropy", type=int, default=None,
                                help="The minimum password's entropy.")
        cmd_parser.add_argument("--clipboard", action="store_true",
                                help="Copy password to system clipboard " + \
                                "instead of printing it to stdout.")

    def generate_action(self):
        """
        Function called when the generate command is passed as argument.
        """
        self.load_database()
        manager = self.manager.generator_manager
        default_generator = self.conf["default_generator"]
        generator_name = self.args.generator if self.args.generator \
                         else default_generator
        generator = manager.get_generator(generator_name)

        if self.args.entropy:
            length = max(generator.get_minimum_length(self.args.entropy),
                         self.args.length)
        else:
            length = self.args.length
        entropy = generator.get_entropy(length)
        password = generator.get_random_password(length)
        print "Random password of length {} (entropy={}):".format(length,
                                                                  entropy)

        if self.args.clipboard:
            self.copy2clipboard(password)
        else:
            print password

    def init_curses(self):
        """
        Initializes the curses command subparser options.
        """
        help="Opens the curses UI."
        cmd_parser = self.cmd_parsers.add_parser("curses", help=help)
        cmd_parser.set_defaults(action=self.curses_action)

    def curses_action(self):
        """
        Function called when the curses command is passed as argument.
        Starts the curses UI.
        """
        print "curses"
        pass # TODO

    def init_gtk(self):
        """
        Initializes the gtk command subparser options.
        """
        help="Opens the GTK GUI."
        cmd_parser = self.cmd_parsers.add_parser("gtk", help=help)
        cmd_parser.set_defaults(action=self.gtk_action)

    def gtk_action(self):
        """
        Function called when the push command is passed as argument.
        Starts de GTK GUI.
        """
        print "gtk"
        pass # TODO

    def parse_args(self, args=None):
        """
        Parses the arguments.
        """
        self.args = self.parser.parse_args(args)

    def load_config(self):
        """
        Load the configuration from ~/.passman/passman.yml.
        """
        dir = os.path.join(os.path.expanduser("~"), ".passman")
        if sys.platform == "win32" and not os.path.exists(dir):
            dir = os.path.join(os.path.expanduser("~"), "passman")
        if not self.args.conf:
            self.args.conf = os.path.join(dir, "passman.yml")
        with open(self.args.conf) as f:
            self.conf = yaml.load(f)
        db_filename = os.path.expanduser(self.conf["db"]["filename"])
        self.conf["db"]["filename"] = db_filename
        self.conf["symbols_dir"] = os.path.expanduser(self.conf["symbols_dir"])

    def load_loader(self):
        """
        Loads the local loader.
        """
        if self.conf["db"]["format"] == "gpg":
            self.loader = loader.GPGLoader()
        elif self.conf["db"]["format"] == "aes":
            self.loader = loader.AESLoader()
        else:
            self.loader = loader.YAMLLoader()

    def load_distant_loader(self):
        """
        Loads the distant loader.
        """
        if not self.args.dist_type:
            self.args.dist_type = self.conf["default_distant"]
        if self.args.dist_type == "ftp":
            passwd = getpass.getpass("FTP password: ")
            return loader.FTPLoader(self.loader, self.conf["ftp"]["filename"],
                                    self.conf["ftp"]["host"],
                                    self.conf["ftp"]["username"], passwd)
        elif self.args.dist_type == "ssh":
            passwd = getpass.getpass("SSH password: ")
            return loader.SFTPLoader(self.loader, self.conf["ssh"]["filename"],
                                     self.conf["ssh"]["host"],
                                     self.conf["ssh"]["port"],
                                     self.conf["ssh"]["username"], passwd)

    def load_database(self):
        """
        Loads the (local) password database.
        """
        if self.args.newdb:
            self.manager = passman.PasswordManager(self.conf["symbols_dir"])
        else:
            passphrase = self.conf["db"]["passphrase"] \
                         if self.conf["db"].has_key("passphrase") else None
            self.manager = self.loader.load(self.conf["db"]["filename"],
                                            passphrase)

    def save_database(self):
        """
        Saves the (local) password database.
        """
        passphrase = self.conf["db"]["passphrase"] \
                     if self.conf["db"].has_key("passphrase") else None
        self.loader.save(self.manager, self.conf["db"]["filename"],
                         passphrase)

def main():
    cli = CLI()
    cli.parse_args()
    cli.load_config()
    cli.load_loader()
    cli.args.action()
    return 0

if __name__ == "__main__":
    sys.exit(main())
