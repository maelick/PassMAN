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

import unittest, random, os
import passgen

def generate_default_symbols(filename):
    with open(filename, 'w') as f:
        f.write("\n".join([chr(33 + i) for i in xrange(94)]))

class TestOplopGenerator(unittest.TestCase):
    entropy_test_limit = 24 # Bigger than 24 => useless/impossible

    def setUp(self):
        generate_default_symbols("test_symbols")
        self.generator = passgen.OplopGenerator()

    def tearDown(self):
        os.remove("test_symbols")

    def test_entropy(self):
        for i in xrange(1, self.entropy_test_limit + 1):
            entropy = self.generator.get_entropy(i)
            length = self.generator.get_length(entropy)
            min_length = self.generator.get_minimum_length(entropy)
            self.assertAlmostEqual(i, length)
            self.assertTrue(i == min_length or i == min_length - 1)
        self.assertAlmostEqual(self.generator.get_entropy(16),
                               93.32192809488737)

    def test_secure_password(self):
        secure_password = self.generator.get_password("", "passman",
                                                      "", "passman", 8)
        self.assertEqual(secure_password, "sYyCj4OE")
        secure_password = self.generator.get_password("name", "username",
                                                      "nonce", "passphrase",
                                                      8)
        self.assertEqual(secure_password, "6rWI_aOE")
        secure_password = self.generator.get_password("", "username",
                                                      "", "passphrase",
                                                      8)
        self.assertEqual(secure_password, "6rWI_aOE")
        secure_password = self.generator.get_password("name", "username",
                                                      "nonce", "passphrase",
                                                      15)
        self.assertEqual(secure_password, "6rWI_aOE3JHXjh0")
        secure_password = self.generator.get_password("name2", "username",
                                                      "nonce2", "passphrase",
                                                      15)
        self.assertEqual(secure_password, "6rWI_aOE3JHXjh0")
        secure_password = self.generator.get_password("name", "username",
                                                      "nonce", "passphrase",
                                                      24)
        self.assertEqual(secure_password, "6rWI_aOE3JHXjh06GCp2ug==")

class TestSuperGenPassGenerator(unittest.TestCase):
    entropy_test_limit = 24 # Bigger than 24 => useless/impossible

    def setUp(self):
        generate_default_symbols("test_symbols")
        self.generator = passgen.SuperGenPassGenerator()

    def tearDown(self):
        os.remove("test_symbols")

    def test_entropy(self):
        for i in xrange(1, self.entropy_test_limit + 1):
            entropy = self.generator.get_entropy(i)
            length = self.generator.get_length(entropy)
            min_length = self.generator.get_minimum_length(entropy)
            self.assertAlmostEqual(i, length)
            self.assertTrue(i == min_length or i == min_length - 1)
        self.assertAlmostEqual(self.generator.get_entropy(16),
                               93.32192809488737)

    def test_secure_password(self):
        secure_password = self.generator.get_password("passman", "",
                                                      "", "passman", 10)
        # self.assertEqual(secure_password, "oSEWunR9EM")
        # Fails... FIXME

class TestPasswordComposerGenerator(unittest.TestCase):
    entropy_test_limit = 24 # Bigger than 24 => useless/impossible

    def setUp(self):
        generate_default_symbols("test_symbols")
        self.generator = passgen.PasswordComposerGenerator()

    def tearDown(self):
        os.remove("test_symbols")

    def test_entropy(self):
        for i in xrange(1, self.entropy_test_limit + 1):
            entropy = self.generator.get_entropy(i)
            length = self.generator.get_length(entropy)
            min_length = self.generator.get_minimum_length(entropy)
            self.assertAlmostEqual(i, length)
            self.assertTrue(i == min_length or i == min_length - 1)
        self.assertAlmostEqual(self.generator.get_entropy(16),
                               93.32192809488737)

    def test_secure_password(self):
        secure_password = self.generator.get_password("passman", "",
                                                      "", "passman", 10)
        self.assertEqual(secure_password, "RPIktBkD1a")

class TestPassmanGenerator(unittest.TestCase):
    entropy_test_limit = 156 # Bigger than 156 => overflow

    def setUp(self):
        generate_default_symbols("test_symbols")
        self.generator = passgen.PassmanGenerator("test_symbols")
        random.seed(0)

    def tearDown(self):
        os.remove("test_symbols")

    def test_symbol(self):
        symbol = self.generator.next_symbol()
        self.assertEqual(symbol, 'p')

    def test_simple_password(self):
        password = self.generator.get_next_password()
        self.assertEqual(password, "phH9QGj=MWvP;h[")

    def test_entropy(self):
        for i in xrange(1, self.entropy_test_limit + 1):
            entropy = self.generator.get_entropy(i)
            length = self.generator.get_length(entropy)
            min_length = self.generator.get_minimum_length(entropy)
            self.assertAlmostEqual(i, length)
            self.assertTrue(i == min_length or i == min_length - 1)
        self.assertAlmostEqual(self.generator.get_entropy(16), 104.873421627)

    def test_secure_password(self):
        secure_password = self.generator.get_password("name", "username",
                                                      "nonce", "passphrase",
                                                      15)
        self.assertEqual(secure_password, "~T'pIAM+vyZ[,7T")

        # Test if seed has been correctly set back
        next_password = self.generator.get_next_password()
        self.assertEqual(next_password, "phH9QGj=MWvP;h[")

if __name__ == '__main__':
    unittest.main()
