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
import json

import aiohttp
import random
import string
from requests_toolbelt import MultipartEncoder

import logger

URL_BASE = "https://huggingface.co"


class AIChatChannel:
    def __init__(self, session, uid: str):
        self.session = session
        self.uid = uid
        self.url = f"https://huggingface.co/chat/conversation/{uid}"

    async def ask(
        self,
        message: str,
        temperature: float = 0.9,
        top_p: float = 0.95,
        repetition_penalty: float = 1.2,
        top_k: int = 50,
        truncate: int = 1024,
        watermark: bool = False,
        max_new_tokens: int = 1024,
    ):
        async with self.session.post(
            url=self.url,
            json={
                "inputs": message,
                "parameters": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "repetition_penalty": repetition_penalty,
                    "top_k": top_k,
                    "truncate": truncate,
                    "watermark": watermark,
                    "max_new_tokens": max_new_tokens,
                    "stop": ["<|endoftext|>"],
                    "return_full_text": False,
                },
                "stream": True,
                "options": {"use_cache": False},
            }
        ) as r:
            r: aiohttp.ClientResponse
            if r.status != 200:
                raise Exception("Failed to send message")

            async for chunk in r.content.iter_chunks():
                d = chunk[0].decode("utf-8")
                if chunk[1]:
                    try:
                        d = json.loads(chunk[0][5:].strip())
                        if "error" not in d:
                            yield d["token"]["text"].replace("</s>", "")
                        else:
                            print("error: ", d["error"])
                            break
                    except json.decoder.JSONDecodeError:
                        # sometimes the response is not valid json
                        # like b''
                        pass


class AIChatManager:
    def __init__(self, model: str = None):
        self.chats = {}
        self.session: aiohttp.ClientSession | None = None
        self.model = (
            "OpenAssistant/oasst-sft-6-llama-30b-xor" if model is None else model
        )
        self.accepted_welcome_modal = False

    async def connect(self):
        logger.debug("Establishing connection to HuggingChat...")
        self.session = aiohttp.ClientSession()
        logger.debug("Connected!")

    async def get_chat(self, cid: int = None) -> AIChatChannel:

        if self.chats.get(cid) is None:
            logger.debug("Creating new channel...")
            self.chats[cid] = await self.new_chat()
            logger.debug(f"New channel created with id {self.chats[cid].uid}")
        return self.chats[cid]

    async def new_chat(self) -> AIChatChannel:
        if not self.accepted_welcome_modal:
            logger.debug("Bypassing welcome modal...")
            boundary = "----WebKitFormBoundary" + "".join(
                random.sample(string.ascii_letters + string.digits, 16)
            )
            headers = {
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Origin": URL_BASE,
                "Referer": URL_BASE + "/chat/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.64",
                "Accept": "application/json",
            }
            welcome_modal_fields = {
                "ethicsModalAccepted": "true",
                "shareConversationsWithModelAuthors": "true",
                "ethicsModalAcceptedAt": "",
                "activeModel": self.model,
            }
            m = MultipartEncoder(fields=welcome_modal_fields, boundary=boundary)
            _ = await self.session.post(
                URL_BASE + "/chat/settings", headers=headers, data=m.to_string()
            )
            self.accepted_welcome_modal = True
            logger.debug("Bypassed welcome modal.")

        logger.debug("Making request...")
        r = await self.session.post(
            url="https://huggingface.co/chat/conversation",
            json={"model": self.model},
            headers={"Content-Type": "application/json"},
        )
        if r.status != 200:
            raise Exception(f"Failed to create new conversation: {r.json}")
        else:
            logger.debug("Request success.")
            j = await r.json()
            return AIChatChannel(self.session, j["conversationId"])

    async def disconnect(self):
        await self.session.close()


async def main():
    a = AIChatManager()
    await a.connect()
    chat = await a.get_chat()
    async for i in chat.ask("What is one plus one?"):
        print(i, end="")

    await a.disconnect()


if __name__ == "__main__":
    logger.set_min_level("debug")
    asyncio.run(main())
