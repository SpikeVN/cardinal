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


"""
Apes localization engine.
"""

import json
import os
import random
import typing

import logger
from .abc import *
from .checker import check_structure

LOCALIZATION_DATA: dict[Locale, dict[str, dict]] = {}
LocaleType = Locale | disnake.Locale


def init_translation_database():
    logger.info("Initializing localization database...")
    global LOCALIZATION_DATA
    for lan in os.listdir("i18n/translations"):
        if lan.endswith(".json"):
            with open(f"i18n/translations/{lan}", "r", encoding="utf8") as f:
                LOCALIZATION_DATA[get_locale(lan[:-5])] = json.loads(f.read())
                logger.debug(f"Loaded language {lan[:-5]} from {lan}")
    logger.success("Localization initialization successful.")


def translated_string(_i: str, locale: LocaleType) -> str:
    path = _i.split(".")
    loc = locale if isinstance(locale, Locale) else abc.get_locale(locale)
    a = LOCALIZATION_DATA[loc].copy()
    for i in path:
        a = a[i]
    if isinstance(a, list):
        return random.choice(a)
    return a  # type: ignore


def localized_command_description(cmd: str) -> disnake.Localized:
    data = {}
    for k, v in LOCALIZATION_DATA.items():
        if k.value.discord_locale is not None:
            data[k.value.discord_locale] = (
                v.get("commands").get(cmd).get("commandDescription")
            )
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
