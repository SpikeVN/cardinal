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
