# CePy-Tools - A sleepy little chinese english dictionary toolkit

The `cepy-tools` package contains a variety of tools for working with
chinese texts as a language learner.

It includes features for:

- Chinese Word Segmentation
- Chinese / english dictionary tools
- Pinyin normalization
- Study plan creation

# Installation

CePy-Tools can be installed via pip: `pip install cepy-tools`.

# Usage

## Chinese English Dictionary

CePy-Tools ships with a built in Chinese English dictionary via
[`cepy-dict`](https://github.com/swans-one/cepy-dict). It builds
several useful tools on top of the base dictionary.

```python
from cepy_tools import CeDict

cedict = CeDict()
cedict.lookup_simplified("巨蟒")
cedict.lookup_traditional("話")
cedict.lookup_pinyin("cheng2 xu4 she4 ji4")
```

## Pinyin Normalization

CePy-Tools can normalize a variety of pinyin formats into the [format
used by cc-cedict](https://cc-cedict.org/wiki/format:syntax) which is
the underlying chinese-english dictionary shipping with CePy-Tools.

While not perfect for proper nouns, words that contain Latin
characters, or ambiguously written pinyin, it can normalize a variety
of pinyin representations:

```python
from cepy_tools.pinyin import normalize_pinyin

normalize_pinyin("wǒ hěn xǐhuān là de cài")
# -> "wo3 hen3 xi3 huan1 la4 de5 cai4"

normalize_pinyin("nv3ren2")
# -> "nu:3 ren2"
```

## Study Plans

A more advanced example is creating study plans for a novel text
in chinese.

The following will compare all the characters and words in a given
text to the characters and words you've listed as "known" in your
knowledge base. It will then print out a study plan of what characters
and words you should learn to best understand the text.

```python
from cepy_tools import CeDict, StudyPlan, Text, KnowledgeBase
from cepy_tools.word_segmentation import greedy

cedict = CeDict()
kb = KnowledgeBase("我设计很", "设计")
text = Text("我很喜欢程序设计")
def segmenter(text):
    return greedy(text, lambda w: cedict.lookup_simplified(w) is not None)

planner = StudyPlan(text, kb, cedict, segmenter)
print(planner)

for plan_entry in planner.plan():
    print(str(plan_entry))
```

It prints the following information. Note that the words and
characters also show a cumulative percentage of how much of the input
text can be understood by following the study guide to that point.

```
Total Character Count:           8
Unique Characters:               8
New Characters:                  4
% New Characters (total/unique): 50.0% / 50.0%

Total Word Count:                5
Unique Words:                    5
New Words:                       2
% New Words (total/unique):      40.0% / 40.0%

[w: 60% / c:50%] <0> X (X) :: [<Current Knowledge>]
[w: 60% / c:62%] <1> 喜* (xi3) :: [to be fond of / to like / to enjoy / to be happy / to feel pleased / happiness / delight / glad]
[w: 60% / c:75%] <1> 欢* (huan1;huan1;huan1;huan1) ::
    -- (huan1) :: variant of 歡|欢[huan1]
    -- (huan1) :: joyous / happy / pleased
    -- (huan1) :: hubbub / clamor / variant of 歡|欢[huan1]
    -- (huan1) :: a breed of horse / variant of 歡|欢[huan1]
[w: 80% / c:75%] <1> 喜欢 (xi3 huan5) :: [to like; to be fond of]
[w: 80% / c:88%] <1> 程* (Cheng2;cheng2) ::
    -- (Cheng2) :: surname Cheng
    -- (cheng2) :: rule / order / regulations / formula / journey / procedure / sequence
[w: 80% / c:100%] <1> 序* (xu4) :: [(bound form) order; sequence / (bound form) introductory; initial / preface]
[w: 100% / c:100%] <1> 程序 (cheng2 xu4) :: [procedures / sequence / order / computer program]
```

The above example uses a very small knowledge base and very short
text, but it can be used to generate study plans for much larger texts
and much larger knowledge bases.

# License

CePy-Tools -- Copyright (C) 2025 Erik Swanson

CePy-Tools is licensed under the GPL-v3 (or later). See COPYING for more details.
