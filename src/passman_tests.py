import unittest
from passman import PasswordEntry, PasswordManager

class TestPasswordEntry(unittest.TestCase):
    def setUp(self):
        self.entry = PasswordEntry("username", "site", "www.site.com",
                                   "Comment about the site", "Salt", 16)

    def test_password(self):
        p = self.entry.get_password()
        self.assertEqual(p.get_password("passphrase"), "2j!WSUch4qz?vSd{")

    def test_title(self):
        self.assertEqual(self.entry.title(), "site: username")

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
                                    "Comment about the site", "Salt", 16,
                                    "Category 1")
        self.entry2 = PasswordEntry("username2", "site2", "www.site2.com",
                                    "No comment", "Salt2", 16, "Category 2")
        self.entry3 = PasswordEntry("username3", "site3", "www.site3.com")

    def test_add_entry(self):
        self.manager.add_entry(self.entry1)
        self.manager.add_entry(self.entry2)
        self.manager.add_entry(self.entry3)
        self.assertTrue(True)

    def test_get_entry(self):
        self.test_add_entry()
        self.assertEqual(self.manager.get_entry("site1: username1",
                                                "Category 1"), self.entry1)
        self.assertEqual(self.manager.get_entry("site2: username2",
                                                "Category 2"), self.entry2)
        self.assertEqual(self.manager.get_entry("site3: username3"),
                         self.entry3)

    def test_get_entries(self):
        self.test_add_entry()
        self.assertEqual(self.manager.get_entries("Category 1"),
                         {"site1: username1": self.entry1})
        self.assertEqual(self.manager.get_entries("Category 2"),
                         {"site2: username2": self.entry2})
        self.assertEqual(self.manager.get_entries("Main"),
                         {"site3: username3": self.entry3})

    def test_get_all_entries(self):
        self.test_add_entry()
        entries = self.manager.get_all_entries()
        self.assertEqual(len(entries), 3)

    def test_remove_entry(self):
        self.test_add_entry()
        self.manager.remove_entry(self.entry1)
        self.manager.remove_entry(self.entry2)
        self.manager.remove_entry(self.entry3)
        self.assertEqual(self.manager.passwords, {})

    def test_change_category(self):
        self.test_add_entry()
        self.manager.change_category(self.entry1, "Main")
        self.assertEqual(len(self.manager.get_entries("Main")), 2)

    def test_get_categories(self):
        self.test_add_entry()
        categories = self.manager.get_categories()
        self.assertTrue(self.entry1.category in categories)
        self.assertTrue(self.entry2.category in categories)
        self.assertTrue(self.entry3.category in categories)
        self.assertEqual(len(categories), 3)

    def filter_entries(self):
        self.test_add_entry()
        self.assertEqual(self.manager.filter(["1"]), [self.entry1])
        self.assertEqual(self.manager.filter(["www.*co"]),
                         self.get_all_entries())
        self.assertEqual(len(self.manager.filter(["^www.*co"], "Main")), 1)
        self.assertEqual(self.manager.filter(["^www.*co$"]), [])

if __name__ == '__main__':
    unittest.main()
