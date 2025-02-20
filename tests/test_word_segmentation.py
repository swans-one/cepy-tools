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


from cepy_tools import word_segmentation as ws

def word_sample_func(text):
    words = [
        "我", "你", "她", "他", "是", "有", "人", "美",
        "喜", "欢", "中", "国", "菜", "的", "吗",
        "美国", "哪个", "喜欢", "中国",
        "中国菜"
    ]
    return text in words


def test_greedy():
    text = "她是美国人。"
    output = ws.greedy(text, word_sample_func)
    expected = (["她", "是", "美国", "人"], {"。": 1})
    assert output == expected

    text2 = "我喜欢中国菜。你喜欢的吗"
    output2 = ws.greedy(text2, word_sample_func)
    expected2 = (["我", "喜欢", "中国菜", "你", "喜欢", "的", "吗"], {"。": 1})
    print(output2)
    print(expected2)
    assert output2 == expected2
