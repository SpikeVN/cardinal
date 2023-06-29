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
from disnake import ui

import logger
from security import safe_format
from . import manager, player

import i18n
from .video_search import Song


FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


def make_embed(
    song: Song, author: disnake.Member, locale: i18n.LocaleType
) -> disnake.Embed:
    output = disnake.Embed(
        title=song.song_name,
        description=song.description[:50] + "...",
        url=song.song_url,
        color=disnake.Color.red(),
    )
    output.set_thumbnail(song.thumbnail_url)
    output.add_field(
        i18n.translated_string("commands.music.card.likeDislike", locale),
        f"{song.likes}👍/{song.dislikes}👎",
    )
    output.add_field(
        i18n.translated_string("commands.music.card.channel", locale),
        f"[{song.author_name}]({song.author_url})",
    )
    output.add_field(
        i18n.translated_string("commands.music.card.views", locale), song.views
    )
    output.add_field(
        i18n.translated_string("commands.music.card.duration", locale),
        str(song.duration),
    )
    logger.info(song.upload_date)
    output.add_field(
        i18n.translated_string("commands.music.card.uploadDate", locale),
        song.upload_date.strftime("%d/%m/%y"),
    )
    if author.avatar is not None:
        output.set_footer(
            text=safe_format(
                i18n.translated_string("commands.music.card.requestedTemplate", locale),
                name=author.display_name,
            ),
            icon_url=author.avatar.url,
        )
    else:
        output.set_footer(
            text=safe_format(
                i18n.translated_string("commands.music.card.requestedTemplate", locale),
                name=author.display_name,
            ),
        )
    return output


def _lim_len(song: Song) -> str:
    if len(song.song_name) > 30:
        name = song.song_name[:30]
    else:
        name = song.song_name
    return f"{song.author_name} - {name}"


class SongChooser(ui.StringSelect):
    def __init__(self, songs: list[Song], locale: i18n.LocaleType):
        super().__init__()
        self.placeholder = i18n.translated_string(
            "commands.music.chooserPlaceholder", locale
        )
        self.songs = songs
        for i, s in enumerate(songs):
            self.add_option(label=_lim_len(s), value=str(i))

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.pong()
        song = self.songs[int(self.values[0])]
        v = disnake.ui.View()
        ok = SongPlayButton(interaction.locale, song)
        self.placeholder = song.song_name
        v.add_item(self)
        v.add_item(ok)

        await interaction.response.edit_message(
            embed=make_embed(song, interaction.author, interaction.locale),
            view=v,
        )


class SongPlayButton(disnake.ui.Button):
    def __init__(self, lang: i18n.LocaleType, choice: Song = None):
        super().__init__(
            style=disnake.ButtonStyle.green,
            label=i18n.translated_string("commands.music.playButton", lang),
        )
        self.lang = lang
        self.choice = choice

    async def callback(self, interaction: disnake.MessageInteraction):
        channel = interaction.author.voice.channel
        manager.add_song(channel, self.choice)
        client = await manager.connect_to(channel)
        if not (client.is_playing() or client.is_paused()):
            player.play_next(client, interaction, asyncio.get_event_loop())
        else:
            await interaction.response.edit_message(
                i18n.translated_string(
                    "commands.music.actions.addedQueue", interaction.locale
                ),
                embed=make_embed(
                    self.choice,
                    interaction.author,
                    interaction.locale,
                ),
                view=None,
            )
