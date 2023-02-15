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
import disnake
from disnake.ext import commands

import cfgman


class AntiClog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if cfgman.get("modules.antiClog.enabled"):
            if message.author.id == self._bot.user.id:
                await message.add_reaction(cfgman.get("modules.antiClog.emoji"))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: disnake.Reaction, user: disnake.Member):
        if (
            reaction.emoji == cfgman.get("modules.antiClog.emoji")
            and reaction.count >= 3
            and cfgman.get("modules.antiClog.enabled")
        ):
            await reaction.message.delete()


def setup(bot):
    bot.add_cog(AntiClog(bot))
