"""

    █▀▀ ▄▀█ █▄▀ █▀▀ █▀ ▀█▀ █░█░█ █ ▀▄▀
    █▄▄ █▀█ █░█ ██▄ ▄█ ░█░ ▀▄▀▄▀ █ █░█

    Copyleft 2022 t.me/CakesTwix                                                            
    This program is free software; you can redistribute it and/or modify 

"""

__version__ = (1, 1, 0)

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
        "no_ok": "Everything not okay (maybe not admin rights)",
        "channel_status": "<b>Channel Status</b>:",
        "channel_username": "<b>Channel username</b>:",
        "change_channel_username": "<b>Change the channel username</b>:",
        "btn_menu_change": "✍️ Change username channel",
        "btn_menu_change_input": "✍️ Enter new configuration value for this option",
        "btn_menu_update": "Update",
        "btn_menu_start": "Start",
        "btn_menu_stop": "Stop",
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
        self.last_id = 0
        self.status_loop = False

    # Check channel rights
    async def check_entity(self) -> bool:
        try:
            self.entity = await self._client.get_entity(self.config["CONFIG_CHANNEL"])
        except ValueError:
            self.entity = None
            return False

        if self.entity.admin_rights is None:
            return False
        elif self.entity.admin_rights.post_messages:
            return True

    # Just async init
    async def _init(self) -> None:
        await self.check_entity()
        try:
            self.loop__send_arts.stop()
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

            self.loop__send_arts.start()
            self.status_loop = True
        except ValueError:
            pass

    async def client_ready(self, client, db) -> None:
        self._db = db
        self._client = client

        await self._init()

    async def on_unload(self) -> None:
        try:
            self.loop__send_arts.stop()
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
            self.entity = None
            return await utils.answer(message, self.strings["no_chennel"])

        if self.entity.admin_rights is None:
            await utils.answer(message, self.strings["no_ok"])
        elif self.entity.admin_rights.post_messages:
            await utils.answer(message, self.strings["ok"])

    async def channelmenucmd(self, message):
        """Simple Menu and status"""
        string = f"{self.strings['channel_status']} {self.strings['ok'] if await self.check_entity() else self.strings['no_ok']}\n"
        string += f"{self.strings['channel_username']} {self.config['CONFIG_CHANNEL'] if self.config['CONFIG_CHANNEL'] != '@notset' else {self.strings['change_channel_username']}}"

        local_btn = [
            [
                {
                    "text": self.strings['btn_menu_change'],
                    "input": self.strings['btn_menu_change_input'],
                    "handler": self.change_channel,
                }
            ],
            [{"text": self.strings['btn_menu_update'], "callback": self.update_channel_status}],
            [
                {"text": self.strings['btn_menu_stop'], "callback": self.stop_posting}
                if self.status_loop
                else {"text": self.strings['btn_menu_start'], "callback": self.start_posting}
            ] if await self.check_entity() else [],
        ]

        await self.inline.form(
            text=string,
            message=message,
            reply_markup=local_btn,
        )

    async def change_channel(self, call, channel_username) -> None:
        self.config["CONFIG_CHANNEL"] = channel_username
        await call.edit(text="Успешно изменено", reply_markup=[self.btn[1]])

    async def update_channel_status(self, call) -> None:
        string = f"{self.strings['channel_status']} {self.strings['ok'] if await self.check_entity() else self.strings['no_ok']}\n"
        string += f"{self.strings['channel_username']} {self.config['CONFIG_CHANNEL'] if self.config['CONFIG_CHANNEL'] != '@notset' else {self.strings['change_channel_username']}}"

        local_btn = [
            [
                {
                    "text": self.strings['btn_menu_change'],
                    "input": self.strings['btn_menu_change_input'],
                    "handler": self.change_channel,
                }
            ],
            [{"text": self.strings['btn_menu_update'], "callback": self.update_channel_status}],
            [
                {"text": self.strings['btn_menu_stop'], "callback": self.stop_posting}
                if self.status_loop
                else {"text": self.strings['btn_menu_start'], "callback": self.start_posting}
            ] if await self.check_entity() else [],
        ]

        await call.edit(
            text=string,
            reply_markup=local_btn,
        )

    async def start_posting(self, call) -> None:
        self.loop__send_arts.start()
        self.status_loop = True
        await self.update_channel_status(call)

    async def stop_posting(self, call) -> None:
        self.loop__send_arts.stop()
        self.status_loop = False
        await self.update_channel_status(call)

    @loader.loop(interval=60)
    async def loop__send_arts(self):
        """Auto-Posting"""
        if not self.check_entity():
            self.loop__send_arts.stop()

        params = "?tags=" + self.config["CONFIG_TAGS"]
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + params) as get:
                art_data = await get.json()
                await session.close()

        if self.last_id == 0:
            self.last_id = art_data[0]["id"]
            return

        for item in reversed(art_data):
            if item["id"] > self.last_id:
                await self._client.send_file(
                    self.entity,
                    item["sample_url"],
                    caption=self.string_builder(item),
                )

        self.last_id = art_data[0]["id"]
        await asyncio.sleep(5 * 60)