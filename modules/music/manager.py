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
import disnake
import typing

import utils
from .video_search import Song


class MusicPlaybackEntry(typing.TypedDict):
    queue: list[Song]
    client: disnake.VoiceClient | None
    playtime: int


_STORAGE: dict[int, MusicPlaybackEntry] = {}


def add_song(channel: disnake.VoiceChannel, song: Song):
    if channel.id not in _STORAGE:
        _STORAGE[channel.id] = {"queue": [], "client": None, "playtime": 0}
    _STORAGE[channel.id]["queue"].append(song)


def get_queue(channel: disnake.VoiceChannel) -> list[Song]:
    return _STORAGE[channel.id]["queue"]


def remove_player(channel: disnake.VoiceChannel):
    _STORAGE.pop(channel.id)


def complete_song(channel: disnake.VoiceChannel):
    if channel.id not in _STORAGE:
        return
    if len(_STORAGE[channel.id]) > 0:
        _STORAGE[channel.id]["queue"].pop(0)


def is_empty(channel: disnake.VoiceChannel):
    return len(_STORAGE[channel.id]["queue"]) == 0


async def connect_to(channel: disnake.VoiceChannel) -> disnake.VoiceClient:
    if _STORAGE[channel.id]["client"] is None:
        connection = await channel.connect()
        _STORAGE[channel.id]["client"] = connection
    return _STORAGE[channel.id]["client"]


def get_client(channel: disnake.VoiceChannel) -> disnake.VoiceClient:
    return _STORAGE[channel.id]["client"]


def get_playtime(channel: disnake.VoiceChannel) -> int:
    return _STORAGE[channel.id]["playtime"]


def managed_channels() -> tuple[int]:
    return tuple(_STORAGE.keys())


def get_storage() -> dict[int, dict[str, list[Song] | disnake.VoiceClient]]:
    return _STORAGE
