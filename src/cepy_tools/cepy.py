import cepy_dict
import collections
import pathlib
import textwrap
import unicodedata

import cepy_tools.serialize as cepy_serial

class CeDict:
    def __init__(self, path=None):
        self.cc_cedict_path = path

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
        raw_entries = cepy_dict.entries()
        return [CeDictEntry(*e) for e in raw_entries]

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

    # TODO: pinyin normilization
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
        defs = [d.strip() for d in rest.strip(" /\n\t").split("/")]
        return cls(line, trad, simp, pinyin, defs)

    @classmethod
    def empty(cls, empty_text=None):
        empty_text = (
            empty_text if empty_text is not None
            else "Definition Not Found"
        )
        return cls(f"X X [X] /{empty_text}/", "X", "X", "X", [empty_text])

    def __init__(self, line, trad, simp, pinyin, defs):
        self.line = line.strip()
        self.traditional = trad
        self.simplified = simp
        self.pinyin = pinyin
        self.defs = defs

    def __repr__(self):
        return f"CeDictEntry.from_line('{self.line}')"

    @cepy_serial.class_serializer(
        "line", "traditional", "simplified", "pinyin", "defs"
    )
    def serialize(self):
        return {}

    @property
    def unicode_pinyin(self):
        # TODO implement this
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
        # TODO: should this just take an array rather than do the split for you?
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

    def __repr__(self):
        if len(self.text) > 40:
            return 'Text("{short}...")'.format(short=self.text[0:40])
        else:
            return f'Text("{self.text}")'

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
        print(words, non_words)
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

    def plan(self):
        """List the characters and words needed to understand a given
        cumulative percentage of the text."""
        plan = []
        newly_learned_characters = set()

        def pct_known(count, total):
            return count / total if total > 0 else 0

        known_char_count = sum([
            f for c, f in self.character_frequency.items()
            if self.kb.know_char(c)
        ])
        known_word_count = sum([
            f for w, f in self.word_frequency.items()
            if self.kb.know_word(w)
        ])
        total_word = self.total_words()
        total_char = self.total_characters()
        base_entry = PlanEntry(
            count = 0,
            cumulative_char = pct_known(known_char_count, total_char),
            cumulative_word = pct_known(known_word_count, total_word),
            text = "X",
            text_type = "word",
            definitions = [CeDictEntry.empty("<Current Knowledge>")],
        )
        plan.append(base_entry)

        snd = lambda x: x[1]
        for word, freq in sorted(self.new_words.items(), key=snd, reverse=True):
            unknown_word_characters = [
                c for c in word
                if not self.kb.know_char(c) and c not in newly_learned_characters
            ]
            for char in unknown_word_characters:
                known_char_count += self.character_frequency[char]
                newly_learned_characters.add(char)
                plan.append(PlanEntry(
                    count = self.character_frequency[char],
                    cumulative_char = pct_known(known_char_count, total_char),
                    cumulative_word = pct_known(known_word_count, total_word),
                    text = char,
                    text_type = "char",
                    definitions = (
                        self.cedict.lookup_simplified(char)
                        or self.cedict.lookup_traditional(char)
                        or [CeDictEntry.empty()]
                    )
                ))
            known_word_count += freq
            plan.append(PlanEntry(
                count = freq,
                cumulative_char = pct_known(known_char_count, total_char),
                cumulative_word = pct_known(known_word_count, total_word),
                text = word,
                text_type = "word",
                definitions = (
                    self.cedict.lookup_simplified(word)
                    or self.cedict.lookup_traditional(word)
                    or [CeDictEntry.empty()]
                )
            ))
        return plan

    def total_characters(self):
        return sum(self.character_frequency.values())

    def unique_characters(self):
        return len(self.character_frequency)

    def total_words(self):
        return sum(self.word_frequency.values())

    def unique_words(self):
        return len(self.word_frequency)

    def stats(self):
        stats = {}
        stats["total_char"] = self.total_characters()
        stats["unique_char"] = self.unique_characters()
        stats["new_unique_char"] = len(self.new_characters)
        stats["new_total_char"] = sum(self.new_characters.values())
        stats["pct_new_char_total"] = (
            stats["new_total_char"] / stats["total_char"]
            if stats["total_char"] > 0 else 0
        )
        stats["pct_new_char_unique"] = (
            stats["new_unique_char"] / stats["unique_char"]
            if stats["unique_char"] > 0 else 0
        )
        stats["total_word"] = self.total_words()
        stats["unique_word"] = self.unique_words()
        stats["new_unique_word"] = len(self.new_words)
        stats["new_total_word"] = sum(self.new_words.values())
        stats["pct_new_word_total"] = (
            stats["new_total_word"] / stats["total_word"]
            if stats["total_word"] > 0 else 0
        )
        stats["pct_new_word_unique"] = (
            stats["new_unique_word"] / stats["unique_word"]
            if stats["unique_word"] > 0 else 0
        )
        return stats

    def __str__(self):
        text = """
        Total Character Count:           {total_char}
        Unique Characters:               {unique_char}
        New Characters:                  {new_unique_char}
        % New Characters (total/unique): {pct_new_char_total:.1%} / {pct_new_char_unique:.1%}

        Total Word Count:                {total_word}
        Unique Words:                    {unique_word}
        New Words:                       {new_unique_word}
        % New Words (total/unique):      {pct_new_word_total:.1%} / {pct_new_word_unique:.1%}
        """.format(**self.stats())
        return textwrap.dedent(text).strip()


class PlanEntry:
    def __init__(self, count, cumulative_char, cumulative_word, text, text_type, definitions):
        self.count = count
        self.cumulative_char = cumulative_char
        self.cumulative_word = cumulative_word
        self.text = text
        self.text_type = text_type
        self.definitions = definitions

    def fmt_one_line(self):
        all_pinyin = ";".join(d.pinyin for d in self.definitions)
        all_definitions = "] ;; [".join(" / ".join(d.defs) for d in self.definitions)
        return "[w: {cw:.0%} / c:{cc:.0%}] <{n}> {txt}{tt} ({pin}) :: [{dfn}]".format(
            cw = self.cumulative_word,
            cc = self.cumulative_char,
            n = self.count,
            txt = self.text,
            tt = "*" if self.text_type == "char" else "",
            pin = all_pinyin,
            dfn = all_definitions,
        )

    def fmt_multi_line(self):
        all_pinyin = ";".join(d.pinyin for d in self.definitions)
        header = "[w: {cw:.0%} / c:{cc:.0%}] <{n}> {txt}{tt} ({pin}) ::\n".format(
            cw = self.cumulative_word,
            cc = self.cumulative_char,
            n = self.count,
            txt = self.text,
            tt = "*" if self.text_type == "char" else "",
            pin = all_pinyin,
        )
        defs = "\n".join([
            "    -- ({pin}) :: {dfn}".format(pin=d.pinyin, dfn=" / ".join(d.defs))
            for d in self.definitions
        ])
        return f"{header}{defs}"

    @cepy_serial.class_serializer(
        "count", "cumulative_char", "cumulative_word", "text", "text_type"
    )
    def serialize(self):
        return { "definitions": [d.serialize() for d in self.definitions] }

    def __repr__(self):
        return f"<PlanEntry - {self.text} - [{self.count}]>"

    def __str__(self):
        if len(self.definitions) == 1:
            return self.fmt_one_line()
        else:
            return self.fmt_multi_line()
