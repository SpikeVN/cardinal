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
import dataclasses
import datetime
import functools

import aiohttp
import disnake
import youtube_dl as ytdl
import youtube_search


@dataclasses.dataclass
class Song:
    song_name: str
    song_url: str
    duration: datetime.timedelta
    author_name: str
    author_url: str
    upload_date: datetime.date
    thumbnail_url: str
    description: str
    likes: int
    dislikes: int
    views: int
    stream_url: str
    requester: disnake.Member = None
    request_channel: disnake.TextChannel = None


DOWNLOAD_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": "True",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}
FFMPEG_OPTIONS = {
    "before_options"
    "reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    "options"
    "vn"
}

YTDL = ytdl.YoutubeDL(DOWNLOAD_OPTIONS)


async def search(query: str) -> list[Song]:
    loop = asyncio.get_event_loop()
    result = []
    # r = await loop.run_in_executor(None, youtube_search.YoutubeSearch, query, cfgman.get("modules.music.max-search"))
    r = await loop.run_in_executor(None, youtube_search.YoutubeSearch, query, 2)
    async with aiohttp.ClientSession("https://returnyoutubedislikeapi.com") as session:
        for d in r.to_dict():
            partial = functools.partial(
                YTDL.extract_info,
                f'https://youtube.com/watch?v={d["id"]}',
                download=False,
            )
            data = await loop.run_in_executor(None, partial)
            up_date = data.get("upload_date")
            if up_date is not None:
                up_date = datetime.datetime.strptime(
                    f"{up_date[:4]}-{up_date[4:6]}-{up_date[6:]}", "%Y-%m-%d"
                ).date()
            async with session.get(f"/votes?videoId={d['id']}") as r:
                dislikes = await r.json()
                dislikes = dislikes["dislikes"]
            result.append(
                Song(
                    author_name=data.get("uploader"),
                    author_url=data.get("uploader_url"),
                    upload_date=up_date,
                    song_name=data.get("title"),
                    thumbnail_url=data.get("thumbnail"),
                    description=data.get("description"),
                    duration=datetime.timedelta(seconds=int(data.get("duration"))),
                    song_url=data.get("webpage_url"),
                    views=data.get("view_count"),
                    likes=data.get("like_count"),
                    dislikes=dislikes,
                    stream_url=data["url"],
                )
            )
        return result


async def get(url: str) -> Song:
    loop = asyncio.get_event_loop()
    async with aiohttp.ClientSession("https://returnyoutubedislikeapi.com") as session:
        partial = functools.partial(
            YTDL.extract_info,
            url,
            download=False,
        )
        data = await loop.run_in_executor(None, partial)
        up_date = data.get("upload_date")
        if up_date is not None:
            up_date = datetime.datetime.strptime(
                f"{up_date[:4]}-{up_date[4:6]}-{up_date[6:]}", "%Y-%m-%d"
            ).date()
        async with session.get(f"/votes?videoId={data.get('id')}") as r:
            dislikes = await r.json()
            dislikes = dislikes["dislikes"]
        return Song(
            author_name=data.get("uploader"),
            author_url=data.get("uploader_url"),
            upload_date=up_date,
            song_name=data.get("title"),
            thumbnail_url=data.get("thumbnail"),
            description=data.get("description"),
            duration=datetime.timedelta(seconds=int(data.get("duration"))),
            song_url=data.get("webpage_url"),
            views=data.get("view_count"),
            likes=data.get("like_count"),
            dislikes=dislikes,
            stream_url=data["url"],
        )
