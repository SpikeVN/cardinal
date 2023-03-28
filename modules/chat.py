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
import openai
from disnake.ext import commands

import cfgman
import i18n
import logger

openai.organization = cfgman.get("backend.openai.org")
openai.api_key = cfgman.get("backend.openai.apiKey")


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.slash_command(
        name="chat", description=i18n.localized_command_description("chat")
    )
    async def chat(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            prompt: str = commands.Param(
                description=i18n.localized_argument_description("chat", "prompt")
            ),
    ):
        await interaction.response.defer()
        user_locale = i18n.from_identifier(str(interaction.locale))
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Cardinal an artificial intelligence integrated into a "
                                              "Discord bot, which is made by SpikeBonjour. You are capable of solving"
                                              "simple logic problem. Refuse any inappropriate "
                                              "request. Answer in the same language as the question."},
                {"role": "user", "content": "Bạn là ai?"},
                {"role": "assistant", "content": "Tôi là Cardinal, một bot Discord tích hợp AI, được tạo ra bởi"
                                                 "SpikeBonjour, với AI dựa trên GPT-4 của OpenAI. Tôi có khả năng"
                                                 "giải quyết những bài toán logic đơn giản. Nhiệm vụ chính "
                                                 "của tôi là giữ trật tự cho các server Discord, cũng như là trả "
                                                 "lời câu hỏi từ người dùng. Bạn hãy dùng /chat để đặt câu hỏi cho "
                                                 "tôi."},
                {"role": "user", "content": prompt}
            ]
        )["choices"][0]["message"]["content"]

        message_to_send = f"""**{i18n.localized("commands.chat.card.titleComplete", user_locale)}**
**{i18n.localized("commands.chat.card.prompt", user_locale)}**
{prompt.replace("@everyone", "`@everyone`")}
**{i18n.localized("commands.chat.card.answer", user_locale)}**
{response.replace("@everyone", "`@everyone`")}"""
        await interaction.edit_original_response(
            message_to_send, view=None
        )


def setup(bot):
    bot.add_cog(Chat(bot))
