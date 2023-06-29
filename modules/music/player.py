#  Copyright (c) 2022-2023  SpikeBonjour
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import asyncio

import disnake

import i18n
from . import manager, widgets


FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


def play_next(
    client: disnake.VoiceClient,
    interaction: disnake.Interaction,
    loop: asyncio.AbstractEventLoop,
):
    async def disconnection_seq(locale: i18n.LocaleType):
        await client.disconnect()
        await interaction.send(
            i18n.translated_string("commands.music.queueEndDisconnect", locale)
        )

    def play_next_song(err):
        manager.complete_song(client.channel)
        if not manager.is_empty(client.channel):
            asyncio.run_coroutine_threadsafe(
                interaction.send(
                    embed=widgets.make_embed(
                        manager.get_queue(client.channel)[0],
                        interaction.author,
                        interaction.locale,
                    )
                ),
                loop,
            )
            client.play(
                disnake.FFmpegPCMAudio(
                    manager.get_queue(client.channel)[0].stream_url, **FFMPEG_OPTIONS
                ),
                after=play_next_song,
            )
        else:
            asyncio.run_coroutine_threadsafe(
                disconnection_seq(interaction.locale), loop
            )

    if not manager.is_empty(client.channel):
        asyncio.run_coroutine_threadsafe(
            interaction.send(
                i18n.translated_string("commands.music.actions.nowPlaying", interaction.locale),
                embed=widgets.make_embed(
                    manager.get_queue(client.channel)[0],
                    interaction.author,
                    interaction.locale,
                ),
            ),
            loop,
        )
        client.play(
            disnake.FFmpegPCMAudio(
                manager.get_queue(client.channel)[0].stream_url, **FFMPEG_OPTIONS
            ),
            after=play_next_song,
        )
    else:
        asyncio.run_coroutine_threadsafe(disconnection_seq(interaction.locale), loop)
