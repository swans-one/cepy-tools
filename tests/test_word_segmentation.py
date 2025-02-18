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
