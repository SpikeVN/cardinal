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
import os

import logger
from . import Locale


def _same_struct(_d1: dict, _d2: dict) -> bool:
    if len(_d1.keys()) != len(_d2.keys()):
        logger.debug(
            "Dissimillar length: ", _d1.keys(), "and", _d2.keys(), ", invalidating"
        )
        return False
    for k, v in _d1.items():
        if k not in _d2.keys():
            logger.debug("Dissimillar key: ", k, "not in", _d2.keys(), ", invalidating")
            return False
        if isinstance(v, dict):
            if isinstance(_d2[k], dict):
                if not _same_struct(v, _d2[k]):
                    return False
    return True


def check_structure(database: dict[Locale, dict[str, dict]]) -> bool:
    skeleton = database[Locale.SKELETON]
    for loc, val in database.items():
        if loc == Locale.SKELETON:
            continue
        if not _same_struct(val, skeleton):
            logger.error(
                f"Inconsistent localization file i18n{os.sep}translation{os.sep}{loc.value.identifier}.json -> "
                f"dissimilar JSON structure to one defined in i18n{os.sep}translation{os.sep}skeleton.json. "
                f"Is an entry missing?"
            )
            return False
        logger.success(f"Checked locale {loc.value}.")

    return True
