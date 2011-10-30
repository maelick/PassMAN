#-*- coding: utf-8 -*-

import unittest, random, os, copy
from passgen import PassmanGenerator, GeneratorManager
from passman import PasswordEntry, PasswordManager

def generate_default_symbols(filename):
    with open(filename, 'w') as f:
        f.write("\n".join([chr(33 + i) for i in xrange(94)]))

# Test égalité entries

class TestPasswordEntry(unittest.TestCase):
    def setUp(self):
        generate_default_symbols("test_symbols")
        self.generator = GeneratorManager(".")
        self.entry = PasswordEntry("sha512:test_symbols", "name", "username",
                                   "Comment about password", "nonce", 16)

    def tearDown(self):
        os.remove("test_symbols")

    def test_match(self):
        self.assertTrue(self.entry.match(["about"]))
        self.assertTrue(self.entry.match(["n.m"]))
        self.assertTrue(self.entry.match(["n.m", "^comMent"]))
        self.assertTrue(not self.entry.match(["nm", "abc"]))
        self.assertTrue(not self.entry.match(["nm", "site"]))

class TestPasswordManager(unittest.TestCase):
    def setUp(self):
        generate_default_symbols("test_symbols")
        self.manager = PasswordManager(".")
        self.generator = self.manager.generator_manager
        self.entry1 = PasswordEntry("sha512:test_symbols", "name1",
                                    "username1", "Comment about password",
                                    "Nonce")
        self.entry2 = PasswordEntry("sha512:test_symbols", "name2",
                                    "username2", "Comment about password",
                                    "www.site2.com")
        self.entry3 = PasswordEntry("sha512:test_symbols", "name3",
                                    "username3")

    def tearDown(self):
        os.remove("test_symbols")

    def test_eq(self):
        self.assertNotEqual(self.entry1, self.entry2)
        self.assertEqual(self.entry1, copy.copy(self.entry1))

    def test_add_entry(self):
        self.manager.add_entry(self.entry1)
        self.manager.set_entry_tags(self.entry1, ["tag1", "tag2"])
        self.manager.add_entry(self.entry2)
        self.manager.set_entry_tags(self.entry2, ["tag2"])
        self.manager.add_entry(self.entry3)
        self.manager.set_entry_tags(self.entry3, ["tag3"])

    def test_get_entries(self):
        self.test_add_entry()
        self.assertItemsEqual(self.manager.get_entries(),
                              [self.entry1, self.entry2, self.entry3])
        self.assertItemsEqual(self.manager.get_entries("tag1"),
                              [self.entry1])
        self.assertItemsEqual(self.manager.get_entries("tag2"),
                              [self.entry1, self.entry2])
        self.assertItemsEqual(self.manager.get_entries("tag3"),
                              [self.entry3])

    def test_remove_entry(self):
        self.test_add_entry()
        self.manager.remove_entry(self.entry1)
        self.manager.remove_entry(self.entry2)
        self.manager.remove_entry(self.entry3)
        self.assertEqual(len(self.manager.passwords), 0)
        self.assertEqual(len(self.manager.tags), 0)

    def test_change_tags(self):
        self.test_add_entry()
        self.manager.set_entry_tags(self.entry1, ["tag1"])
        self.assertEqual([self.entry2], self.manager.get_entries("tag2"))

    def test_get_tags(self):
        self.test_add_entry()
        tags = self.manager.get_tags()
        self.assertItemsEqual(tags, ["tag1", "tag2", "tag3"])

    def test_filter_entries(self):
        self.test_add_entry()
        self.assertItemsEqual(self.manager.filter(["tag2"]),
                         [self.entry1, self.entry2])
        self.assertEqual(self.manager.filter(["www.*co"]),
                         [self.entry2])
        self.assertItemsEqual(self.manager.filter(["comment"]),
                         [self.entry1, self.entry2])
        self.assertEqual(self.manager.filter(["comment", "tag1"]),
                         [self.entry1])
        self.assertEqual(self.manager.filter(["^www.*co$"]), [])

if __name__ == '__main__':
    unittest.main()
