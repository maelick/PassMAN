import unittest, random, os
from passgen import PassmanGenerator, OplopGenerator

def generate_default_symbols(filename):
    with open(filename, 'w') as f:
        f.write("\n".join([chr(33 + i) for i in xrange(94)]))

class TestOplopGenerator(unittest.TestCase):
    entropy_test_limit = 24 # Bigger than 24 => useless/impossible

    def setUp(self):
        generate_default_symbols("test_symbols")
        self.generator = OplopGenerator()

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

class TestPassmanGenerator(unittest.TestCase):
    entropy_test_limit = 156 # Bigger than 156 => overflow

    def setUp(self):
        generate_default_symbols("test_symbols")
        self.generator = PassmanGenerator("test_symbols")
        random.seed(0)

    def tearDown(self):
        os.remove("test_symbols")

    def test_symbol(self):
        symbol = self.generator.next_symbol()
        self.assertEqual(symbol, 'p')

    def test_simple_password(self):
        password = self.generator.get_simple_password()
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
        self.assertEqual(secure_password, "{H~Won5+t@oN\\Qf")

        # Test if seed has been correctly set back
        simple_password = self.generator.get_simple_password()
        self.assertEqual(simple_password, "phH9QGj=MWvP;h[")

if __name__ == '__main__':
    unittest.main()
