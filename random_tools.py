__version__ = (1, 0, 0)

import logging
import aiohttp
import asyncio
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class RToolsMod(loader.Module):
    """Random tools"""

    strings = {
        "name": "Tools",
        "no_found": "No found",
        "no_args": "Not found args, pls check help",
        "general_error": "Oh no, cringe, error"
    }

    @loader.unrestricted
    @loader.ratelimit
    async def mac2vendorcmd(self, message):
        """Get vendor name by mac"""
        args = utils.get_args(message)
        if args:
            mac = args[0].lower()
            async with aiohttp.ClientSession() as session:
                async with session.get("http://api.macvendors.com/" + mac) as get:
                    if get.ok:
                        await utils.answer(message, await get.text())
                    else:
                        await utils.answer(message, self.strings["no_found"])
                        await asyncio.sleep(5)
                        await message.delete()
        else:
            await utils.answer(message, self.strings["no_args"])
            await asyncio.sleep(5)
            await message.delete()

    @loader.unrestricted
    @loader.ratelimit
    async def oneptcmd(self, message):
        """A simple URL shortener (1pt.co)"""
        args = utils.get_args(message)
        if args:
            mac = args[0].lower()
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.1pt.co/addURL?long=" + mac) as get:
                    if get.ok:
                        answer_json = await get.json()
                        await utils.answer(message, "1pt.co/" + answer_json['short'])
                    else:
                        await utils.answer(message, self.strings["general_error"])
                        await asyncio.sleep(5)
                        await message.delete()
        else:
            await utils.answer(message, self.strings["no_args"])
            await asyncio.sleep(5)
            await message.delete()
        