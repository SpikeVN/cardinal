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
