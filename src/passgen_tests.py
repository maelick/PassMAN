import unittest, random
from passgen import PasswordGenerator, Password, parse

class TestPasswordGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = PasswordGenerator()
        random.seed(0)

    def test_symbol(self):
        symbol = self.generator.next_symbol()
        self.assertEqual(symbol, '[')

    def test_simple_password(self):
        password = self.generator.get_simple_password()
        self.assertEqual(password, "[(NyVL_CS2~UA(5")

    def test_secure_password(self):
        secure_password = self.generator.get_secure_password("test")
        self.assertEqual(secure_password, "k.)\L1{1%Cn>A+]")

        # Test if seed has been correctly set back
        simple_password = self.generator.get_simple_password()
        self.assertEqual(simple_password, "[(NyVL_CS2~UA(5")

    def test_str(self):
        string = "PasswordGenerator<sha512: abcdefghijklmnopqrstuvwxyz" + \
                 "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" + \
                 "!\"?$%^&*()_-+={}[]:;@'~#|\<,>./>"
        self.assertEqual(str(self.generator), string)

    def test_parse(self):
        generator = parse(str(self.generator))
        self.assertEqual(generator, self.generator)

class TestPassword(unittest.TestCase):
    def setUp(self):
        self.generator = PasswordGenerator()
        random.seed(0)

    def test_password(self):
        p = Password("site.com", "username", "salt", self.generator)
        result = p.get_password("passphrase")
        self.assertEqual(result, "u~/.8iK'+a2zRAG")
        self.assertEqual(len(result), 15)

        p = Password("site.com", "username", "salt", self.generator, 42)
        result = p.get_password("passphrase")
        self.assertEqual(len(result), 42)

if __name__ == '__main__':
    unittest.main()
