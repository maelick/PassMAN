import unittest
from passman import PasswordEntry, PasswordManager

class TestPasswordEntry(unittest.TestCase):
    def setUp(self):
        self.entry = PasswordEntry("username", "site", "www.site.com",
                                   "Comment about the site", "Salt", 16)

    def test_password(self):
        p = self.entry.get_password()
        self.assertEqual(p.get_password("passphrase"), "2j!WSUch4qz?vSd{")

    def test_match(self):
        self.assertTrue(self.entry.match(["about"]))
        self.assertTrue(self.entry.match(["^www.*\\.com$"]))
        self.assertTrue(self.entry.match(["n.m"]))
        self.assertTrue(self.entry.match(["n.m", "^comMent"]))
        self.assertTrue(not self.entry.match(["nm", "abc"]))
        self.assertTrue(not self.entry.match(["nm", "site"]))

class TestPasswordManager(unittest.TestCase):
    def setUp(self):
        self.manager = PasswordManager()
        self.entry1 = PasswordEntry("username1", "site1", "www.site1.com",
                                    "Comment about the site", "Salt", 16)
        self.entry2 = PasswordEntry("username2", "site2", "www.site2.com",
                                    "No comment", "Salt2", 16)
        self.entry3 = PasswordEntry("username3", "site3", "www.site3.com")

    def test_get_entry(self):
        pass

    def test_get_entries(self):
        pass

    def test_add_entry(self):
        pass

    def test_delete_entry(self):
        pass

    def test_change_category(self):
        pass

    def test_get_categories(self):
        pass

    def filter_entries(self):
        pass

if __name__ == '__main__':
    unittest.main()
