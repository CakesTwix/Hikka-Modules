"""

    █▀▀ ▄▀█ █▄▀ █▀▀ █▀ ▀█▀ █░█░█ █ ▀▄▀
    █▄▄ █▀█ █░█ ██▄ ▄█ ░█░ ▀▄▀▄▀ █ █░█

    Copyleft 2022 t.me/CakesTwix                                                            
    This program is free software; you can redistribute it and/or modify 

"""

__version__ = (1, 0, 0)

# requires: aiohttp
# meta pic: https://www.seekpng.com/png/full/824-8246338_yandere-sticker-yandere-simulator-ayano-bloody.png
# meta developer: @CakesTwix

from .. import loader, utils
import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)


@loader.tds
class ImageBoardSenderMod(loader.Module):
    """Auto-posting art to your channels"""

    strings = {
        "cfg_channel": "Сhannel variable where the content will be posted",
        "cfg_tags": "Filtering art by tags",
        "name": "ImageBoardSender",
        "no_chennel": "Channel does not exist",
        "ok": "Everything is okay",
        "no_ok": "Everything not okay (not admin rights)",
    }

    rating = {"e": "Explicit 🔴", "q": "Questionable 🟡", "s": "Safe 🟢"}
    url = "https://yande.re/post.json"

    def __init__(self):
        self.config = loader.ModuleConfig(
            "CONFIG_CHANNEL",
            "@notset",
            lambda: self.strings("cfg_channel"),
            "CONFIG_TAGS",
            "",
            lambda: self.strings("cfg_tags"),
        )

        self.entity = None

    async def _init(self) -> None:
        try:
            self._task.cancel()
        except Exception:
            pass

        if self.config["CONFIG_CHANNEL"] == "@notset":
            return

        try:
            self.entity = await self._client.get_entity(self.config["CONFIG_CHANNEL"])
            params = "?tags=" + self.config["CONFIG_TAGS"]
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url + params) as get:
                    art_data = await get.json()
                    self.last_id = art_data[0]["id"]

            self._task = asyncio.ensure_future(self.send_last_arts())
        except ValueError:
            pass

    async def client_ready(self, client, db) -> None:
        self._db = db
        self._client = client

        await self._init()

    async def on_unload(self) -> None:
        try:
            self._task.cancel()
        except Exception:
            pass

    def string_builder(self, json):
        string = f"Tags : {json['tags']}\n"
        string += f'©️ : {json["author"] or "No author"}\n'
        string += f'🔗 : {json["source"] or "No source"}\n'
        string += f"Rating : {self.rating[json['rating']]}\n\n"
        string += (f"🆔 : <a href=https://yande.re/post/show/{json['id']}>{json['id']}</a>")  # fmt: skip

        return string

    async def channelcheckcmd(self, message):
        """Checking for posting rights"""
        try:
            self.entity = await self._client.get_entity(self.config["CONFIG_CHANNEL"])
        except ValueError:
            return await utils.answer(message, self.strings["no_chennel"])

        if self.entity.admin_rights is None:
            await utils.answer(message, self.strings["no_ok"])
        elif self.entity.admin_rights.post_messages:
            await utils.answer(message, self.strings["ok"])

    async def send_last_arts(self):
        """Auto-Posting"""
        while True:
            if self.entity is None:
                await asyncio.sleep(30)
                await self._init()
                continue

            params = "?tags=" + self.config["CONFIG_TAGS"]
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url + params) as get:
                    art_data = await get.json()
                    await session.close()

            for item in reversed(art_data):
                if item["id"] > self.last_id:
                    await self._client.send_file(
                        self.entity,
                        item["sample_url"],
                        caption=self.string_builder(item),
                    )

            self.last_id = art_data[0]["id"]
            await asyncio.sleep(5 * 60)
