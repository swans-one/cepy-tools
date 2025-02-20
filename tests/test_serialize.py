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
