Documentation for developpers
=============================

PassMAN algorithm
-----------------

PassMAN uses mainly two algorithm to generate a password. The first
one is the algorithm used to generate a password based on a seed and a
dictionary (i.e. a set of symbols). The second one is used to get the
same seed for a given hash algorithm, username, site, nounce and
passphrase for each password entry.

The first algorithm simply uses Python built-in pseudo-random number
generator which is a Mersene Twister generator
(https://en.wikipedia.org/wiki/Mersenne_twister) to pick each
symbol. This means that the ordering of symbols in the dictionary is
important and must not change. This means that the generation of the
password cannot occur in a threaded environnement using the same
generator withtout locks.

The seed is generated like this:

- concatenate site name, username, nonce and passphrase;
- compute hash (default is SHA-512);
- compute Python seed with built-in seed function to get an integer.



Architecture
------------

Core Architecture
.................

PassMAN core architecture is organised around four modules:

- :py:mod:`passgen` containing password generators implementations and
  password generator manager.
- :py:mod:`passman` containing structures for the password
  database/manager.
- :py:mod:`loader` used to load and save database with YAML, AES.
- :py:mod:`actions` is a set of functions that do different actions on
  the password database like listing entries, adding entries,
  generating passwords, etc.

Password generation
*******************

Password generators are implemented using an abstract class
:py:class:`~passgen.PasswordGenerator`. Methods that needs to be
overridden are the one giving the entropy for a given length
(:py:class:`~passgen.PasswordGenerator.get_entropy`), the one giving
the length for a given entropy
(:py:class:`~passgen.PasswordGenerator.get_length`), the one returning
the next random password
(:py:class:`~passgen.PasswordGenerator.get_next_password`) and the one
returning the password for a given site name, username, nonce and
passphrase
(:py:class:`~passgen.PasswordGenerator.get_password`). Currently
subclasses of :py:class:`~passgen.PasswordGenerator` are
:py:class:`~passgen.PassmanGenerator` and
:py:class:`~passgen.OplopGenerator`. Future implementation are
:py:class:`~passgen.SuperGenPassGenerator` and
:py:class:`~passgen.PasswordComposerGenerator`.

Password generator management
*****************************

PasswordGenerator is used to load generators on demand and to provide
an easy way to use access to them. It loads at object creation oplop,
SuperGenPass and Password Composer generators. Then it can load on
demand any PassMAN generator needed. This is done using the method
:py:meth:`~passgen.GeneratorManager.get_generator`. The method returns
the generator depending of its name and loads it (with its dictionary
for PassMAN generators) if not already loaded.

Passwords management
********************

The management of passwords is achieved with
:py:class:`~passman.PasswordEntry` and
:py:class:`~passman.PasswordManager`. A password entry is an object
containing informations such as generator, site name, username, nonce,
comment, length, entropy and the list of tags associated with the
entry. The password manager maintains a list of theses entries, the
set of all tags available and the
:py:class:`~passgen.GeneratorManager`. The class provides methods to
get/filter entries and modify tags.

Database loading
****************

A :py:class:`~loader.Loader` is an object that provides a
:py:meth:`~loader.Loader.save` and a :py:meth:`~loader.Loader.load`
methods. These two methods save or load a
:py:class:`~passman.PasswordManager` from a file with an optional
passphrase (if encryption is applicable).

Two classes inherit from this class:

- :py:class:`~loader.YAMLLoader`: simple YAML loading of the database
  using no encryption with PyYAML.
- :py:class:`~loader.AESLoader`: YAML loading with AES encryption with
  OpenSSH.

CLI Architecture
................

Todo.

GUI Architecture
................

Not yet implemented.

Other modules
.............

Others module includes:
- :py:mod:`diceware` containing functions used for the diceware generator feature.
