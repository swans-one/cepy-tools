from cepy import cepy, word_segmentation as ws
import sys
import pprint

if __name__ == "__main__":
    characters_path = sys.argv[1]
    words_path = sys.argv[2]
    text_path = sys.argv[3]

    with open(characters_path) as f:
        characters = f.read()

    with open(words_path) as f:
        words = f.read()

    with open(text_path) as f:
        full_text = f.read()

    kb = cepy.KnowledgeBase(characters, words)
    text = cepy.Text(full_text)
    cedict = cepy.CeDict()

    def is_word(text):
        return cedict.lookup_simplified(text) is not None

    def segmenter(text):
        return ws.greedy(text, is_word)

    sp = cepy.StudyPlan(text, kb, cedict, segmenter)
    print(str(sp))
