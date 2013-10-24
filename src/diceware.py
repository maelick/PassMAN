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


def load_file(filename):
    with open(filename) as f:
        return f.read().lower()


def filter_text(text):
    ignore = set(['!', '"', '$', '&', '(', ')', '*', ',', ';', ':', '?',
                  '.', "'", "-"])
    text = (' ' if c in ignore or c.isdigit() else c for c in text)
    return ''.join(text)


def make_word_count(text):
    wc = {}
    for word in text.split():
        if word not in wc:
            wc[word] = 0
        wc[word] += 1
    return wc

def make_diceware(wc, n=7776, min_length=1):
    words = [w for w in wc if len(w) >= min_length]
    words.sort(key=lambda w: -wc[w])
    return words[:n]


def write_diceware(words, filename):
    with open(filename, 'w') as f:
        f.write('\n'.join(words))
