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


import cepy_tools.pinyin as pin

def test_normalize_pinyin():
    tests = {
        "wǒ ài nà ge nǚrén": "wo3 ai4 na4 ge5 nu:3 ren2",
        "Ta1men2": "ta1 men2",
        "T F ka3": "[T F] ka3",
        "Xī'ān": "xi1 an1",
        "xi'an": "xi5 an5",
        "xian": "xian5",
        "xīān": "xi1 an1",
        "xīan": "xian1",
        "là de cài.": "la4 de5 cai4"
    }
    for input_pinyin, expected in tests.items():
        assert pin.normalize_pinyin(input_pinyin) == expected

def test_pop_pinyin():
    tests = {
        # valid pinyin at the start
        "wo3 ai4 ni3": ("wo3", " ai4 ni3"),
        "xiang3": ("xiang3", ""),
        "xìhuan": ("xì", "huan"),
        "wǒ": ("wǒ", ""),
        "wǒ5": ("wǒ", "5"),
        "nu:3 er2": ("nu:3", " er2"),
        "hua1 r5": ("hua1", " r5"),
        " wo3": ("wo3", ""),
        "ge": ("ge", ""),
        "wǒshì": ("wǒ", "shì"),
        "mei3guo2": ("mei3", "guo2"),
        "xīān": ("xī", "ān"),
        "xī'ān": ("xī", "'ān"),
        "Dai4": ("dai4", ""),
        "Dài": ("dài", ""),
        "AA zhi4": ("a", "A zhi4"),
        "nv3": ("nv3", ""),
        "nǚ": ("nǚ", ""),

        # Invalid pinyin at the start
        "XYZ": ("[XYZ]", ""),
        "XYZ wo3 shi4": ("[XYZ]", "wo3 shi4"),
        "123 - wǒ": ("[123]", "wǒ"),
        "3P": ("[3P]", ""),
        "Blah": ("[B]", "lah"), # Because "la" is valid pinyin

        # munches whitespace and punctuation
        " \n\t-・· wǒ .": ("wǒ",  " ."),
        "XYZ ,，_'’`‘’shì": ("[XYZ]", "shì"),
        "“”\"«»‹›„“‚’「」『』《》〈〉": ("", ""),

        # empty gives empty
        "": ("", "")
    }
    for input_text, (popped, rest) in tests.items():
        print(input_text)
        assert pin.pop_pinyin(input_text) == (popped, rest)


def test_segment_pinyin():
    test = "wǒshì・ mei3 guo2ren2. XYZ nage"
    expected = ["wǒ", "shì", "mei3", "guo2", "ren2", "[XYZ]", "na", "ge"]
    assert pin.segment_pinyin(test) == expected


def test_tone_diacritic_to_numeral():
    tests = {
        "yī": "1",
        "rén": "2",
        "xiǎng": "3",
        "shì": "4",
        "ge": "5",
        "xīán": "2",
    }
    for text, expected in tests.items():
        assert pin.tone_diacritic_to_number_string(text) == expected
