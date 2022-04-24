"""

    █▀▀ ▄▀█ █▄▀ █▀▀ █▀ ▀█▀ █░█░█ █ ▀▄▀
    █▄▄ █▀█ █░█ ██▄ ▄█ ░█░ ▀▄▀▄▀ █ █░█

    Copyleft 2022 t.me/CakesTwix                                                            
    This program is free software; you can redistribute it and/or modify 

"""

__version__ = (1, 2, 2)

# requires: aiohttp
# meta pic: https://www.seekpng.com/png/full/824-8246338_yandere-sticker-yandere-simulator-ayano-bloody.png
# meta developer: @CakesTwix
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.1.2

from .. import loader, utils
import aiohttp
import asyncio
import logging
import ast
import telethon

logger = logging.getLogger(__name__)


def rating_string(rating_list: list) -> str:
    rating_str = ["s", "q", "e"]
    if sum(rating_list) == 2:
        return (
            "-rating:"
            + rating_str[[i for i, val in enumerate(rating_list) if not val][0]]
        )
    elif sum(rating_list) == 1:
        return (
            "rating:" + rating_str[[i for i, val in enumerate(rating_list) if val][0]]
        )
    else:
        return ""


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
        "channel_tags": "<b>Channel tags</b>:",
        "channel_no_tags": "no tags",
        "change_channel_username": "<b>Change the channel username</b>",
        "btn_menu_change_channel": "✍️ Change username channel",
        "btn_menu_change_tags": "✍️ Change tags",
        "btn_menu_change_input": "✍️ Enter new configuration value for this option",
        "btn_menu_update": "Update",
        "btn_menu_start": "Start",
        "btn_menu_stop": "Stop",
        "btn_menu_Safe": "Safe",
        "btn_menu_Questionable": "Questionable",
        "btn_menu_Explicit": "Explicit",
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

    # Check channel rights
    async def check_entity(self) -> bool:
        try:
            self.entity = await self._client.get_entity(self.config["CONFIG_CHANNEL"])
            if not isinstance(self.entity, telethon.types.Channel):
                self.entity = None
                return False
        except ValueError:
            self.entity = None
            return False

        if self.entity.admin_rights is None:
            return False
        elif self.entity.admin_rights.post_messages:
            return True

    async def menu_keyboard(self) -> list:
        return [
            [
                {
                    "text": self.strings["btn_menu_change_channel"],
                    "input": self.strings["btn_menu_change_input"],
                    "handler": self.change_config,
                    "args": ("CONFIG_CHANNEL",),
                },
                {
                    "text": self.strings["btn_menu_change_tags"],
                    "input": self.strings["btn_menu_change_input"],
                    "handler": self.change_config,
                    "args": ("CONFIG_TAGS",),
                },
            ],
            [
                {
                    "text": f"[ {self.strings['btn_menu_Safe']} ]"
                    if self._db.get(self.strings["name"], "rating")[0]
                    else self.strings["btn_menu_Safe"],
                    "callback": self.set_rating,
                    "args": ("s"),
                },
                {
                    "text": f"[ {self.strings['btn_menu_Questionable']} ]"
                    if self._db.get(self.strings["name"], "rating")[1]
                    else self.strings["btn_menu_Questionable"],
                    "callback": self.set_rating,
                    "args": ("q"),
                },
                {
                    "text": f"[ {self.strings['btn_menu_Explicit']} ]"
                    if self._db.get(self.strings["name"], "rating")[2]
                    else self.strings["btn_menu_Explicit"],
                    "callback": self.set_rating,
                    "args": ("e"),
                },
            ]
            if await self.check_entity()
            else [],
            [
                {
                    "text": self.strings["btn_menu_update"],
                    "callback": self.update_channel_status,
                }
            ]
            if await self.check_entity()
            else [],
            [
                {"text": self.strings["btn_menu_stop"], "callback": self.stop_posting}
                if self.loop__send_arts.status
                else {
                    "text": self.strings["btn_menu_start"],
                    "callback": self.start_posting,
                }
            ]
            if await self.check_entity()
            else [],
        ]

    # Just async init
    async def _init(self) -> None:
        await self.check_entity()
        try:
            self.loop__send_arts.stop()
        except Exception:
            pass

        if self.config["CONFIG_CHANNEL"] == "@notset":
            return

        self.entity = await self._client.get_entity(self.config["CONFIG_CHANNEL"])
        params = (
            "?tags="
            + rating_string(self._db.get(self.strings["name"], "rating"))
            + self.config["CONFIG_TAGS"]
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + params) as get:
                art_data = await get.json()
                self.last_id = art_data[0]["id"]

        self.loop__send_arts.start()

    async def client_ready(self, client, db) -> None:
        self._db = db
        self._client = client

        if self._db.get(self.strings["name"], "rating") is None:
            self._db.set(self.strings["name"], "rating", [False, False, False])

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

    async def channelmenucmd(self, message):
        """Simple Menu and status"""
        string = f"{self.strings['channel_status']} {self.strings['ok'] if await self.check_entity() else self.strings['no_ok']}\n"
        string += f"{self.strings['channel_username']} {self.config['CONFIG_CHANNEL'] if self.config['CONFIG_CHANNEL'] != '@notset' else self.strings['change_channel_username']}\n"
        string += f"{self.strings['channel_tags']} {self.config['CONFIG_TAGS'] if self.config['CONFIG_TAGS'] != '' else self.strings['channel_no_tags']}\n"

        await self.inline.form(
            text=string,
            message=message,
            reply_markup=await self.menu_keyboard(),
        )

    # From Hikka https://github.com/hikariatama/Hikka/blob/d3144fcebdbc8ecbec7f3d299cc927bb1fea00b6/hikka/modules/hikka_config.py#L51-L80
    async def change_config(self, call, param, config_name) -> None:
        for module in self.allmodules.modules:
            if module.strings("name") == self.strings["name"]:
                module.config[config_name] = param

                if param:
                    try:
                        param = ast.literal_eval(param)
                    except (ValueError, SyntaxError):
                        pass

                    self._db.setdefault(module.__class__.__name__, {}).setdefault(
                        "__config__", {}
                    )[config_name] = param
                else:
                    try:
                        del self._db.setdefault(
                            module.__class__.__name__, {}
                        ).setdefault("__config__", {})[config_name]
                    except KeyError:
                        pass

                self.allmodules.send_config_one(module, self._db, skip_hook=True)
                self._db.save()

        await call.edit(
            text="Успешно изменено",
            reply_markup=[
                {
                    "text": self.strings["btn_menu_update"],
                    "callback": self.update_channel_status,
                }
            ],
        )

    async def update_channel_status(self, call) -> None:
        string = f"{self.strings['channel_status']} {self.strings['ok'] if await self.check_entity() else self.strings['no_ok']}\n"
        string += f"{self.strings['channel_username']} {self.config['CONFIG_CHANNEL'] if self.config['CONFIG_CHANNEL'] != '@notset' else self.strings['change_channel_username']}\n"
        string += f"{self.strings['channel_tags']} {self.config['CONFIG_TAGS'] if self.config['CONFIG_TAGS'] != '' else self.strings['channel_no_tags']}\n"

        await call.edit(
            text=string,
            reply_markup=await self.menu_keyboard(),
        )

    async def set_rating(self, call, rating) -> None:
        list_rating = self._db.get(self.strings["name"], "rating")
        if rating == "s":
            list_rating[0] = not list_rating[0]
            self._db.set(self.strings["name"], "rating", list_rating)
        elif rating == "q":
            list_rating[1] = not list_rating[1]
            self._db.set(self.strings["name"], "rating", list_rating)
        elif rating == "e":
            list_rating[2] = not list_rating[2]
            self._db.set(self.strings["name"], "rating", list_rating)

        await self.update_channel_status(call)

    async def start_posting(self, call) -> None:
        if not self.loop__send_arts.status:
            self.loop__send_arts.start()
            await self.update_channel_status(call)

    async def stop_posting(self, call) -> None:
        if self.loop__send_arts.status:
            self.loop__send_arts.stop()
            await self.update_channel_status(call)

    @loader.loop(interval=60)
    async def loop__send_arts(self):
        """Auto-Posting"""
        params = (
            "?tags="
            + rating_string(self._db.get(self.strings["name"], "rating"))
            + self.config["CONFIG_TAGS"]
        )
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
                await asyncio.sleep(0.5)

        self.last_id = art_data[0]["id"]
        await asyncio.sleep(5 * 60)
