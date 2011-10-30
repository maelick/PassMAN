#!/usr/bin/env python
#-*- coding: utf-8 -*-

import argparse, sys, yaml, os.path
import loader, passman

class CLI:
    def __init__(self):
        self.loader = None
        self.init_parser()

    def init_parser(self):
        desc = "PassMAN Command Line Interface."
        parser = argparse.ArgumentParser(description=desc)

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

    def init_generate(self):
        help="Generates a random strong password."
        cmd_parser = self.cmd_parsers.add_parser("generate", help=help)
        cmd_parser.set_defaults(action=self.generate_action)

    def generate_action(self):
        print "generate"
        pass # TODO

    def init_retrieve(self):
        help="Retrieves the distant passwords database."
        cmd_parser = self.cmd_parsers.add_parser("retrieve", help=help)
        cmd_parser.set_defaults(action=self.retrieve_action)

    def retrieve_action(self):
        distant_loader = self.load_distant_loader()
        distant_loader.load(self.conf["db"]["filename"])
        print "Database retrieved."

    def init_push(self):
        help="Pushes the distant passwords database."
        cmd_parser = self.cmd_parsers.add_parser("push", help=help)
        cmd_parser.set_defaults(action=self.push_action)

    def push_action(self):
        self.load_database()
        distant_loader = self.load_distant_loader()
        distant_loader.save(self.manager, self.conf["db"]["filename"])
        print "Database pushed."

    def init_list(self):
        help="Lists (or filters) the entries of the database."
        cmd_parser = self.cmd_parsers.add_parser("list", help=help)
        cmd_parser.set_defaults(action=self.list_action)

    def list_action(self):
        print "list"
        pass # TODO

    def init_add(self):
        help="Adds an entry to the passwords database."
        cmd_parser = self.cmd_parsers.add_parser("add", help=help)
        cmd_parser.set_defaults(action=self.add_action)

    def add_action(self):
        print "add"
        pass # TODO

    def init_add_tag(self):
        help="Adds a tag to the matching entries."
        cmd_parser = self.cmd_parsers.add_parser("add_tag", help=help)
        cmd_parser.set_defaults(action=self.add_tag_action)

    def add_tag_action(self):
        print "add_tag"
        pass # TODO

    def init_remove_tag(self):
        help="Removes a tag from the matching entries."
        cmd_parser = self.cmd_parsers.add_parser("remove_tag", help=help)
        cmd_parser.set_defaults(action=self.remove_tag_action)

    def remove_tag_action(self):
        print "remove_tag"
        pass # TODO

    def init_remove(self):
        help="Removes one entry of the database."
        cmd_parser = self.cmd_parsers.add_parser("remove", help=help)
        cmd_parser.set_defaults(action=self.remove_action)

    def remove_action(self):
        print "remove"
        pass # TODO

    def init_password(self):
        help="Gets the associated password of an entry."
        cmd_parser = self.cmd_parsers.add_parser("password", help=help)
        cmd_parser.set_defaults(action=self.password_action)

    def password_action(self):
        print "password"
        pass # TODO

    def init_curses(self):
        help="Opens the curses UI."
        cmd_parser = self.cmd_parsers.add_parser("curses", help=help)
        cmd_parser.set_defaults(action=self.curses_action)

    def curses_action(self):
        print "curses"
        pass # TODO

    def init_gtk(self):
        help="Opens the GTK GUI."
        cmd_parser = self.cmd_parsers.add_parser("gtk", help=help)
        cmd_parser.set_defaults(action=self.gtk_action)

    def gtk_action(self):
        print "gtk"
        pass # TODO

    def parse_args(self, args=None):
        self.args = self.parser.parse_args(args)

    def load_config(self):
        dir = os.path.join(os.path.expanduser("~"), ".passman")
        if not self.args.conf:
            self.args.conf = os.path.join(dir, "passman.conf")
        with open(self.args.conf) as f:
            self.conf = yaml.load(f)
        db_filename = os.path.expanduser(self.conf["db"]["filename"])
        self.conf["db"]["filename"] = db_filename
        self.conf["symbols_dir"] = os.path.expanduser(self.conf["symbols_dir"])

    def load_loader(self):
        if self.conf["db"]["format"] == "gpg":
            self.loader = loader.GPGLoader()
        elif self.conf["db"]["format"] == "aes":
            self.loader = loader.AESLoader()
        else:
            self.loader = loader.YAMLLoader()

    def load_distant_loader(self):
        if not self.args.dist_type:
            self.args.dist_type = self.conf["default_distant"]
        if self.args.dist_type == "ftp":
            passwd = "MElz1Ous"
            return loader.FTPLoader(self.loader, self.conf["ftp"]["filename"],
                                    self.conf["ftp"]["host"],
                                    self.conf["ftp"]["username"], passwd)
        elif self.args.dist_type == "ssh":
            pass # TODO

    def load_database(self):
        if self.args.newdb:
            self.manager = passman.PasswordManager(self.conf["symbols_dir"])
        else:
            self.manager = self.loader.load(self.conf["db"]["filename"])

def main():
    cli = CLI()
    cli.parse_args()
    cli.load_config()
    cli.load_loader()
    cli.args.action()
    return 0

if __name__ == "__main__":
    sys.exit(main())
