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

import i18n
import logger

from disnake.ext import commands
from .cringe import transform_text


class Shitposting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.slash_command(
        name="shitpost", description=i18n.localized_command_description("shitpost")
    )
    async def shitpost(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @shitpost.sub_command(
        name="cringe", description=i18n.localized_command_description("shitpost_cringe")
    )
    async def shitpost_cringe(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        prompt: str = commands.Param(
            description=i18n.localized_argument_description("shitpost_cringe", "prompt")
        ),
    ):
        await interaction.response.send_message(transform_text(prompt))


def setup(bot):
    logger.debug("loaded")
    bot.add_cog(Shitposting(bot))
