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

import unittest

from loader import YAMLLoader, AESLoader, GPGLoader

class TestYAMLLoader(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_save(self):
        self.assertEqual(True, False)

    def test_load(self):
        self.assertTrue(False)

class TestAESLoader(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_save(self):
        self.assertEqual(True, False)

    def test_load(self):
        self.assertTrue(False)

class TestGPGLoader(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_save(self):
        self.assertEqual(True, False)

    def test_load(self):
        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
