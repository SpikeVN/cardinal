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

# Cannot ignore the trend lol

import disnake
import revChatGPT.V1

import i18n
import logger

from disnake.ext import commands
from revChatGPT.V1 import Chatbot

import cfgman

CHATGPT_BOT: Chatbot

THREADS: list[int] = []


class StopGenerationButton(disnake.ui.Button):
    def __init__(self, lang: disnake.Locale):
        super().__init__(
            style=disnake.ButtonStyle.red,
            label="■ " + i18n.localized("commands.chatgpt.stopGeneration", lang),
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.style = disnake.ButtonStyle.green
        global THREADS
        status = await interaction.original_response()
        logger.info("REMOVING...")
        THREADS.remove(status.id)
        logger.info(THREADS)


class ChatGPT(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.slash_command(
        name="chatgpt", description=i18n.localized_command_description("chatgpt")
    )
    async def chatgpt(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        prompt: str = commands.Param(
            description=i18n.localized_argument_description("chatgpt", "prompt")
        ),
    ):
        await interaction.response.defer()
        global THREADS
        bot_response = await interaction.original_response()
        THREADS.append(bot_response.id)
        logger.info(THREADS)
        user_locale = i18n.from_identifier(str(interaction.locale))
        stop_button = StopGenerationButton(user_locale)
        v = disnake.ui.View()
        v.add_item(stop_button)
        response = ""
        message_to_send = ""
        try:
            for data in CHATGPT_BOT.ask(
                prompt,
                conversation_id=CHATGPT_BOT.config.get("conversation"),
                parent_id=CHATGPT_BOT.config.get("parent_id"),
            ):
                if data["message"] != "":
                    logger.info(THREADS)
                    response = data["message"]
                    if response.count("```") % 2 != 0:
                        response += "```"
                    if bot_response.id not in THREADS:
                        message_to_send = f"""**{i18n.localized("commands.chatgpt.card.titleComplete", user_locale)}**
**{i18n.localized("commands.chatgpt.card.prompt", user_locale)}**
{prompt.replace("@everyone", "`@everyone`")}
**{i18n.localized("commands.chatgpt.card.answer", user_locale)}**
{response.replace("@everyone", "`@everyone`")}
`{i18n.localized("commands.chatgpt.error.outputCut", user_locale)}`"""
                        await interaction.edit_original_response(
                            message_to_send, view=None
                        )
                        break
                    message_to_send = f"""**{i18n.localized("commands.chatgpt.card.title", user_locale)}**
**{i18n.localized("commands.chatgpt.card.prompt", user_locale)}**
{prompt.replace("@everyone", "`@everyone`")}
**{i18n.localized("commands.chatgpt.card.answer", user_locale)}**
{response.replace("@everyone", "`@everyone`")}"""
                    await interaction.edit_original_response(message_to_send, view=v)
        except revChatGPT.V1.Error:
            await interaction.edit_original_response(
                i18n.localized("commands.chatgpt.error.noResponse", user_locale)
                + f"""
**Technical details:**
    Error: `503 Service Unavailable`
    Text: `No server is available to handle this request.`"""
            )
            return
        if bot_response.id in THREADS:
            THREADS.remove(bot_response.id)
            message_to_send = f"""**{i18n.localized("commands.chatgpt.card.titleComplete", user_locale)}**
**{i18n.localized("commands.chatgpt.card.prompt", user_locale)}**
{prompt.replace("@everyone", "`@everyone`")}
**{i18n.localized("commands.chatgpt.card.answer", user_locale)}**
{response.replace("@everyone", "`@everyone`")}"""
            await interaction.edit_original_response(message_to_send, view=None)


def setup(bot):
    global CHATGPT_BOT
    logger.info("Logging into OpenAI account...")
    CHATGPT_BOT = Chatbot(
        config={
            "email": cfgman.get("backend.openai.email"),
            "password": cfgman.get("backend.openai.password"),
        }
    )
    logger.success("Logged into OpenAI account!")
    bot.add_cog(ChatGPT(bot))
