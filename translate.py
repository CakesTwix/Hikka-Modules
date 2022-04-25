"""

    █▀▀ ▄▀█ █▄▀ █▀▀ █▀ ▀█▀ █░█░█ █ ▀▄▀
    █▄▄ █▀█ █░█ ██▄ ▄█ ░█░ ▀▄▀▄▀ █ █░█

    Copyleft 2022 t.me/CakesTwix                                                            
    This program is free software; you can redistribute it and/or modify 

"""

__version__ = (1, 0, 0)

# meta pic: https://icon-library.com/images/google-translate-icon/google-translate-icon-28.jpg
# meta developer: @CakesTwix

import logging
import aiohttp, asyncio
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class TranslatorMod(loader.Module):
    """Module for text translation"""

    strings = {
        "name": "Translator",
        "cfg_lingva_url": "Alternative front-end for Google Translate",
        "error": "Error!\n .gtr [en] ru | text",
    }

    strings_ru = {
        "cfg_lingva_url": "Альтернативный интерфейс для Google Translate",
        "error": "Ошибка!\n .gtr [en] ru | текст",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "lingva_url",
            "https://lingva.ml/api/v1/{source}/{target}/{query}",
            lambda m: self.strings("cfg_lingva_url", m),
        )
        self.name = self.strings["name"]

    @loader.unrestricted
    @loader.ratelimit
    async def gtrcmd(self, message):
        """
        .gtr en ru | Hello World
        .gtr ru | Hello World
        Based on lingva.ml (Google Translate)
        """
        args = utils.get_args_raw(message)
        lang_args = args.split("|")[0].split()
        text_args = args.split("|")[1]
        if args:
            if len(lang_args) == 2 and text_args:
                url = self.config["lingva_url"].format(
                    source=lang_args[0], target=lang_args[1], query=text_args
                )
            elif len(lang_args) == 1 and text_args:
                url = self.config["lingva_url"].format(
                    source="auto", target=lang_args[0], query=text_args
                )
            else:
                await utils.answer(message, self.strings["error"])
                await asyncio.sleep(5)
                await message.delete()
                return

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as get:
                    translated_text = await get.json()
                    await session.close()

            await utils.answer(message, translated_text["translation"])
        else:
            await utils.answer(message, self.strings["error"])
            await asyncio.sleep(5)
            await message.delete()
