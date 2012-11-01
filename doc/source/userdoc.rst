Documentation for users
=======================

Introduction
------------

PassMAN is a password mannager that aims to be secure without storing
any passwords on disk. This is achieved by using a hash function over
a set of informations and a master passphrase to generate a near
unique password for each websites. It is similar to other softwares
like oplop (http://code.google.com/p/oplop) or SuperGenPass
(http://supergenpass.com).

PassMAN stores a database containing for each site an entry with a
name, a username, a nonce, a comment, a length or an entropy and some
tags. The password is generated using a concatenation of the name, the
username, the nonce and the master passphrase that keeps most of the
secret. The comment is used as a memo to keep additional informations
about the entry and the length/(bit) entropy is used to control the
strength of the passwords. Tags are used to easily filter the list of
entries.

Although it doesn't contain any password, the resulting database can
be encrypted using AES-256 or GnuPG.

If you find any bug, please report it on
https://bugs.launchpad.net/passman



Features
--------

- Password generation based on differents algorithms and dictionaries
- Password management with tags and regex filters
- CLI interface to the database including commands: create, list, add,
  add_tag, remove_tag, remove, password, generate.
- CLI interpreter: entering a loop which avoid to load database each
  time. Additional database commands: save.
- YAML, AES and GPG for database serialization/encryption.
- YAML configuration file.
- Dictionaries included: diceware and diceware8k (de, en, fi, fr, it,
  nl, sv), latin alphabet, lowercase (nocase) latin alphabet,
  alphanumerical, base64 and ascii



Required libraries and softwares
--------------------------------

- Python 2.7
- PyYAML
- OpenSSL for AES encryption
- PyGPGME for GPG encryption



Installation
------------

Put all the .py files from src folder where you want and optionally
create a symbolic link in a folder that is in your PATH variable. For
example:

.. code-block:: bash

  mkdir ~/passman
  cp src/*.py ~/passman
  ln -s ~/passman/passmancli.py ~/bin/passman

And in your ~/.bashrc (or equivalent):

.. code-block:: bash

  export $PATH="$PATH:$HOME/bin"

Put all the files from conf folder into ~/.passman. For example:

.. code-block:: bash

  cp -r conf ~/.passman

For Windows copy the .py where you want and create a link. Copy the
content of conf directory into ~/passman.

Installation scripts will be provided in future versions.



Configuration
-------------

Additional dictionaries can be added in ~/.passman/symbols.
~/.passman/passman.yml is the main configuration file and is encoded
with YAML.

Options for ~/.passman/passman.yml:

- default_generator: the default generator to use when generating
  random passwords or adding a new entry in the database. See below
  for more informations.
- symbols_dir: the directory in which the dictionaries are store.
- clipboard_cmdlin: the command to use to store a password into the
  clipboard. The password will be passed on the stdin of the command's
  process.
- default_password_length:
    - normal: default password length for normal passwords
    - diceware: default password length for diceware passwords
    - algorithm_name: default password for passwords generated with
      algorithm_name
- db:
    - filename: the filename of the local database file.
    - format: the format used to save the database. May be yaml, aes,
      gnupg. aes and gpg encryption also use bzip2 compression and
      YAML.
    - passphrase: encryption passphrase to use (optional and not
      recommended to use).



Generator name format
---------------------

A generator is identified by a string representation. It uses the
form: algo_name:dictionary. algo_name is the name of the hash
algorithm name (e.g. md5, sha256, sha512, etc). sha512 is
recommended. The dictonary is the dictionary filename. It may be a
file containing a character on each line or a list of words to be used
as a diceware (see http://www.diceware.com). In the last case, the
file must start with "diceware" otherwise there will be no space
between words in the resulting diceware password.

Additional "third-party" algorithms are (or will be) also impleted and
can be used by simply using their name.

Currently implemented third-party algorithms:

- oplop



CLI Usage
---------

The general help for the command line interface can be seen directly
with the -h option.

General usage is:

.. code-block:: bash

   passman [global options] subcommand [action options]

Global options are:

- -h or --help: display the help.
- -v: verbose mode, display additional informations.
- -c CONF or --conf CONF: specify the configuration file to use.
  Default: ~/.passman/passman.yml

The subcommand is one of the following:

- create
- list
- add
- remove
- add_tag
- remove_tag
- password
- generate
- interpreter
- gui

Create
......

Retrieve the distant password database. Options are:

- -h, --help: display the help.

List subcommand
...............

List all the entries, entries matching a tag or entries matching one
or multiple regex. Options are:

- -h, --help: display the help.
- -t TAG or --tag TAG: the tag of the entries to list.
- -f FILTERS or --filter FILTERS: a list of regex to use to filter
   entries.
- -e, --entropy: computes and display entries entropy.

Add subcommand
..............

Add a new entry to the database. Options are:

- -h, --help: display the help.
- -g GENERATOR, --generator GENERATOR: the generator/algorithm name to
   use.
- -n, --name NAME: the name to give to the entry.
- -u, --username USERNAME: the user's name.
- --comment COMMENT: an optional comment/memo text for the entry.
- --nonce: an optional text filed used to generate the password (only
  used with PassMAN algorithm).
- -l, --length LENGTH: the minimum length of the resulting password
  (see configuration file for default)
- -e --entropy ENTROPY: the minimum entropy of the password.

Remove subcommand
.................

Remove multiple entries matching a tag or filters. Options are:

- -h, --help: display the help.
- -t TAG or --tag TAG: the tag of the entries to remove.
- -f FILTERS or --filter FILTERS: a list of regex to use to filter
   entries.

Add tag subcommand
..................

Adds a tag to multiple entries matching filters. Options are:

- -h, --help: display the help.
- -f FILTERS or --filter FILTERS: a list of regex to use to filter
   entries.
- -t TAG or --tag TAG: the tag to add.

Remove tag subcommand
.....................

Remove a tag from multiple entries matching filters. Options are:

- -h, --help: display the help.
- -f FILTERS or --filter FILTERS: a list of regex to use to filter
   entries.
- -t TAG or --tag TAG: the tag to remove.

Password subcommand
...................

Get the associated password of an entry. Options are:

- -h, --help: display the help.
- -t TAG or --tag TAG: the tag of the entries.
- -f FILTERS or --filter FILTERS: a list of regex to use to filter
   entries.
- -i INDEX or --index INDEX: the index of the entry to get the
  password from the tag/filtered list.
- --clipboard: copy password to clipboard instead of printing it to
    stdout.

Generate subcommand
...................

Generate a random password using an algorithm implemented in
PassMAN. Options are:

- -h, --help: display the help.
- -g GENERATOR, --generator GENERATOR: the generator/algorithm name to
   use.
- -l, --length LENGTH: the minimum length of the resulting password
  (see configuration file for default)
- -e, --entropy ENTROPY: the minimum entropy of the password.
- -n: The number of passwords to generate.
- --clipboard: copy password to clipboard instead of printing it to
    stdout.

Interpreter subcommand
......................

Starts a loop to enter Commands on stdin. Commands are the same than
CLI's subcommands. However database is not automatically saved and
must be saved with command "save".

GUI subcommand
..............

Start the GUI. Not implemented yet.



Credits
-------

The software is licensed under the GNU General Public License v3, see
https://www.gnu.org/licenses/gpl-3.0.html or LICENSE file in source
archive.

Diceware lists get credits of their respective authors (see
http://world.std.com/~reinhold/diceware.html#languages).

Third-party algorithms are based on:

- http://code.google.com/p/oplop for oplop
