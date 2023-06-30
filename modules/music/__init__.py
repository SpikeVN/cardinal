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
import datetime

import disnake

from disnake.ext import commands, tasks

import i18n
from . import manager, player
from .video_search import Song, search, get
from .widgets import SongChooser


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot
        self.playtime_counter.start()

    @commands.slash_command(name="music")
    async def music(self, interaction):
        pass

    @music.sub_command(
        name="play", description=i18n.localized_command_description("music_play")
    )
    async def play(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        query_or_url: str = commands.Param(
            description=i18n.localized_argument_description(
                "music_play", "query_or_url"
            )
        ),
    ):
        if (
            not isinstance(interaction.author, disnake.Member)
            or interaction.author.voice is None
        ):
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notInVoice", interaction.locale
                )
            )
            return
        await interaction.response.defer()
        if "youtube.com/watch?v=" in query_or_url or "youtu.be/" in query_or_url:
            url = query_or_url.replace("youtu.be/", "youtube.com/watch?v=")
            vid = await video_search.get(url)
            manager.add_song(interaction.author.voice.channel, vid)
            client = await manager.connect_to(interaction.author.voice.channel)
            if not (client.is_playing() or client.is_paused()):
                player.play_next(client, interaction, asyncio.get_event_loop())
            else:
                await interaction.send(
                    "Added to queue:",
                    embed=widgets.make_embed(
                        vid,
                        interaction.author,
                        interaction.locale,
                    ),
                )
        else:
            result = await search(query_or_url)
            v = disnake.ui.View()
            v.add_item(SongChooser(result, interaction.locale))
            await interaction.edit_original_response(view=v)

    @music.sub_command(
        name="pause", description=i18n.localized_command_description("music_pause")
    )
    async def pause(self, interaction: disnake.ApplicationCommandInteraction):
        if (
            not isinstance(interaction.author, disnake.Member)
            or interaction.author.voice is None
        ):
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notInVoice", interaction.locale
                )
            )
            return
        channel = interaction.author.voice.channel
        if channel.id not in manager.managed_channels():
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notPlaying", interaction.locale
                )
            )
            return
        if manager.get_client(channel) is None:
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notPlaying", interaction.locale
                )
            )
            return
        client = manager.get_client(channel)
        if client.is_paused():
            client.resume()
            await interaction.send(
                i18n.translated_string("commands.music.resumed", interaction.locale)
            )
        else:
            client.pause()
            await interaction.send(
                i18n.translated_string("commands.music.paused", interaction.locale)
            )

    @music.sub_command(
        name="stop", description=i18n.localized_command_description("music_stop")
    )
    async def stop(self, interaction: disnake.ApplicationCommandInteraction):
        if (
            not isinstance(interaction.author, disnake.Member)
            or interaction.author.voice is None
        ):
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notInVoice", interaction.locale
                )
            )
            return
        channel = interaction.author.voice.channel
        if channel.id not in manager.managed_channels():
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notPlaying", interaction.locale
                )
            )
            return
        if manager.get_client(channel) is None:
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notPlaying", interaction.locale
                )
            )
            return
        client = manager.get_client(channel)
        if client.is_playing():
            client.stop()
            await client.disconnect()
            manager.remove_player(channel)
            await interaction.send("Playback stopped.")
        else:
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notPlaying", interaction.locale
                )
            )

    @music.sub_command(
        name="status", description=i18n.localized_command_description("music_status")
    )
    async def status(self, interaction: disnake.ApplicationCommandInteraction):
        if (
            not isinstance(interaction.author, disnake.Member)
            or interaction.author.voice is None
        ):
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notInVoice", interaction.locale
                )
            )
            return
        channel = interaction.author.voice.channel
        if channel.id not in manager.managed_channels():
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notPlaying", interaction.locale
                )
            )
            return
        if manager.get_client(channel) is None:
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notPlaying", interaction.locale
                )
            )
            return
        current_song = manager.get_queue(channel)[0]
        answer = disnake.Embed(
            color=disnake.Color.red(),
            title=current_song.song_name,
            url=current_song.song_url,
        )
        answer.add_field(
            name=i18n.translated_string("commands.music.status", interaction.locale),
            value=f"{datetime.timedelta(seconds=manager.get_playtime(channel))}/{current_song.duration}",
        )
        await interaction.send(embed=answer)

    @music.sub_command(
        name="skip", description=i18n.localized_command_description("music_skip")
    )
    async def skip(self, interaction: disnake.ApplicationCommandInteraction):
        if (
            not isinstance(interaction.author, disnake.Member)
            or interaction.author.voice is None
        ):
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notInVoice", interaction.locale
                )
            )
            return
        channel = interaction.author.voice.channel
        if channel.id not in manager.managed_channels():
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notPlaying", interaction.locale
                )
            )
            return
        if manager.get_client(channel) is None:
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notPlaying", interaction.locale
                )
            )
            return
        client = manager.get_client(channel)
        client.stop()
        if manager.is_empty(channel):
            await client.disconnect()
            await interaction.send(
                i18n.translated_string(
                    "commands.music.queueEndDisconnect", interaction.locale
                )
            )

    @music.sub_command(
        name="list", description=i18n.localized_command_description("music_list")
    )
    async def list(self, interaction: disnake.ApplicationCommandInteraction):
        if (
            not isinstance(interaction.author, disnake.Member)
            or interaction.author.voice is None
        ):
            await interaction.send(
                i18n.translated_string(
                    "commands.music.error.notInVoice", interaction.locale
                )
            )
            return
        q = manager.get_queue(interaction.author.voice.channel)
        r = "```\n"
        for i, s in enumerate(q):
            r += f"#{i+1}: {s.author_name} - {s.song_name} ({s.duration})\n"
        r += "```"
        await interaction.response.send_mesage(r)

    def cog_unload(self) -> None:
        self.playtime_counter.cancel()

    @tasks.loop(seconds=1)
    async def playtime_counter(self):
        for data in manager.get_storage().values():
            if data["client"] is not None and data["client"].is_playing():
                data["playtime"] += 1


def setup(bot):
    bot.add_cog(Music(bot))
