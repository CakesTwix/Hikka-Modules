"""

    █▀▀ ▄▀█ █▄▀ █▀▀ █▀ ▀█▀ █░█░█ █ ▀▄▀
    █▄▄ █▀█ █░█ ██▄ ▄█ ░█░ ▀▄▀▄▀ █ █░█

    Copyleft 2022 t.me/CakesTwix                                                            
    This program is free software; you can redistribute it and/or modify 

"""

__version__ = (1, 0, 0)

# requires: aiohttp timeago
# meta pic: https://b.thumbs.redditmedia.com/-cDkj6PuQHqdLEhPh1JYsYplTArOOUuBnKs5FC8sgKs.png
# meta developer: @CakesTwix
# scope: inline
# scope: geektg_only

import logging
import uuid
from datetime import datetime
from typing import Union

import aiohttp
import timeago

from .. import loader, utils  # noqa

logger = logging.getLogger(__name__)


# From Hikka https://github.com/hikariatama/Hikka/blob/master/hikka/utils.py#L459-L461
def chunks(_list: Union[list, tuple, set], n: int, /) -> list:
    """Split provided `_list` into chunks of `n`"""
    return [_list[i: i + n] for i in range(0, len(_list), n)]


@loader.tds
class InlineWynnCraftInfoMod(loader.Module):
    """A module for displaying player information on the WynnCraft rpg server"""

    strings = {
        "name": "InlineWynnCraft",
        "error_message": "🚫 This entity does not exist or you entered it incorrectly",

        "about_user": "<b>Available player information</b> <code>{}</code> {}\n",
        "rank_user": "<b>Rank</b>: ",
        "last_join_user": "\n<b>Last Seen</b>: ",
        "first_join_user": "\n<b>First Join</b>: ",
        "professions_user": "\n<b>Professions</b>: ",
        "guild_user": "\n<b>Guild</b>: {} ({})",

        "general_info_user": "\n\n👉 <b>General Information</b>",
        "chestsFound": "\n  🔍 <b>Chests Found</b>: ",
        "blocksWalked": "\n  🚶‍♀️ <b>Walked blocks</b>: ",
        "mobsKilled": "\n  🐗 <b>Mobs Killed</b>: ",
        "itemsIdentified": "\n  🧰 <b>Items analyzed</b>: ",
        "logins": "\n  🎟 <b>Logins</b>: ",
        "discoveries": "\n  🔎 <b>Discoveries</b>: ",
        "dungeons": "\n  🪨 <b>Dungeons</b>: ",
        "raids": "\n  ⚔️ <b>Raids</b>: ",
        "quests": "\n  📕 <b>Quests</b>: ",
        "eventsWon": "\n  🎊 <b>Events Won</b>: ",

        "pvp_user": "\n\n🗡 <b>PVP</b>: ",
        "deaths": "\n  ☠️ <b>Deaths</b>: ",
        "kills": "\n  ⚔️ <b>Kills</b>: ",

        "completed": "\n✅ <b>Completed</b>",

        "skills": "\n\n🔧 <b>Skills</b>",
        "strength": "\n  💪 <b>Strength</b>: ",
        "dexterity": "\n  💨 <b>Dexterity</b>: ",
        "intelligence": "\n  🧐 <b>Intelligence</b>: ",
        "defense": "\n  🧱 <b>Defence</b>: ",
        "defence": "\n  🛡 <b>Defence</b>: ",
        "agility": "\n  🤸‍♂️ <b>Agility</b>: ",

        "professions": "\n\n👷‍♀️ <b>Professions</b>: ",
        "alchemism": "\n  💧 <b>Alchemism</b>: ",
        "armouring": "\n  🛡 <b>Armouring</b>: ",
        "combat": "\n  ⚔️ <b>Combat</b>: ",
        "cooking": "\n  🍽 <b>Cooking</b>: ",
        "farming": "\n  🌾️ <b>Farming</b>: ",
        "fishing": "\n  🎣 <b>Fishing</b>: ",
        "jeweling": "\n  💎 <b>Jeweling</b>: ",
        "mining": "\n  ⛏ <b>Mining</b>: ",
        "scribing": "\n  🖋 <b>Scribing</b>: ",
        "tailoring": "\n  🪡 <b>Tailoring</b>: ",
        "weaponsmithing": "\n  🗡️ <b>Weaponsmithing</b>: ",
        "woodcutting": "\n  🪓 <b>Woodcutting</b>: ",
        "woodworking": "\n  🌳️ <b>Woodworking</b>: ",

        "btn_back": "Back",
        "btn_close": "Close",
    }

    base_url = "https://mc-heads.net/minecraft/profile/"
    wynncraft_api = "https://api.wynncraft.com/v2/player/{}/stats"

    def general_info_builder(self, user) -> str:
        text = self.strings["about_user"].format(
            f'🟢 ({user["meta"]["location"]["server"]})'
            if user["meta"]["location"]["online"]
            else "🔴",
            user["username"],
        )
        text += (
                self.strings["rank_user"]
                + user["rank"]
                + (
                    f' ({user["meta"]["tag"]["value"]})'
                    if user["meta"]["tag"]["value"]
                    else ""
                )
        )

        # Guild
        text += (
            self.strings["guild_user"].format(
                user["guild"]["name"], user["guild"]["rank"]
            )
            if user["guild"]["name"]
            else ""
        )

        text += self.strings["last_join_user"] + timeago.format(
            datetime.strptime(user["meta"]["lastJoin"][:-5], "%Y-%m-%dT%H:%M:%S"),
            datetime.now(),
        )
        text += self.strings["first_join_user"] + timeago.format(
            datetime.strptime(user["meta"]["firstJoin"][:-5], "%Y-%m-%dT%H:%M:%S"),
            datetime.now(),
        )

        # Global stuff
        text += self.strings["general_info_user"]
        for general_stuff in user["global"]:
            if general_stuff in ["pvp", "totalLevel"]:
                continue
            text += (
                    self.strings[general_stuff]
                    + f"<code>{user['global'][general_stuff]}</code>"
            )

        # PvP
        text += self.strings["pvp_user"]
        text += self.strings["kills"] + f"<code>{user['global']['pvp']['kills']}</code>"
        text += (
                self.strings["deaths"] + f"<code>{user['global']['pvp']['deaths']}</code>"
        )

        return text

    def class_info_builder(self, class_) -> str:
        text = self.strings["about_user"].format(
            "".join([i for i in class_["name"].title() if not i.isdigit()]),
            f"[{class_['level']}]",
        )

        # Completed stuff
        text += self.strings["completed"]
        for some_item in class_:
            if some_item not in ["dungeons", "raids", "quests"]:
                continue

            text += (
                    self.strings[some_item]
                    + f"<code>{class_[some_item]['completed']}</code>"
            )

        # Some stuff
        text += self.strings["general_info_user"]
        for some_item in class_:
            if some_item in [
                "itemsIdentified",
                "mobsKilled",
                "chestsFound",
                "blocksWalked",
                "logins",
                "discoveries",
                "eventsWon",
            ]:
                text += self.strings[some_item] + f"<code>{class_[some_item]}</code>"

        # PvP
        text += self.strings["pvp_user"]
        text += self.strings["kills"] + f"<code>{class_['pvp']['kills']}</code>"
        text += self.strings["deaths"] + f"<code>{class_['pvp']['deaths']}</code>"

        # Skills stuff
        text += self.strings["skills"]
        for skill in class_["skills"]:
            text += self.strings[skill] + f"<code>{class_['skills'][skill]}</code>"

        # Professions stuff
        text += self.strings["professions"]
        for skill in class_["professions"]:
            text += self.strings[skill] + f"<code>{class_['professions'][skill]['level']} ({class_['professions'][skill]['xp']})</code>"

        return text

    def keyboard_class_builder(self, user):
        return [
            {
                "text": f'[{class_["level"]}] {"".join([i for i in class_["name"].title() if not i.isdigit()])}',
                "callback": self.inline__get_class,
                "args": [class_, user],
            }
            for class_ in user["classes"]
        ]

    async def wucheckcmd(self, message):
        """Check user by username"""
        if not (args := utils.get_args_raw(message)):
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{args}") as get:
                if get.status != 200:
                    return await utils.answer(message, self.strings["error_message"])
                uuid_str = (await get.json())["id"]

            # Get info about user
            async with session.get(
                    self.wynncraft_api.format(uuid.UUID(hex=uuid_str))
            ) as get:
                logger.debug(str(await get.json()))
                if (await get.json())["code"] != 200:
                    return await utils.answer(message, self.strings["error_message"])

            user = (await get.json())["data"][0]

        await self.inline.form(
            text=self.general_info_builder(user),
            message=message,
            reply_markup=chunks(self.keyboard_class_builder(user), 3),
            photo=f"https://wynndata.tk/gen/stats/{args}.png",
            force_me=False,  # optional: Allow other users to access form (all)
        )

    async def inline__get_class(self, call, class_, player):
        await call.edit(
            text=self.class_info_builder(class_),
            reply_markup=[
                {
                    "text": self.strings["btn_back"],
                    "callback": self.inline__back,
                    "args": [player],
                }
            ],
        )

    async def inline__back(self, call, player):
        await call.edit(
            text=self.general_info_builder(player),
            reply_markup=chunks(self.keyboard_class_builder(player), 3),
        )
