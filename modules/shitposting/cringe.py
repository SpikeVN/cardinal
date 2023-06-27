# Copyright (c) 2022-2023 SpikeBonjour
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import random

# Default dictionary.
CONTENT = {
    "anh": "ank",
    "à": "àk",
    "có": "kó",
    "biết": "bík",
    "khi": "khj",
    "em": "e",
    "mới": "múk",
    "rời": "gờii",
    "xa": "xak",
    "đã": "đả",
    "rất": "gấk",
    "buồn": "pùk",
    "khóc": "khók",
    "nhiều": "nkìu",
    "ăn": "ăng",
    "ngon": "ngok",
    "không": "hokk",
    "ngủ": "nghũ",
    "cũng": "cx",
    "yên": "yn",
    "cuộc": "kuộk",
    "sống": "xốlg",
    "của": "kũa",
    "dường": "giườnk",
    "như": "nku",
    "bất": "pấk",
    "ổn": "ỗn",
    "còn": "tòn",
    "yêu": "iu",
    "phát": "pkát",
    "điên": "đjin",
    "mỗi": "mõi",
    "ngày": "nqày",
    "trôi": "chôi",
    "qua": "wa",
    "đều": "đìuu",
    "nhớ": "nkớ",
    "sức": "xứk",
    "bị": "pj",
    "trầm": "ckam",
    "cảm": "kãm",
    "nhìn": "nhìnn",
    "người": "ngừi",
    "lúc": "lúk",
    "trước": "trk",
    "hai": "2",
    "từng": "từg",
    "vui": "zuii",
    "vẻ": "zẻ",
    "chấp": "ckấp",
    "nhận": "nkận",
    "sự": "xự",
    "thật": "thậkk",
    "nhưng": "nhưnq",
    "trong": "trongg",
    "trí": "trý",
    "là": "làk",
    "hình": "hỳnh",
    "bóng": "pónk",
    "tự": "tựk",
    "hỏi": "hõi",
    "nghĩ": "nghỉ",
    "nổi": "nỗii",
    "vì": "vỳ",
    "nhạt": "nhạc",
    "nhẽo": "nhẻo",
    "đêm": "đêmm",
    "nào": "nàoo",
    "bản": "pãn",
    "thân": "thâng",
    "tại": "tạii",
    "sao": "s",
    "vậy": "zz",
    "chọn": "chọnn",
    "nhóc": "nhók",
    "đó": "đók",
    "chứ": "chứk",
    "phải": "phãi",
    "nó": "nók",
    "tốt": "tốt",
    "hơn": "hơng",
    "luôn": "lunn",
    "thấy": "thấykk",
    "cô": "kô",
    "đơn": "đơng",
    "thương": "thw",
    "lắm": "lémm",
    "mơ": "mơk",
    "quên": "q:ươn",
    "vẫn": "zẫn",
    "rồi": "gùii",
    "chung": "truk",
    "phim": "fjm",
    "ừ": "uk",
    "gì": "z",
    "trời": "tr",
    "tuổi": "tut",
    "chú": "chu",
}

MODIFICATIONS = [
    lambda x: x.replace("h", "k"),
    lambda x: x.replace("ị", "j"),
    lambda x: x + x[-1],
    lambda x: x.replace("r", "g"),
    lambda x: x.replace("l", "n"),
    lambda x: x.replace("c", "k"),
    lambda x: x.replace("s", "x"),
    lambda x: x.replace("y", "i"),
    lambda x: x.replace("tr", "ch"),
    lambda x: x.replace("qu", "w"),
    lambda x: x.replace("g", "q"),
    lambda x: x.replace("ê", "i"),
    lambda x: x.replace("ng", "g"),
    lambda x: x.replace("l", "n"),
    lambda x: x + "k",
    lambda x: x.replace("ph", "f"),
]


def _transform_word(word: str):
    """
    Creates a cringe spelling of a word.

    :param word: the word to transform
    :return: the transformed cringe word
    """
    output = CONTENT.get(word, word)
    mods = random.choices(MODIFICATIONS, k=2)
    output = mods[0](output)
    output = mods[1](output)
    return output


def transform_text(text: str):
    return " ".join([_transform_word(i) for i in text.split()])
