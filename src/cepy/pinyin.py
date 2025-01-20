import csv
import pathlib

PINYIN_TABLE_CSV = pathlib.Path(__file__).parent.parent.parent / "data" / "pinyin-table.csv"
PINYIN_EXCEPTIONS_TXT = pathlib.Path(__file__).parent.parent.parent / "data" / "pinyin-exceptions.txt"

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
                "is_alt": pinyin.endswith("*"),
            })

pinyin_exceptions = []
with open(PINYIN_EXCEPTIONS_TXT) as txt:
    for line in txt.readlines():
        pinyin_exceptions.append(line.strip())

all_pinyin = (
    set(p["pinyin"] for p in pinyin_table)
    | set(p["cedict_pinyin"] for p in pinyin_table)
    | set(pinyin_exceptions)
)
pinyin_characters = "aeiouāēīōūáéíóúǎěǐǒǔàèìòùbcdfghjklmnpqrstwxz:"
pinyin_diacritics = "āēīōūáéíóúǎěǐǒǔàèìòù"
diacritic_removal_table = str.maketrans(dict(zip(
    list("āēīōūáéíóúǎěǐǒǔàèìòù"), list("aeiou")*4
)))

"""
- A and e trump all other vowels and always take the tone mark. There
  are no Mandarin syllables in Hanyu Pinyin that contain both a and e.
- In the combination ou, o takes the mark.
- In all other cases, the final vowel takes the mark
"""

def normalize_pinyin(pinyin):
    """Basic pinyin standardization to make comparison easier

    Normalizations:

    - Remove spaces
    - Remove capitals
    - Remove punctuation
    - Convert tone markers
    - Add neutral tone (5) to un-toned pinyin words
    - Bracket non-pinyin letters

    Examples:
      - "wǒ ài nà ge nǚrén" -> "wo3 ai4 na4 ge5 nu:3 ren2"
      - "AA - zhi4" -> "[AA] zhi4"
    """

    return pinyin

def segment_pinyin(pinyin):
    """Convert string into a list of pinyin and non-pinyin components"""
    remaining_text = pinyin
    output = []
    while remaining_text:
        component, is_pinyin, remaining_text = pop_pinyin(remaining_text)
        output.append((component, is_pinyin))
    return output

def pop_pinyin(text):
    """Pop the first pinyin component off some text"""
    # (0) Munch any whitespace or unused punctuation from the start
    munch_characters = " \n\t-・·.,，_'’`‘’“”\"«»‹›„“‚’「」『』《》〈〉"
    text = text.lstrip(munch_characters)

    # (1) if there's any pinyin at the start, grab it and return.
    i = 0
    while i < len(text) and text[i] in pinyin_characters:
        (curr_slice, curr_rest) = text[:i+1], text[i+1:]
        (next_slice, next_rest) = text[:i+2], text[i+2:]
        next_char = text[i+1] if i+1 < len(text) else None

        curr_no_diacritic = curr_slice.translate(diacritic_removal_table)
        next_no_diacritic = next_slice.translate(diacritic_removal_table)
        if (
                curr_no_diacritic in all_pinyin and
                (next_no_diacritic not in all_pinyin or next_char is None)
        ):
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
