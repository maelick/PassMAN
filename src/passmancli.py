#!/usr/bin/env python
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

import argparse
import sys
import shlex
try:
    import readline
except:
    pass

import actions


class ParserExitError(Exception):
    pass


class CLIParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)
        raise ParserExitError


class CLI:
    """This class is the command line interface with PassMAN. It
    parses command line arguments to manipulate PassMAN and to open
    the curses and GUI."""
    def __init__(self, interpreter=False):
        desc = "PassMAN Command Line Interface."
        self.interpreter = interpreter
        self.parser = CLIParser(description=desc)
        if not self.interpreter:
            self.parser.add_argument("-v", "--verbose", action="store_true",
                                     default=False, help="Verbose mode.")
            self.parser.add_argument("-c", "--conf",
                                     help="The configuration file to " + \
                                     "use (default is" + \
                                     "~/.passman/passman.yml or " + \
                                     "~/passman/passman.yml on M$ Windows).")
        title = "PassMAN-CLI Action"
        desc = "The action to do on the password database."
        help = "Use -h or --help with the action for more details."
        self.subparsers = self.parser.add_subparsers(title=title,
                                                     description=desc,
                                                     help=help,
                                                     metavar="action_name")

        self.add_command(Create())
        self.add_command(List())
        self.add_command(Add())
        self.add_command(Remove())
        self.add_command(AddTag())
        self.add_command(RemoveTag())
        self.add_command(Password())
        self.add_command(Generate())

    def add_command(self, command):
        """Adds a subparser to the general parser."""
        subparser = self.subparsers.add_parser(command.name,
                                               help=command.help)
        command.init(subparser)
        subparser.set_defaults(command=command)

    def start(self, args=None):
        """Parse the arguments of the script and runs the command
        passed as parameters if options are valid. Returns True if the
        command have been successfully run or if -h option has been
        used."""
        try:
            self.args = self.parser.parse_args(args)
        except ParserExitError:
            return False
        cmd = self.args.command
        if self.interpreter:
            self.args.verbose = True
        else:
            self.conf = actions.load_config(self.args.conf)
            self.loader = actions.load_loader(self.conf)
        cmd.args = self.args
        cmd.conf = self.conf
        cmd.loader = self.loader
        cmd.action()
        return True


class Command:
    """Abstract class used to represent a (sub)Command of the CLI.
    An instance of Command have a command name, a text help, a method
    to initialize the arguments of the (sub)Command and a callback action."""

    name = "comand" # The (sub)command's name. Must be overriden.
    help = "Command help" # The (sub)command's help text. Must be overriden.

    def init(self, subparser):
        """Initializes the (sub)Command arguments. Must be overriden."""
        pass

    def action(self):
        """Callback called when the (sub)Command is used. Must be
        overriden."""
        pass


class Create(Command):
    """Class used to represents the create Command which creates a new
    password database."""
    name = "create"
    help = "Creates a new password database."

    def init(self, subparser):
        Command.init(self, subparser)

    def action(self):
        actions.create_database(self.conf)
        actions.save_database(self.conf, self.loader)


class Save(Command):
    """Class used to represents the save Command which saves the
    password database."""
    name = "save"
    help = "Saves a new password database."

    def init(self, subparser):
        Command.init(self, subparser)

    def action(self):
        actions.save_database(self.conf, self.loader)


class List(Command):
    """Class used to represents the list Command which list password
    entries associated with a tag or filtered with regular
    expressions."""
    name = "list"
    help = "Lists the entries of the database."

    def init(self, subparser):
        Command.init(self, subparser)
        group = subparser.add_mutually_exclusive_group()
        group.add_argument("-t", "--tag",
                           help="The tag of the entries to list.")
        group.add_argument("-f", "--filter", nargs="+",
                           help="Regex used to filter the list to print.")
        subparser.add_argument("-e", "--entropy",
                               action="store_true",
                               help="Computes the entries entropy.")

    def action(self):
        actions.load_database(self.conf, self.loader)
        actions.list_entries(self.conf, self.args.filter, self.args.tag,
                             self.args.verbose, self.args.entropy)


class Add(Command):
    """Class used to represents the add Command which adds a new
    password entry in the database."""
    name = "add"
    help = "Adds an entry to the passwords database."

    def init(self, subparser):
        Command.init(self, subparser)
        subparser.add_argument("-g", "--generator", default=None,
                               help="The generator's name.")
        subparser.add_argument("-n", "--name", required=True,
                               help="The entry's name.")
        subparser.add_argument("-u", "--username", required=True)
        subparser.add_argument("--comment", default="")
        subparser.add_argument("--nonce", default="")
        subparser.add_argument("-l", "--length", type=int, default=0)
        subparser.add_argument("-e", "--entropy", type=float, default=0.)

    def action(self):
        actions.load_database(self.conf, self.loader)
        actions.add(self.conf, self.args.name, self.args.username,
                    self.args.comment, self.args.nonce, self.args.length,
                    self.args.entropy, self.args.generator)
        actions.save_database(self.conf, self.loader)


class Remove(Command):
    """Class used to represents the remove Command which removes a set
    of password entries associated with a tag or filtered with regular
    expressions."""

    name = "remove"
    help = "Removes one entry of the database."

    def init(self, subparser):
        Command.init(self, subparser)
        group = subparser.add_mutually_exclusive_group()
        group.add_argument("-t", "--tag",
                           help="The tag of the entries to remove.")
        group.add_argument("-f", "--filter", nargs="+",
                           help="Regex used to filter the list to print.")

    def action(self):
        actions.load_database(self.conf, self.loader)
        actions.remove(self.conf, self.args.filter, self.args.tag)
        actions.save_database(self.conf, self.loader)


class AddTag(Command):
    """Class used to represents the add_tag Command which adds a tag
    to a set of password entries associated with a tag or filtered
    with regular expressions."""

    name = "add_tag"
    help = "Adds a tag to the matching entries."

    def init(self, subparser):
        Command.init(self, subparser)
        group = subparser.add_mutually_exclusive_group()
        group.add_argument("-f", "--filter", nargs="+",
                           help="Regex used to filter the list to print.")
        subparser.add_argument("-t", "--tag", required=True,
                               help="The tag to add.")

    def action(self):
        actions.load_database(self.conf, self.loader)
        actions.add_tag(self.conf, self.args.filter, self.args.tag)
        actions.save_database(self.conf, self.loader)


class RemoveTag(Command):
    """Class used to represents the add_tag Command which removes a
    tag to a set of password entries associated with a tag or filtered
    with regular expressions."""

    name = "remove_tag"
    help = "Removes a tag from the matching entries."

    def init(self, subparser):
        Command.init(self, subparser)
        group = subparser.add_mutually_exclusive_group()
        group.add_argument("-f", "--filter", nargs="+",
                           help="Regex used to filter the list to print.")
        subparser.add_argument("-t", "--tag", required=True,
                               help="The tag to remove.")

    def action(self):
        actions.load_database(self.conf, self.loader)
        actions.remove_tag(self.conf, self.args.filter, self.args.tag)
        actions.save_database(self.conf, self.loader)


class Password(Command):
    """Class used to represents the password Command which generates
    the password for a password entry associated with a tag or
    filtered with regular expressions."""

    name = "password"
    help = "Gets the associated password of an entry."

    def init(self, subparser):
        Command.init(self, subparser)
        group = subparser.add_mutually_exclusive_group()
        group.add_argument("-t", "--tag",
                           help="The tag of the entries.")
        group.add_argument("-f", "--filter", nargs="+",
                           help="Regex used to filter the list of entries.")
        subparser.add_argument("-i", "--index", type=int, default=0,
                                help="The index of the entry in the " + \
                                "tag/filtered list.")
        subparser.add_argument("--clipboard", action="store_true",
                                help="Copy password to system clipboard " + \
                                "instead of printing it to stdout.")

    def action(self):
        actions.load_database(self.conf, self.loader)
        actions.password(self.conf, self.args.filter, self.args.tag,
                         self.args.index, self.args.clipboard,
                         self.args.verbose)


class Generate(Command):
    """Class used to represents the generate Command which a
    pseudo-random password using one of PassMAN's generators."""

    name = "generate"
    help = "Generates a random strong password."

    def init(self, subparser):
        Command.init(self, subparser)
        subparser.add_argument("-g", "--generator",
                                default=None,
                                help="The generator's name.")
        subparser.add_argument("-l", "--length", type=int, default=0,
                                help="The minimum password's length " +
                                "(see configuration file for default).")
        subparser.add_argument("-e", "--entropy", type=float, default=None,
                                help="The minimum password's entropy.")
        subparser.add_argument("--clipboard", action="store_true",
                                help="Copy password to system clipboard " + \
                                "instead of printing it to stdout.")

    def action(self):
        actions.load_database(self.conf, self.loader)
        actions.generate(self.conf, self.args.generator, self.args.length,
                         self.args.entropy, self.args.clipboard,
                         self.args.verbose)


class GUI(Command):
    """Class used to represents the gui Command which opens the GUI."""

    name = "gui"
    help = "Opens the GUI."

    def init(self, subparser):
        pass

    def action(self):
        pass


class Interpreter(Command):
    """Class used to represents the interpreter Command which starts a
    loop to enter Commands on stdin."""

    name = "interpreter"
    help = "Starts a loop to enter Commands on stdin."

    def get_parser(self):
        parser = CLI(True)
        parser.conf = self.conf
        parser.loader = self.loader
        parser.add_command(Save())
        return parser

    def action(self):
        running = True
        while running:
            try:
                args = raw_input(">> ")
            except (EOFError, KeyboardInterrupt):
                running = False
            else:
                cmd = shlex.split(args)
                self.get_parser().start(cmd)


def main():
    cli = CLI()
    cli.add_command(GUI())
    cli.add_command(Interpreter())
    cli.start()
    print
    return 0

if __name__ == "__main__":
    sys.exit(main())
