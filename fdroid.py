"""

    █▀▀ ▄▀█ █▄▀ █▀▀ █▀ ▀█▀ █░█░█ █ ▀▄▀
    █▄▄ █▀█ █░█ ██▄ ▄█ ░█░ ▀▄▀▄▀ █ █░█

    Copyleft 2022 t.me/CakesTwix
    This program is free software; you can redistribute it and/or modify

"""

__version__ = (1, 0, 0)

# meta pic: https://forum.f-droid.org/uploads/default/original/2X/c/cfb2c14973c28415b0e5b5f7adef9c8288cd8609.png
# meta developer: @cakestwix_mods
# scope: hikka_only
# requires: httpx bs4

import logging

import httpx
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from aiogram.utils.markdown import hlink
from bs4 import BeautifulSoup

from .. import loader, utils
from ..inline.types import InlineQuery

logger = logging.getLogger(__name__)

url = "https://search.f-droid.org/?lang=en&page="


async def fdroid_search(search_app) -> dict:
    """From https://github.com/imthepooh/fdroidsrch/blob/master/main.py"""
    fin_dict = []

    i = 1
    url_set = url + str(i) + "&q=" + search_app
    async with httpx.AsyncClient() as client:
        s_page = await client.get(url_set)
    # fetch the search results
    soup = BeautifulSoup(s_page.content, "html.parser")
    num = 0

    # check if the search results are multipaged
    for nums in soup.find_all("span", class_="step-links"):
        try:
            num = int(nums.get_text())
        except Exception:
            num_str = nums.get_text()

    # set the number of pages to be scrapped
    i = 1 if num == 0 else num
    for n in range(1, i + 1):
        if n > 1:
            url_set = url + str(n) + "&q=" + search_app
            async with httpx.AsyncClient() as client:
                s_page = await client.get(url_set)
                soup = BeautifulSoup(s_page.content, "html.parser")

        # get app name, details and url
        for app_h in soup.find_all("a", class_="package-header"):
            app_n = app_h.find("h4", class_="package-name")
            app_s = app_h.find("span", class_="package-summary")
            app_l = app_h.find("span", class_="package-license")
            app_i = app_h.find("img", class_="package-icon")

            # prepare result string
            fin_dict.append(
                {
                    "Name": app_n.get_text().strip(),
                    "Desc": app_s.get_text().strip(),
                    "Url": app_h["href"].strip(),
                    "License": app_l.get_text().strip(),
                    "Icon": app_i["src"],
                }
            )
        
        if len(fin_dict) >= 40:
            return fin_dict
    
    return fin_dict
    


class FDroidMod(loader.Module):
    """Search for android apps from FDroid"""

    strings = {
        "name": "FDroid",
        "no_args": "🚫 Not found args, pls check help",
        "no_apps": "🚫 Unfortunately, I couldn't find any applications",
        "link": "🔗 Link",
    }

    strings_ru = {
        "name": "FDroid",
        "no_args": "🚫 Аргументы не найдены, пожалуйста, проверьте справку",
        "no_apps": "🚫 К сожалению, не нашел приложений",
        "link": "🔗 Ссылка",
    }

    async def fdroidcmd(self, message):
        """Find the app in the FDroid catalog"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings["no_args"])

        if apps := await fdroid_search(args):
            await self.inline.gallery(
                message,
                [app["Icon"] for app in apps],
                [
                    f"<code>{app['Name']}</code> ({app['License']})\n\n{app['Desc']}\n{hlink(self.strings['link'], app['Url'])}"
                    for app in apps
                ],
            )
        else:
            await utils.answer(message, self.strings["no_apps"])

    @loader.inline_everyone
    async def fdroid_inline_handler(self, query: InlineQuery) -> None:
        """Find the app in the FDroid catalog (Inline)"""
        query_args = query.args
        if not query_args:
            return await query.e400()

        if apps := await fdroid_search(query_args):
            InlineQueryResult = []
            for app in apps:
                # Generate button
                markup = InlineKeyboardMarkup()
                markup.insert(InlineKeyboardButton(self.strings["link"], app["Url"]))

                # Add InlineQueryResultArticle
                InlineQueryResult.append(
                    InlineQueryResultArticle(
                        id=utils.rand(64),
                        title=f'{app["Name"]} ({app["License"]})',
                        description=app["Desc"],
                        input_message_content=InputTextMessageContent(
                            f"<code>{app['Name']}</code> ({app['License']})\n\n{app['Desc']}",
                            "HTML",
                            disable_web_page_preview=True,
                        ),
                        reply_markup=markup,
                        thumb_url=app["Icon"],
                    )
                )

            await query.answer(InlineQueryResult, cache_time=0)
        else:
            await query.e404()
