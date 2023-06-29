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

import disnake
import i18n

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

environment = Environment(
    loader=FileSystemLoader("./templates"), autoescape=True, enable_async=True
)
template = environment.get_template("wf_lookup.html")

if not os.path.exists(os.path.join("resources", "wfsolver")):
    os.mkdir(os.path.join("resources", "wfsolver"))
    with open(
        os.path.join("resources", "wfsolver", "dictionary.json"), "w", encoding="utf8"
    ) as f:
        f.write(
            json.dumps(
                requests.get(
                    "https://github.com/ssvivian/WebstersDictionary/raw/master/dictionary.json"
                ).json()
            )
        )

with open(
    os.path.join("resources", "wfsolver", "dictionary.json"), "r", encoding="utf8"
) as f:
    tmp = json.load(f)
    WORDS = {}
    for i in tmp:
        WORDS[(i["word"].lower(), i["pos"])] = i["definitions"]


def autocomplete_word(interaction, entry) -> list[str]:
    output = []
    for w in WORDS:
        if entry in w:
            if " " not in w:
                output.append(w)
            elif "; " in w:
                a = w.split("; ")
                necessary = ""
                for word in a:
                    if entry in word:
                        necessary = word
                output.append(necessary)
        if len(output) > 4:
            break
    return output


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
            description=i18n.localized_argument_description("wfsolver", "query"),
            autocomplete=autocomplete_word,
        ),
        pos_search: str = commands.Param(
            description=i18n.localized_argument_description("wfsolver", "pos"),
            choices=list(WEBSTER_WIKITONARY_MAP.values()),
            default="*",
        ),
        max_search: int = commands.Param(
            description=i18n.localized_argument_description("wfsolver", "max"),
            default=-1,
        ),
    ):
        potential = {}
        for (w, pos), ds in WORDS.items():
            if pos_search != "*":
                if WEBSTER_WIKITONARY_MAP.get(pos, "$$") not in pos_search:
                    continue
            if query in w:
                if " " not in w:
                    if w in potential:
                        potential[w][pos] = ds
                        potential[w]["allpos"].append(pos)
                    potential[w] = {
                        "allpos": [
                            pos,
                        ],
                        pos: ds,
                    }
                elif "; " in w:
                    a = w.split("; ")
                    necessary = ""
                    for word in a:
                        if query in word:
                            necessary = word
                    if w in potential:
                        potential[necessary][pos] = ds
                        potential[necessary]["allpos"].append(pos)
                    potential[necessary] = {
                        "allpos": [
                            pos,
                        ],
                        pos: ds,
                    }
        sent_msg = []
        if max_search != -1:
            potential = potential[:max_search]
        m = await interaction.send(f"`Query OK, found {len(potential)} entries.`")
        sent_msg.append(m)

        index_length = len(str(len(potential)))
        if index_length < 5:
            index_length = 10
        print(potential)
        word_length = max([len(str(k)) for k in potential.keys()])
        if word_length < 4:
            word_length = 9
        pos_length = max([len(str(", ".join(v["allpos"]))) for v in potential.values()])
        if pos_length < 14:
            pos_length = 19
        # Python moment
        message = f"```| {'INDEX':{index_length}} | {'WORD':{word_length}} | {'PART OF SPEECH':{pos_length}} |\n"
        message += "=" * (len(message) - 4) + "\n"
        for i, (w, d) in enumerate(potential.items()):
            ap = ", ".join([WEBSTER_WIKITONARY_MAP[p] for p in d["allpos"]])
            tmpmsg = (
                f"| {i + 1:{index_length}} | {w:{word_length}} | {ap:{pos_length}} |\n"
            )
            if len(message + tmpmsg) >= 2000:
                message += "```"
                m = await interaction.channel.send(message)
                sent_msg.append(m)
                message = "```"
            message += tmpmsg
        message += "```"
        m = await interaction.channel.send(message)
        sent_msg.append(m)

        def check(x):
            if x.to_reference() is None:
                return False
            return x.to_reference().message_id in [reply.id for reply in sent_msg]

        msg = await self._bot.wait_for("message", check=check)


def setup(bot):
    bot.add_cog(WFSolver(bot))
