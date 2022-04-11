"""

    █▀▀ ▄▀█ █▄▀ █▀▀ █▀ ▀█▀ █░█░█ █ ▀▄▀
    █▄▄ █▀█ █░█ ██▄ ▄█ ░█░ ▀▄▀▄▀ █ █░█

    Copyleft 2022 t.me/CakesTwix                                                            
    This program is free software; you can redistribute it and/or modify 

"""

__version__ = (1, 0, 0)

# requires: aiohttp
# meta pic: https://icons.iconarchive.com/icons/blackvariant/button-ui-requests-2/1024/Minecraft-2-icon.png
# meta developer: @CakesTwix

import logging
import aiohttp
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class InlineMinecraftInfoMod(loader.Module):
    """Information about players and server status"""

    strings = {
        "name": "InlineMinecraftInfo",
        "error_message": "🚫 This entity does not exist or you entered it incorrectly",
        "about_user": "<b>Available player information</b> <code>{}</code>:'\n",
        "username": "<b>Username:</b> <code>{}</code>\n",
        "id": "<b>Id:</b> <code>{}</code>\n"
    }

    base_url = "https://api.minetools.eu"

    async def mucheckcmd(self, message):
        """Check user by username"""
        args = utils.get_args_raw(message)
        if args:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/uuid/{args}") as get:
                    data = await get.json()
                    if data["status"] == "ERR":
                        return await utils.answer(message, self.strings["error_message"])
                
                async with session.get(f"{self.base_url}/profile/{data['id']}") as get:
                    user = await get.json()
            
            text = self.strings["about_user"].format(user["decoded"]["profileName"])
            text += self.strings["id"].format(user["decoded"]["profileId"])
            text += self.strings["username"].format(user["decoded"]["profileName"])

            for texture in user['decoded']['textures']:
                text += f"<b>{texture}</b>: <a href={user['decoded']['textures'][texture]['url']}>URL</a>\n"

            await utils.answer(message, text)
                        
