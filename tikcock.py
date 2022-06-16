"""

    █▀▀ ▄▀█ █▄▀ █▀▀ █▀ ▀█▀ █░█░█ █ ▀▄▀
    █▄▄ █▀█ █░█ ██▄ ▄█ ░█░ ▀▄▀▄▀ █ █░█

    Copyleft 2022 t.me/CakesTwix
    This program is free software; you can redistribute it and/or modify

    Source - https://github.com/sm1ke000FriendlyTelegram/Friendly-Telegram/raw/main/TikTokMOD.py

"""

__version__ = (1, 0, 3)

# meta pic: http://assets.stickpng.com/images/5cb78671a7c7755bf004c14b.png
# meta developer: @cakestwix_mods

import logging
from .. import loader, utils
from telethon.errors.rpcerrorlist import BotResponseTimeoutError

logger = logging.getLogger(__name__)


@loader.tds
class TikTokMod(loader.Module):
    """Download tt video via @tikdobot"""

    strings = {
        "name": "TikTokDownloader",
        "no_args": "🚫 Not found args, pls check help",
        "timeout_error": "🚫 The bot didn't send anything((",
    }

    strings_ru = {
        "no_args": "🚫 Аргументы не найдены, пожалуйста, проверьте справку",
        "timeout_error": "🚫 Бот ничего не прислал((",
    }

    @loader.unrestricted
    @loader.ratelimit
    async def dttnwcmd(self, message):
        """Get tt video without watermark"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings["no_args"])

        try:
            r = await message.client.inline_query("tikdobot", args)
        except BotResponseTimeoutError:
            return await utils.answer(message, self.strings["timeout_error"])

        await message.client.send_file(message.to_id, r[1].result.content.url)
        await message.delete()

    @loader.unrestricted
    @loader.ratelimit
    async def dttcmd(self, message):
        """Get tt video with watermark"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings["no_args"])

        try:
            r = await message.client.inline_query("tikdobot", args)
        except BotResponseTimeoutError:
            return await utils.answer(message, self.strings["timeout_error"])

        await message.client.send_file(message.to_id, r[0].result.content.url)
        await message.delete()
