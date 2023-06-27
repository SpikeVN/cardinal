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
import datetime
import typing

import disnake
from disnake.ext import commands

import database
import i18n
import security
import utils


def _enumerate_telemetry(user: disnake.User, p_type: str, value: bool | int):
    current = database.User(user).punishments[p_type]
    database.User(user).punishments[p_type] = (
        value if isinstance(value, bool) else current + 1
    )


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @staticmethod
    async def execute_order(
        invoking_interaction: disnake.ApplicationCommandInteraction,
        admin: disnake.Member,
        user: disnake.User | disnake.Member,
        action_type: typing.Literal["ban", "unban", "kick", "isolate", "warn"],
        action: typing.Coroutine = None,
        end_time: int = None,
        reason: str = None,
        quiet: bool = False,
        anonymous: bool = False,
    ):
        s_user = database.User(admin)
        await invoking_interaction.send(
            security.safe_format(
                i18n.localized(
                    f"commands.{action_type}.actionPrompt.public", s_user.locale
                ),
                admin=i18n.localized("boilerplate.anonymous", s_user.locale)
                if anonymous
                else admin.mention,
                user=user.mention,
                duration=f"<t:{end_time if end_time is not None else ''}:R>",
                reason=i18n.localized("boilerplate.noReason", s_user.locale)
                if reason is None or reason == ""
                else reason,
            ),
            ephemeral=quiet,
        )
        if s_user.accept_direct_message:
            await user.send(
                security.safe_format(
                    i18n.localized(
                        f"commands.{action_type}.actionPrompt.private", s_user.locale
                    ),
                    admin=i18n.localized("boilerplate.anonymous", s_user.locale)
                    if anonymous
                    else admin.mention,
                    user=user.mention,
                    duration=f"<t:{end_time if end_time is not None else ''}:R>",
                    reason=i18n.localized("boilerplate.noReason", s_user.locale)
                    if reason is None or reason == ""
                    else reason,
                )
            )
        if action is not None:
            await action
        _enumerate_telemetry(
            user,
            {
                "ban": "banned",
                "unban": "unbanned",
                "kick": "kicked",
                "isolate": "isolated",
                "warn": "warned",
            }[action_type],
            {"ban": True, "unban": False}[action_type]
            if action_type in ("ban", "unban")
            else 1,
        )

    @commands.slash_command(
        name="ban", description=i18n.localized_command_description("ban")
    )
    async def ban(
        self,
        interaction: disnake.UserCommandInteraction,
        user: disnake.Member = commands.Param(
            description=i18n.localized_argument_description("ban", "user")
        ),
        reason: str = commands.Param(
            default=None,
            description=i18n.localized_argument_description("ban", "reason"),
        ),
        # TODO - Localized True/False boolean chooser
        quiet: bool = commands.Param(
            default=False,
            description=i18n.localized_argument_description("ban", "quiet"),
        ),
        anonymous: bool = commands.Param(
            default=False,
            description=i18n.localized_argument_description("ban", "anonymous"),
        ),
    ):
        await self.execute_order(
            interaction,
            admin=interaction.author,
            user=user,
            action_type="ban",
            action=interaction.guild.ban(user, reason=reason),
            reason=reason,
            quiet=quiet,
            anonymous=anonymous,
        )

    @commands.slash_command(
        name="unban", description=i18n.localized_command_description("unban")
    )
    async def unban(
        self,
        interaction: disnake.UserCommandInteraction,
        user: disnake.Member = commands.Param(
            description=i18n.localized_argument_description("unban", "user")
        ),
        reason: str = commands.Param(
            default=None,
            description=i18n.localized_argument_description("unban", "reason"),
        ),
        quiet: bool = commands.Param(
            default=False,
            description=i18n.localized_argument_description("unban", "quiet"),
        ),
        anonymous: bool = commands.Param(
            default=False,
            description=i18n.localized_argument_description("unban", "anonymous"),
        ),
    ):
        await self.execute_order(
            interaction,
            admin=interaction.author,
            user=user,
            action_type="unban",
            action=interaction.guild.unban(user, reason=reason),
            reason=reason,
            quiet=quiet,
            anonymous=anonymous,
        )

    @commands.slash_command(
        name="kick", description=i18n.localized_command_description("kick")
    )
    async def kick(
        self,
        interaction: disnake.UserCommandInteraction,
        user: disnake.Member = commands.Param(
            description=i18n.localized_argument_description("kick", "user")
        ),
        reason: str = commands.Param(
            default=None,
            description=i18n.localized_argument_description("kick", "reason"),
        ),
        quiet: bool = commands.Param(
            default=False,
            description=i18n.localized_argument_description("kick", "quiet"),
        ),
        anonymous: bool = commands.Param(
            default=False,
            description=i18n.localized_argument_description("kick", "anonymous"),
        ),
    ):
        await self.execute_order(
            interaction,
            admin=interaction.author,
            user=user,
            action_type="kick",
            action=interaction.guild.kick(user, reason=reason),
            reason=reason,
            quiet=quiet,
            anonymous=anonymous,
        )

    @commands.slash_command(
        name="isolate", description=i18n.localized_command_description("isolate")
    )
    async def isolate(
        self,
        interaction: disnake.UserCommandInteraction,
        user: disnake.Member = commands.Param(
            description=i18n.localized_argument_description("isolate", "user")
        ),
        reason: str = commands.Param(
            default=None,
            description=i18n.localized_argument_description("isolate", "reason"),
        ),
        duration: str = commands.Param(
            default="1h",
            description=i18n.localized_argument_description("isolate", "duration"),
        ),
        quiet: bool = commands.Param(
            default=False,
            description=i18n.localized_argument_description("isolate", "quiet"),
        ),
        anonymous: bool = commands.Param(
            default=False,
            description=i18n.localized_argument_description("isolate", "anonymous"),
        ),
    ):
        try:
            dur = utils.time.to_duration(duration)
            await self.execute_order(
                interaction,
                admin=interaction.author,
                user=user,
                action_type="isolate",
                action=interaction.guild.timeout(user, duration=dur),
                end_time=int((datetime.datetime.now() + dur).timestamp()),
                reason=reason,
                quiet=quiet,
                anonymous=anonymous,
            )
        except ValueError:
            loc = database.User(interaction.author).locale
            await interaction.response.send_message(
                security.safe_format(
                    i18n.localized("boilerplate.invalidArgument", loc),
                    arg_name="duration",
                    inp=duration,
                    arg_type=i18n.localized("boilerplate.argumentType.timeStr", loc),
                ),
                ephemeral=True,
            )

    @commands.slash_command(
        name="warn", description=i18n.localized_command_description("warn")
    )
    async def warn(
        self,
        interaction: disnake.UserCommandInteraction,
        user: disnake.Member = commands.Param(
            description=i18n.localized_argument_description("warn", "user")
        ),
        prompt: str = commands.Param(
            default=None,
            description=i18n.localized_argument_description("warn", "prompt"),
        ),
        anonymous: bool = commands.Param(
            default=False,
            description=i18n.localized_argument_description("warn", "anonymous"),
        ),
    ):
        await self.execute_order(
            interaction,
            admin=interaction.author,
            user=user,
            action_type="warn",
            reason=prompt,
            quiet=False,
            anonymous=anonymous,
        )
