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

# Cannot ignore the trend lol

import disnake
import i18n
import logger

from disnake.ext import commands
from revChatGPT.V1 import Chatbot

import cfgman

CHATGPT_BOT : Chatbot


class ChatGPT(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.slash_command(
        name="chatgpt", description=i18n.localized_command_description("chatgpt")
    )
    async def chatgpt(
        self,
        interaction: disnake.UserCommandInteraction,
        prompt: str = commands.Param(
            description=i18n.localized_argument_description("chatgpt", "prompt")
        ),
        private: bool = commands.Param(
            description=i18n.localized_argument_description("chatgpt", "private")
        )
    ):
        await interaction.response.defer(ephemeral=private)

        for data in CHATGPT_BOT.ask(
            prompt,
            conversation_id=CHATGPT_BOT.config.get("conversation"),
            parent_id=CHATGPT_BOT.config.get("parent_id"),
        ):
            if data["message"] != "":
                await interaction.edit_original_response(data["message"])


def setup(bot):
    global CHATGPT_BOT
    logger.info("Logging into OpenAI account...")
    CHATGPT_BOT = Chatbot(config={"email": cfgman.get("backend.openai.email"), "password": cfgman.get("backend.openai.password")})
    logger.success("Logged in!")
    bot.add_cog(ChatGPT(bot))
