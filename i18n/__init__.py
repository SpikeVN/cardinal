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


"""
Apes localization engine.
"""

import json
import os
import random

import logger
from .abc import *
from .checker import check_structure

LOCALIZATION_DATA: dict[Locale, dict[str, dict]] = {}


def init_translation_database():
    logger.info("Initializing localization database...")
    global LOCALIZATION_DATA
    for lan in os.listdir("i18n/translations"):
        if lan.endswith(".json"):
            with open(f"i18n/translations/{lan}", "r", encoding="utf8") as f:
                LOCALIZATION_DATA[from_identifier(lan[:-5])] = json.loads(f.read())
                logger.debug(f"Loaded language {lan[:-5]} from {lan}")
    logger.success("Localization initialization successful.")


def localized(_i: str, locale: Locale) -> str:
    path = _i.split(".")
    a = LOCALIZATION_DATA[locale].copy()
    for i in path:
        a = a[i]
    if isinstance(a, list):
        return random.choice(a)
    return a


def localized_command_description(cmd: str) -> disnake.Localized:
    data = {}
    for k, v in LOCALIZATION_DATA.items():
        if k.value.discord_locale is not None:
            data[k.value.discord_locale] = (
                v.get("commands").get(cmd).get("commandDescription")
            )
    logger.debug(data)
    return disnake.Localized(data=data)


def localized_argument_description(cmd: str, argument_name: str) -> disnake.Localised:
    data = {}
    for k, v in LOCALIZATION_DATA.items():
        if k.value.discord_locale is not None:
            data[k.value.discord_locale] = (
                v.get("commands").get(cmd).get("argumentDescription").get(argument_name)
            )
    logger.debug(data)
    return disnake.Localized(data=data)
