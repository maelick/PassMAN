#!/usr/bin/env python
#-*- coding: utf-8 -*-

import argparse, sys
import loader, passman

class CLI:
    def __init__(self):
        self.loader = None
        self.init_parser()

    def init_parser(self):
        desc = "PassMAN Command Line Interface."
        parser = argparse.ArgumentParser(description=desc)
        parser.add_argument("--db",
                            help="The passwords database filename to use." + \
                            "If not provided, will use configuration " + \
                            "file ~/.passman/passman.conf")

        type_group = parser.add_mutually_exclusive_group()
        type_group.add_argument("--yaml",
                                action="store_const",
                                const="yaml",
                                dest="db_type",
                                help="Uses an unencrypted YAML file as " + \
                                "password database (default).")
        type_group.add_argument("--aes",
                                action="store_const",
                                const="aes",
                                dest="db_type",
                                help="Uses an AES-256-CBC encrypted and " + \
                                "compressed YAML file as passwords database.")
        type_group.add_argument("--gpg",
                                action="store_const",
                                const="gpg",
                                dest="db_type",
                                help="Uses a GPG encrypted and compressed " + \
                                "YAML file as passwords database.")

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

        parser.add_argument("--host",
                            help="The server's host.")
        parser.add_argument("-p", "--port",
                            action="store_true",
                            help="The port to use to access the server.")
        parser.add_argument("-u", "--username",
                            help="The username to use to access the " + \
                            "server.")
        parser.add_argument("-f", "--file",
                            help="The distant file to retrieve/push " + \
                            "the database from/to.")

        parser.add_argument("-n", "--newdb",
                            action="store_true",
                            help="Creates a new password database file " + \
                            "instead of opening a new one.")
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
        print "retrieve"
        pass # TODO

    def init_push(self):
        help="Pushes the distant passwords database."
        cmd_parser = self.cmd_parsers.add_parser("push", help=help)
        cmd_parser.set_defaults(action=self.push_action)

    def push_action(self):
        self.loader.save(self.manager, self.args.db)
        print "Push completed."
        pass # TODO

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

    def load_database(self):
        if self.args.db_type == "gpg":
            self.loader = loader.GPGLoader()
        elif self.args.db_type == "aes":
            self.loader = loader.AESLoader()
        else:
            self.loader = loader.YAMLLoader()

        if self.args.dist_type == "ftp":
            self.loader = loader.FTPLoader(self.loader, self.args.file,
                                           self.args.host,
                                           self.args.username, "")
        elif self.args.dist_type == "ssh":
            pass # TODO

        if self.args.newdb:
            self.manager = passman.PasswordManager(".")
        elif self.args.db:
            self.manager = self.loader.load(self.args.db)
        else:
            self.manager = None

def main():
    cli = CLI()
    cli.parse_args()
    cli.load_database()
    cli.args.action()
    return 0

if __name__ == "__main__":
    sys.exit(main())
