import cepy.pinyin as pin


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

        # Invalid pinyin at the start
        "ABC": ("[ABC]", ""),
        "ABC wo3 shi4": ("[ABC]", "wo3 shi4"),
        "123 - wǒ": ("[123]", "wǒ"),
        "Test": ("[T]", "est"), # Because "e" is valid pinyin

        # munches whitespace and punctuation
        " \n\t-・· wǒ .": ("wǒ",  " ."),
        "TEST ,，_'’`‘’shì": ("[TEST]", "shì"),
        "“”\"«»‹›„“‚’「」『』《》〈〉": ("", ""),

        # empty gives empty
        "": ("", "")
    }
    for input_text, (popped, rest) in tests.items():
        print(input_text)
        assert pin.pop_pinyin(input_text) == (popped, rest)
