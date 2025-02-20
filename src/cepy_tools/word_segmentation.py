# cepy-tools - a sleepy little chinese-english python toolkit
#
# Copyright (C) 2025 Erik Swanson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import collections

"""
Segmentation functions.

All functions share a common interface.

Inputs:
    text    - A string containing the full text
    is_word - A function that maps text -> bool.
              True if the given text is a word.

Outputs:
  - A list of words. Punctuation removed
  - A dictionary of non-words and their frequency
"""

def greedy(text, is_word):
    """Return the longest word whenver possible
    """
    words = []
    non_words = collections.defaultdict(int)

    pos = 0
    word_len = 1
    word = None
    while pos < len(text):
        word_end = pos + word_len

        while is_word(text[pos:word_end]) and word_end < len(text) + 1:
            word = text[pos:word_end]
            word_len += 1
            word_end = pos + word_len

        if word is not None:
            words.append(word)
            word = None
            pos += word_len - 1
        else:
            non_words[text[pos:word_end]] += 1
            pos += 1

        word_len = 1
        word = None

    return words, dict(non_words)

def simplest_tree(text, is_word):
    """Find the segmentation with the fewest nodes for a clause.
    """
    pass
