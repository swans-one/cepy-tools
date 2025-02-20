import pathlib

import cepy_tools.cepy as cepy
import cepy_tools.word_segmentation as ws

TEST_DICT = pathlib.Path(__file__).parent / "test_dict.txt"

# TODO: put this setup code in classes, and ther rest too
cedict = cepy.CeDict(TEST_DICT)

# CeDict

def test_cedict_lookup_simplified():
    entries = cedict.lookup_simplified("巨蟒")
    assert entries[0].simplified == "巨蟒"
    assert entries[0].traditional == "巨蟒"
    assert entries[0].pinyin == "ju4 mang3"


def test_cedict_lookup_traditional():
    entries = cedict.lookup_traditional("話")
    assert entries[0].simplified == "话"
    assert entries[0].traditional == "話"
    assert entries[0].pinyin == "hua4"



def test_cedict_lookup_pinyin():
    entries = cedict.lookup_pinyin("cheng2 xu4 she4 ji4")
    assert entries[0].simplified == "程序设计"
    assert entries[0].traditional == "程序設計"
    assert entries[0].pinyin == "cheng2 xu4 she4 ji4"

# CeDictEntry

def test_cedict_entry_serialize():
    entry = cepy.CeDictEntry.from_line("巨蟒 巨蟒 [ju4 mang3] /python/")
    expected = {
        "line": "巨蟒 巨蟒 [ju4 mang3] /python/",
        "traditional": "巨蟒",
        "simplified": "巨蟒",
        "pinyin": "ju4 mang3",
        "defs": ["python"],
    }
    assert entry.serialize() == expected

# KnowledgeBase
kb = cepy.KnowledgeBase(
    characters = "巨蟒程序设计话",
    words = "巨蟒\n程序设计\n话",
    delimeter = "\n"
)

def test_knowledge_base_know_char():
    assert kb.know_char("巨")
    assert not kb.know_char("我")

def test_knowledge_base_know_word():
    assert kb.know_word("巨")
    assert kb.know_word("巨蟒")
    assert not kb.know_word("设计")
    assert not kb.know_word("我")

# Text

cedict = cepy.CeDict(TEST_DICT)

def is_word(text):
    return cedict.lookup_simplified(text) is not None

def segmenter(text):
    return ws.greedy(text, is_word)

class TestText:
    text = cepy.Text("巨蟒程序设计话巨蟒")

    def test_text_character_frequency(self):
        char_counts = self.text.character_frequency()
        expected = {"巨":2,"蟒":2,"程":1,"序":1,"设":1,"计":1,"话":1,}
        assert char_counts == expected

    def test_text_word_frequency(self):
        word_counts = self.text.word_frequency(segmenter)
        print(self.text)
        expected = {"巨蟒":2, "程序": 1, "设计":1, "话":1}
        assert word_counts == expected

# StudyPlan

def test_plan():
    text = cepy.Text("巨蟒程序设计话巨蟒")
    kb = cepy.KnowledgeBase("话程序", "程序")
    planner = cepy.StudyPlan(text, kb, cedict, segmenter)
    plan = planner.plan()

    new_chars = [c.text for c in plan if c.text_type == "char"]
    assert "巨" in new_chars
    assert "话" not in new_chars

    new_words = [w.text for w in plan if w.text_type == "word"]
    assert "设计" in new_words
    assert "程序" not in new_words
