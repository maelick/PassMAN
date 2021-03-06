PassMAN
=======

https://github.com/maelick/PassMAN

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

If you find any bug, please report them on
https://github.com/maelick/PassMAN/issues



Features
--------

* Password generation based on differents algorithms and dictionaries
* Password management with tags and regex filters
* CLI interface to the database including commands: create, list, add,
  add_tag, remove_tag, remove, password, generate.
* CLI interpreter: entering a loop which avoid to load database each
  time. Additional database commands: save.
* YAML, AES and GPG for database serialization/encryption.
* YAML configuration file.
* Dictionaries included: diceware and diceware8k (de, en, fi, fr, it,
  nl, sv), latin alphabet, lowercase (nocase) latin alphabet,
  alphanumerical, base64 and ascii
* Diceware word list generation using most frequen words of a source
  text file.



REQUIRED
--------

* Python 2.7
* PyYAML
* OpenSSL for AES encryption
* PyGPGME for GPG encryption



INSTALLATION
------------

Put all the .py files from src folder where you want and optionally
create a symbolic link in a folder that is in your PATH variable. For
example:

    mkdir ~/passman
    cp src/*.py ~/passman
    ln -s ~/passman/passmancli.py ~/bin/passman

And in your ~/.bashrc (or equivalent):

    export $PATH="$PATH:$HOME/bin"

Put all the files from conf folder into ~/.passman. For example:

    cp -r conf ~/.passman

For Windows copy the .py where you want and create a link. Copy the
content of conf directory into ~/passman.

Installation scripts will be provided in future versions.



CONFIGURATION
-------------

Additional dictionaries can be added in ~/.passman/symbols.
~/.passman/passman.yml is the main configuration file and is encoded
with YAML.

Options for ~/.passman/passman.yml:

* default_generator: the default generator to use when generating
  random passwords or adding a new entry in the database. See below
  for more informations.
* symbols_dir: the directory in which the dictionaries are store.
* clipboard_cmdlin: the command to use to store a password into the
  clipboard. The password will be passed on the stdin of the command's
  process.
* default_password_length:
    * normal: default password length for normal passwords
    * diceware: default password length for diceware passwords
    * algorithm_name: default password for passwords generated with
      algorithm_name
* db:
    * filename: the filename of the local database file.
    * format: the format used to save the database. May be yaml, aes,
      gnupg. aes and gpg encryption also use bzip2 compression and
      YAML.
    * passphrase: encryption passphrase to use (optional and not
      recommended to use).



Generator name format
---------------------

A generator is identified by a string representation. It uses the
form: algo_name:dictionary. algo_name is the name of the hash
algorithm name (e.g. md5, sha256, sha512, etc). sha512 is recommended.
The dictonary is the dictionary filename. It may be a file containing
a character on each line or a list of words to be used as a diceware
(see http://www.diceware.com). In the last case, the file must start
with "diceware" otherwise there will be no space between words in the
resulting diceware password.

Additional "third-party" algorithms are (or will be) also impleted and
can be used by simply using their name.

Currently implemented third-party algorithms:

* oplop
* SuperGenPass
* Password Composer



Credits
-------

The software is licensed under the GNU General Public License v3, see
https://www.gnu.org/licenses/gpl-3.0.html or LICENSE file in source
archive.

Diceware lists get credits of their respective authors (see
http://world.std.com/~reinhold/diceware.html#languages).

Third-party algorithms are based on:

* http://code.google.com/p/oplop for oplop
* http://supergenpass.com/faq/#Technical-Details for SuperGenPassGenerator
* http://www.angel.net/~nic/passwd.sha1.1a.html for Password Composer
