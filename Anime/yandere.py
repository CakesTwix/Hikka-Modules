# requires: aiohttp

import logging
import aiohttp
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class MoebooruMod(loader.Module):
    """Module for obtaining art from the ImageBoard yande.re"""

    strings = {"name": "Yandere",
               "url": "https://yande.re/post.json",
               "cfg_yandere_login":"Login from yande.re",
               "cfg_yandere_password_hash": "SHA1 hashed password",
               }

    def __init__(self):
        self.config = loader.ModuleConfig("yandere_login", "None", lambda m: self.strings("cfg_yandere_login", m),
                                          "yandere_password_hash", "None", lambda m: self.strings("cfg_yandere_password_hash", m))
        self.name = self.strings["name"]

    @loader.unrestricted
    @loader.ratelimit
    async def ylastcmd(self, message):
        """The last posted art"""
        args = utils.get_args(message)
        await message.delete()

        params = f"?login={self.config['yandere_login']}&password_hash={self.config['yandere_password_hash']}&tags="
        async with aiohttp.ClientSession() as session:
                async with session.get(self.strings["url"] + params) as get:
                    art_data = await get.json()
                    await session.close()  

        await message.client.send_file(message.chat_id, art_data[0]['sample_url'])

    @loader.unrestricted
    @loader.ratelimit
    async def yrandomcmd(self, message):
        """Random posted art"""
        
        args = utils.get_args(message)
        await message.delete()

        params = f"?login={self.config['yandere_login']}&password_hash={self.config['yandere_password_hash']}&tags=order:random"
        async with aiohttp.ClientSession() as session:
                async with session.get(self.strings["url"] + params) as get:
                    art_data = await get.json()
                    await session.close()  

        await message.client.send_file(message.chat_id, art_data[0]['sample_url'])


