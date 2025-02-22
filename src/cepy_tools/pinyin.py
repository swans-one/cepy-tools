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

import csv
import pathlib

PINYIN_TABLE_CSV = pathlib.Path(__file__).parent.parent.parent / "data" / "pinyin-table.csv"
PINYIN_EXCEPTIONS_TXT = pathlib.Path(__file__).parent.parent.parent / "data" / "pinyin-exceptions.txt"


# TODO: This shouldn't happen on import. Write a script to generate
# this output.
pinyin_table = []
with open(PINYIN_TABLE_CSV) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        final = row["FINAL"]
        for initial, pinyin in row.items():
            if initial == "FINAL" or pinyin == "":
                continue
            pinyin_table.append({
                "initial": initial,
                "final": final,
                "pinyin": pinyin.strip("*"),
                "cedict_pinyin": pinyin.strip("*").replace("ü", "u:"),
                "v_pinyin": pinyin.strip("*").replace("ü", "v"),
                "is_alt": pinyin.endswith("*"),
            })

pinyin_exceptions = []
with open(PINYIN_EXCEPTIONS_TXT) as txt:
    for line in txt.readlines():
        pinyin_exceptions.append(line.strip())

all_pinyin = (
    set(p["pinyin"] for p in pinyin_table)
    | set(p["cedict_pinyin"] for p in pinyin_table)
    | set(p["v_pinyin"] for p in pinyin_table)
    | set(pinyin_exceptions)
)
pinyin_characters = "aeiouüāēīōūǖáéíóúǘǎěǐǒǔǚàèìòùǜbcdfghjklmnpqrstvwxz:AEIOUBCDFGHJKLMNPQRSTWXZ"
pinyin_diacritics = "āēīōūǖáéíóúǘǎěǐǒǔǚàèìòùǜ"
diacritic_removal_table = str.maketrans(dict(zip(
    list("āēīōūǖáéíóúǘǎěǐǒǔǚàèìòùǜ"), list("aeiouü")*4
)))
umlaut_removal_table = str.maketrans({"ü": "u:", "v": "u:"})

"""
- A and e trump all other vowels and always take the tone mark. There
  are no Mandarin syllables in Hanyu Pinyin that contain both a and e.
- In the combination ou, o takes the mark.
- In all other cases, the final vowel takes the mark
"""

def normalize_pinyin(pinyin):
    """Standardize pinyin strings to make comparison easier.

    Pinyin is a fairly well specified standard, but there are several
    ways of writing different pinyin characters

    "wǒ ài nà ge nǚrén" -> "wo3 ai4 na4 ge5 nu:3 ren2"

    Normalizations:
      - Distinguish pinyin from non pinyin by bracketing non-pinyin segments
      - Remove punctuation markers and extra spaces
      - Replace all diacritics with tone numbers
      - Ensure all pinyin have tone number by adding neutral tone (5)
        to un-toned pinyin words.
      - Remove capitals from pinyin (but not non-pinyin)
      - convert umlauts to cedict standard (e.g. nǚ or nv3 to nu:3)
      - Remove extra spaces and normalize to exactly one space between
        pinyin segments

    Examples:
      - "wǒ ài nà ge nǚrén" -> "wo3 ai4 na4 ge5 nu:3 ren2"
      - "Ta1men2" -> "ta1 men2"
      - "Wo3 shi4 Jane Doe." -> "wo3 shi4 [J] an5 e5 [Do] e5"

    *Note on non-pinyin, ambiguities, and missing tone marks*

    This function assumes that the pinyin entered is valid pinyin. It
    will attempt to continue working if non-pinyin characters are
    included. This is important because some cc-cedict entries include
    characters from the latin alphabet which are pronouced. See for
    example this cc-cedict entry:

    TF卡 TF卡 [T F ka3] /microSD card/

    Which would normalize to `"[T F] ka3"`. However, there are
    limitations to this approach as the following entry would not
    normalize as clearly:

    AA制 AA制 [AA - zhi4] /to split the bill; to go Dutch/

    This would normalize to `"a5 a5 zhi4"`, which is likely not the
    intended normalization. However, the main purpose of this function
    is to deal with pinyin, not non-pinyin, so some sacrifices have
    been made.

    Additionally, this function expects that pinyin be written
    unambiguously. While it will attempt to segment properly, if there
    is ambiguity it may not do what you intend. See for example, the
    several ways of writing Xī'ān:

      - "Xī'ān" -> "xi1 an1"
      - "xi'an" -> "xi5 an5"
      - "xian" -> "xian5"
      - "xīān" -> "xi1 an1"
      - "xīan" -> "xian1"

    This example shows that the normalization attempts to find the
    longest valid pinyin. This is handled in the pinyin standard by
    requiring any sylable starting with a vowel after the first
    syllable of a word be prefixed with an appostrophe (`'`) to make
    it clearer, even in instances where there's not technically an
    ambiguity.
    """
    # Segmenting removes extraneous whitespace and punctuation
    segments = segment_pinyin(pinyin)
    normalized = []
    for segment in segments:
        # Don't change non-pinyin at all
        if segment.startswith("["):
            normalized.append(segment)
            continue

        # Remove Uppercase
        segment = segment.lower()

        # Convert diacritics to numbers
        if not segment.endswith(("1", "2", "3", "4", "5")):
            number_string = tone_diacritic_to_number_string(segment)
            segment = segment.translate(diacritic_removal_table) + number_string

        # Normalize umlauts
        segment = segment.translate(umlaut_removal_table)

        normalized.append(segment)

    return " ".join(normalized)


def tone_diacritic_to_number_string(text):
    """Return the
    """
    diacritic_map = {
        "āēīōūǖ": "1",
        "áéíóúǘ": "2",
        "ǎěǐǒǔǚ": "3",
        "àèìòùǜ": "4",
    }
    for letter in reversed(text):
        if letter in pinyin_diacritics:
            for toned_letters, tone_number in diacritic_map.items():
                if letter in toned_letters:
                    return tone_number
    return "5"


def segment_pinyin(pinyin):
    """Convert string into a list of pinyin and non-pinyin components"""
    remaining_text = pinyin
    output = []
    while remaining_text:
        component, remaining_text = pop_pinyin(remaining_text)
        if component != "":
            output.append(component)
    return output

def pop_pinyin(text):
    """Pop the first pinyin component off some text"""
    # TODO: Output a metadata object that can include:
    #  - Was capitalized
    #  - How many characters removed before
    #  - Followed by space?
    #  - Is pinyin

    # (0) Munch any whitespace or unused punctuation from the start
    munch_characters = " \n\t-・·.,，_'’`‘’“”\"«»‹›„“‚’「」『』《》〈〉"
    text = text.lstrip(munch_characters)

    # (1) if there's any pinyin at the start, grab it and return.
    i = 0
    while i < len(text) and text[i].lower() in pinyin_characters:
        (curr_slice, curr_rest) = text[:i+1].lower(), text[i+1:]
        (next_slice, next_rest) = text[:i+2].lower(), text[i+2:]
        next_char = text[i+1] if i+1 < len(text) else None

        curr_no_diacritic = curr_slice.translate(diacritic_removal_table)
        next_no_diacritic = next_slice.translate(diacritic_removal_table)
        diacritic_count = sum(1 if l in pinyin_diacritics else 0 for l in curr_slice)

        # Determine if we should stop now or keep looking further
        currently_valid_pinyin = curr_no_diacritic in all_pinyin
        should_stop_now = (
            next_no_diacritic not in all_pinyin
            or next_char is None
            or (diacritic_count > 0 and next_char in pinyin_diacritics)
        )
        if currently_valid_pinyin and should_stop_now:
            # We got one!
            has_diacritic = any([c in pinyin_diacritics for c in curr_slice])
            if has_diacritic:
                # Don't look for a number if there's a diacritic (e.g. "gè")
                return (curr_slice, curr_rest)
            elif next_char is not None and next_char in "12345":
                # If there's no diacritic, check to include the number
                # following (e.g. "ge4")
                return (next_slice, next_rest)
            else:
                # Valid pinyin with no diacritic or number (e.g. "ge")
                return (curr_slice, curr_rest)
        i += 1

    # (2) If there's not valid pinyin at the start: reset to 0 and
    # grab anything that's not valid pinyin, up ot the first valid
    # pinyin and bracket it.
    i = 0
    while i < len(text):
        # Search window for valid pinyin
        longest_pinyin = len("zhuang1")
        window_end = i+min(longest_pinyin, len(text) - i)
        x, ln = text[i:window_end], len(text)

        for j in range(i, window_end):
            next_bit = text[i:j+1].translate(diacritic_removal_table)
            if next_bit in all_pinyin:
                invalid, rest = text[:i], text[i:]
                invalid = invalid.strip(munch_characters)
                return (f"[{invalid}]", rest)
        i += 1

    # if we never found more valid pinyin, all the text is invalid and
    # can be returned bracketed.
    final_output = f"[{text}]" if text else ""
    return (final_output, "")
