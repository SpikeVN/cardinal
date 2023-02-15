#  Copyright (c) 2022-2023 The Block Art Online Project contributors.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import dataclasses
import enum

import disnake


@dataclasses.dataclass
class Language:
    """Represents a supported language."""

    native_name: str
    english_name: str
    identifier: str
    discord_locale: disnake.Locale | None


class Locale(enum.Enum):
    """The supported language list."""

    VIETNAMESE: Language = Language("Tiếng Việt", "Vietnamese", "vi", disnake.Locale.vi)
    ENGLISH: Language = Language("English", "English", "en_US", disnake.Locale.en_US)
    SKELETON: Language = Language(
        "skeleton lang", "skeleton_debug_language", "skeleton", None
    )


def from_identifier(_i: str):
    for i in Locale:
        if i.value.identifier == _i:
            return i
    else:
        raise KeyError(f"Locale with identifier '{_i}' not found.")
