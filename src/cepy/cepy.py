import collections
import pathlib
import textwrap
import unicodedata

DEFAULT_PATH = pathlib.Path(__file__).parent.parent.parent / 'data' / 'cc-cedict.txt'

class CeDict:
    def __init__(self, path=None):
        self.cc_cedict_path = path if path is not None else DEFAULT_PATH

        # A list of CeDictEntry objects. Should never be mutated after
        # creation.
        self._dict = CeDict._read_dict_file(self.cc_cedict_path)

        # These dicts provide O(1) lookup for exact matches. The value
        # for each dict entry is an index to the `self._dict` list.
        _trad_to = collections.defaultdict(list)
        _simp_to = collections.defaultdict(list)
        _pinyin_to = collections.defaultdict(list)

        for index, entry in enumerate(self._dict):
            _trad_to[entry.traditional].append(index)
            _simp_to[entry.simplified].append(index)
            _pinyin_to[entry.pinyin].append(index)

        self._trad_to = dict(_trad_to)
        self._simp_to = dict(_simp_to)
        self._pinyin_to = dict(_pinyin_to)

    @classmethod
    def _read_dict_file(cls, path):
        entries = []

        with open(path) as f:
            for line in f.readlines():
                if line.startswith("#") or line.strip() == "":
                    continue
                else:
                    entries.append(CeDictEntry.from_line(line))

        return entries

    def lookup_simplified(self, simplified):
        index = self._simp_to.get(simplified)
        if index is None:
            return None
        return [self._dict[i] for i in index]

    def lookup_traditional(self, traditional):
        index = self._trad_to.get(traditional)
        if index is None:
            return None
        return [self._dict[i] for i in index]

    def lookup_pinyin(self, pinyin):
        index = self._pinyin_to.get(pinyin)
        if index is None:
            return None
        return [self._dict[i] for i in index]

class CeDictEntry:
    @classmethod
    def from_line(cls, line):
        (trad, _sep, rest) = line.partition(" ")
        (simp, _sep, rest) = rest.partition(" [")
        (pinyin, _sep, rest) = rest.partition("] ")
        defs = rest.strip(" /").split("/")
        return cls(line, trad, simp, pinyin, defs)

    def __init__(self, line, trad, simp, pinyin, defs):
        self.line = line.strip()
        self.traditional = trad
        self.simplified = simp
        self.pinyin = pinyin
        self.defs = defs

    def __repr__(self):
        return f"CeDictEntry.from_line('{self.line}')"

    @property
    def unicode_pinyin(self):
        return self.pinyin + "now with diacritics!"


class KnowledgeBase:
    """A personal knowledge base of known characters and words"""
    def __init__(self, characters, words, delimeter="\n"):
        """
        characters - string of chinese characters
        words - delimited list of words
        delimeter - string that words is delimted by. Defaults to newline
        """
        self.characters = set(
            c for c in characters
            if unicodedata.category(c).startswith('L')
        )
        self.words = set(
            words.split(delimeter)
        )

    def know_char(self, char):
        if len(char.strip()) != 1:
            raise ValueError(f"String '{char}' is more than one character long")
        return char.strip() in self.characters

    def know_word(self, word):
        return word.strip() in self.words or word.strip() in self.characters


class Text:
    """A text in predominantly chinese"""
    def __init__(self, text):
        self.text = text

    def character_frequency(self):
        frequency = collections.defaultdict(int)
        for c in self.text:
            cat = unicodedata.category(c)
            if cat.lower().startswith('l'):
                frequency[c] += 1
        return dict(frequency)

    def word_frequency(self, segmenter):
        frequency = collections.defaultdict(int)
        words, non_words = segmenter(self.text)
        for word in words:
            frequency[word] += 1
        return dict(frequency)


class StudyPlan:
    def __init__(self, text, kb, cedict, segmenter):
        self.text = text
        self.kb = kb
        self.cedict = cedict
        self.segmenter = segmenter

        self.character_frequency = text.character_frequency()
        self.word_frequency = text.word_frequency(self.segmenter)

        self.new_characters = {
            char: freq for char, freq in self.character_frequency.items()
            if not kb.know_char(char)
        }
        self.new_words = {
            word: freq for word, freq in self.word_frequency.items()
            if not kb.know_word(word)
        }

    def total_characters(self):
        return sum(self.character_frequency.values())

    def unique_characters(self):
        return len(self.character_frequency)

    def total_words(self):
        return sum(self.word_frequency.values())

    def unique_words(self):
        return len(self.word_frequency)

    def __str__(self):
        tcc = self.total_characters()
        uc = self.unique_characters()
        nc = len(self.new_characters)
        pnct = nc / tcc if tcc > 0 else 0
        pncu = nc / uc if uc > 0 else 0

        twc = self.total_words()
        uw = self.unique_words()
        nw = len(self.new_words)
        pnwt = nw / twc if twc > 0 else 0
        pnwu = nw / uw if uw > 0 else 0
        text = f"""
        Total Character Count:           {tcc}
        Unique Characters:               {uc}
        New Characters:                  {nc}
        % New Characters (total/unique): {pnct:.1%} / {pncu:.1%}

        Total Word Count:                {twc}
        Unique Words:                    {uw}
        New Words:                       {nw}
        % New Words (total/unique):      {pnwt:.1%} / {pnwu:.1%}
        """
        return textwrap.dedent(text).strip()
