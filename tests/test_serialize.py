import cepy_tools.serialize as serialize

def test_class_serializer():
    class EasyHard:
        def __init__(self, easy_1, easy_2, hard):
            self.easy_1 = easy_1
            self.easy_2 = easy_2
            self.hard = hard

        @serialize.class_serializer("easy_1", "easy_2")
        def serialize(self):
            return {"hard": "hard: " + self.hard}

    easy_hard = EasyHard("one", "two", "three")
    expected = {"easy_1": "one", "easy_2": "two", "hard": "hard: three"}
    result = easy_hard.serialize()
    print(result)
    assert result == expected
