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
    ENGLISH: Language = Language("English", "English", "en-US", disnake.Locale.en_US)
    SKELETON: Language = Language(
        "skeleton lang", "skeleton_debug_language", "skeleton", None
    )


def get_locale(_i: str | disnake.Locale):
    for i in Locale:
        if i.value.identifier == str(_i):
            return i
    else:
        raise KeyError(f"Locale with identifier '{_i}' not found.")
