import pathlib

DEFAULT_PATH = pathlib.Path(__file__).parent.parent.parent / 'data' / 'cc-cedict.txt'

class CeDict:
    def __init__(self, path=None):
        self.cc_cedict_path = path if path is not None else DEFAULT_PATH

        # A list of CeDictEntry objects. Should never be mutated after
        # creation.
        self._dict = CeDict._read_dict_file(self.cc_cedict_path)

        # These dicts provide O(1) lookup for exact matches. The value
        # for each dict entry is an index to the `self._dict` list.
        self._trad_to = {}
        self._simp_to = {}
        self._pinyin_to = {}

        def add_entry(dic, ent, ind):
            if ent in dic:
                dic[ent].append(ind)
            dic[ent] = [ind]

        for index, entry in enumerate(self._dict):
            add_entry(self._trad_to, entry.traditional, index)
            add_entry(self._simp_to, entry.simplified, index)
            add_entry(self._pinyin_to, entry.pinyin, index)

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



if __name__ == "__main__":
    d = CeDict()
    num_entry = len(d._dict)
    num_def = sum([len(e.defs) for e in d._dict])
    trad_uniq = len(d._trad_to)
    simp_uniq = len(d._simp_to)
    pinyin_uniq = len(d._pinyin_to)
    print(f"Dictionary contains {num_entry} entries and {num_def} definitions")
    print(f"{trad_uniq} unique traditional character words")
    print(f"{simp_uniq} unique simplified character words")
    print(f"{pinyin_uniq} unique pinyin pronunciations")
