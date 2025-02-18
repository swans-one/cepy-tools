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
