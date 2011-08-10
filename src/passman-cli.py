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
        parser.add_argument("--db", required=True,
                                help="The database filename to use.")

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
                                help="Uses an AES-256-CBC encrypted YAML " + \
                                "file as password database.")
        type_group.add_argument("--gpg",
                                action="store_const",
                                const="gpg",
                                dest="db_type",
                                help="Uses a GPG encrypted YAML file as " + \
                                "password database.")

        pass_group = parser.add_mutually_exclusive_group()
        pass_group.add_argument("-a", "--askpassphrase",
                                action="store_true",
                                help="If specified, the password will " + \
                                "be asked in a secure way instead of " + \
                                "being provided in the command line.")
        pass_group.add_argument("-p", "--passphrase",
                                help="The passphrase to use for " + \
                                "encrypting and decrypting the password " + \
                                "database. Do not use if the file is " + \
                                "not encrypted.")

        parser.add_argument("-n", "--newdb",
                            action="store_true",
                            help="Creates a new password database file " + \
                            "instead of opening a new one.")
        self.parser = parser
        self.init_commands()

    def init_commands(self):
        title = "PassMAN-CLI Action"
        desc = "The action to do on the password database."
        help =  "Use -h or --help with the action for more details."
        self.commands_parser = self.parser.add_subparsers(title=title,
                                                          description=desc,
                                                          help=help,
                                                          metavar="action")
        self.init_generate()
        self.init_list()
        self.init_remove()
        self.init_password()

    def init_generate(self):
        help="Generates a random strong password."
        generate_parser = self.commands_parser.add_parser("generate",
                                                           help=help)
        self.action = self.generate_action

    def generate_action(self):
        pass # TODO

    def init_list(self):
        help="Lists (or filters) the entries of the database."
        list_parser = self.commands_parser.add_parser("list", help=help)
        self.action = self.list_action

    def list_action(self):
        pass # TODO

    def init_remove(self):
        help="Removes one entry of the database."
        remove_parser = self.commands_parser.add_parser("remove", help=help)
        self.action = self.remove_action

    def remove_action(self):
        pass # TODO

    def init_password(self):
        help="Gets the associated password of an entry."
        password_parser = self.commands_parser.add_parser("password",
                                                          help=help)
        self.action = self.password_action

    def password_action(self):
        pass # TODO

    def parse_args(self):
        self.args = self.parser.parse_args()

    def load_database(self):
        if self.args.db_type == "gpg":
            self.loader = loader.GPGLoader()
        elif self.args.db_type == "aes":
            self.loader = loader.AESLoader()
        else:
            self.loader = loader.YAMLLoader()

        if self.args.newdb:
            self.manager = passman.PasswordManager()
        else:
            self.manager = self.loader.load(args.db)

def main():
    cli = CLI()
    cli.parse_args()
    cli.load_database()
    cli.action()
    return 0

if __name__ == "__main__":
    sys.exit(main())
