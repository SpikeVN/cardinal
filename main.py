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
import logging
import os

import disnake
from disnake.ext import commands

import cfgman
import i18n
import logger

bot = commands.Bot(
    "!c", intents=disnake.Intents.all()
)


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=disnake.Activity(
            type=disnake.ActivityType.watching, name=cfgman.get("general.activity")
        )
    )
    logger.success(f"changed Discord presence.")
    logger.info(
        f"Logged in as {bot.user.name}#{bot.user.discriminator}, ID {bot.user.id}."
    )


def load_modules():
    for m in os.listdir("modules"):
        if "__pycache__" in m:
            continue
        logger.debug(f"Trying to load {m}")
        if os.path.isdir(f"modules/{m}"):
            bot.load_extension(name=f"modules.{m}", package=f"modules")
            logger.info(f"-> Loaded module '{m}'.")
        elif m.endswith(".py"):
            bot.load_extension(name=f"modules.{m[:-3]}")
            logger.info(f"-> Loaded module '{m[:-3]}'.")


def start():
    cfgman.init_config_hive()
    logger.set_min_level(cfgman.get("logging.level"))
    logger.info("Loading localization data...")
    i18n.init_translation_database()
    i18n.check_structure(i18n.LOCALIZATION_DATA)
    logger.info("Loading modules...")
    load_modules()
    logger.debug("Testing localization...")
    logger.debug(i18n.localized("test", i18n.Locale.VIETNAMESE))
    logger.debug(i18n.localized("test", i18n.Locale.ENGLISH))
    logger.info("Starting bot...")
    bot.run(cfgman.get("general.token"))


if __name__ == "__main__":
    start()
