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
import json
import os
import requests
import io

import disnake
import i18n
import imgkit

from jinja2 import Environment, FileSystemLoader
from disnake.ext import commands

WEBSTER_WIKITONARY_MAP = {
    "n.": "noun",
    "v.": "verb",
    "a.": "adjective",
    "adv.": "adverb",
    "conj.": "conjunction",
    "interj.": "interjection",
    "pron.": "pronoun",
    "prep.": "preposition",
}

environment = Environment(loader=FileSystemLoader("./templates"), autoescape=True, enable_async=True)
template = environment.get_template("wf_lookup.html")
with open(os.path.join("resources", "wfsolver", "dictionary.json"), "r", encoding="utf8") as f:
    tmp = json.load(f)
    WORDS = {}
    for i in tmp:
        WORDS[(i["word"].lower(), i["pos"])] = i["definitions"]


class WFSolver(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.slash_command(
        name="wf", description=i18n.localized_command_description("wfsolver")
    )
    async def wfsolver(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            query: str = commands.Param(
                description=i18n.localized_argument_description("wfsolver", "query")
            ),
            pos_search: str = commands.Param(
                description=i18n.localized_argument_description("wfsolver", "pos"),
                choices=list(WEBSTER_WIKITONARY_MAP.values()),
                default="*"
            ),
            max_search: int = commands.Param(
                description=i18n.localized_argument_description("wfsolver", "max"),
                default=-1
            ),
            experimental: bool = False
    ):
        if experimental:
            await interaction.response.defer()
        # parser = wiktionaryparser.WiktionaryParser()
        # parser.set_default_language('english')
        # parser.include_part_of_speech(pos)
        # words = parser.fetch('test')
        potential = {}
        for (w, pos), ds in WORDS.items():
            if pos_search != "*":
                if WORDS.get(pos, "$$") not in pos_search:
                    continue
            if query in w:
                if " " not in w:
                    if w in potential:
                        potential[w][pos] = ds
                        potential[w]["allpos"].append(pos)
                    potential[w] = {
                        "allpos": [pos, ],
                        pos: ds
                    }
                elif "; " in w:
                    a, b = w.split("; ")
                    if w in potential:
                        potential[a if query in a else b][pos] = ds
                        potential[a if query in a else b]["allpos"].append(pos)
                    potential[a if query in a else b] = {
                        "allpos": [pos, ],
                        pos: ds
                    }

        if max_search != -1:
            potential = potential[:max_search]
        await interaction.send(f"`Query OK, found {len(potential)} entries.`")
        if not experimental:
            index_length = len(str(len(potential)))
            if index_length < 5:
                index_length = 10
            word_length = max([len(str(k)) for k in potential.keys()])
            print(sorted(potential.keys(), key=lambda x: len(x), reverse=True))
            if word_length < 4:
                word_length = 9
            pos_length = max([len(str(", ".join(v["allpos"]))) for v in potential.values()])
            if pos_length < 14:
                pos_length = 19
            # Python moment
            message = eval(
                "f\"" +
                "```| {'INDEX':il} | {'WORD':wl} | {'PART OF SPEECH':pl} |\\n\""
                .replace("il", str(index_length))
                .replace("wl", str(word_length))
                .replace("pl", str(pos_length))
            )
            message += "="*(len(message)-4) + "\n"
            for i, (w, d) in enumerate(potential.items()):
                ap = ", ".join([WEBSTER_WIKITONARY_MAP[p] for p in d['allpos']])
                tmpmsg = eval(
                    "f\"" +
                    "| {str(i):$$il} | {w:$$wl} | {ap:$$pl} |\\n\""
                    .replace("$$il", str(index_length))
                    .replace("$$wl", str(word_length))
                    .replace("$$pl", str(pos_length))
                    .replace("str(i)", str(i+1))
                )
                if len(message + tmpmsg) >= 2000:
                    message += "```"
                    await interaction.channel.send(message)
                    message = "```"
                message += tmpmsg
            message += "```"
            await interaction.channel.send(message)
        else:
            images = []
            for _ in range(len(potential.items()) // 5):
                img = await template.render_async(words=list(enumerate(potential.items()))[:5])
                img = imgkit.from_string(img, False, {
                    'format': 'png',
                    'crop-w': '400',
                })
                for index in range(5):
                    try:
                        potential.pop(list(potential.keys())[index])
                    except KeyError:
                        pass
                images.append(img)

            if len(images) <= 10:
                await interaction.edit_original_response(
                    files=[disnake.File(io.BytesIO(img), f"result{index}.png") for index, img in enumerate(images)]
                )
            else:
                await interaction.edit_original_response(
                    files=[disnake.File(io.BytesIO(img), f"result{index}.png") for index, img in enumerate(images[:10])]
                )
                for _ in range(10):
                    images.pop()

                for _ in range(len(potential.items()) // 10):
                    await interaction.send(
                        files=[disnake.File(io.BytesIO(img), f"result{index}.png") for index, img in
                               enumerate(images[:10])]
                    )
                    for _ in range(10):
                        images.pop()


def setup(bot):
    if not os.path.exists(os.path.join("resources", "wfsolver")):
        os.mkdir(os.path.join("resources", "wfsolver"))
        with open(os.path.join("resources", "wfsolver", "dictionary.json"), "w", encoding="utf8") as f:
            f.write(
                json.dumps(
                    requests.get("https://github.com/ssvivian/WebstersDictionary/raw/master/dictionary.json").json()
                )
            )
    bot.add_cog(WFSolver(bot))
