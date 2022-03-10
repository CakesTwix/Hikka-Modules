__version__ = (1, 2, 0)

# requires: requests bs4 lxml
# scope: inline

import asyncio
import logging

import aiohttp
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from aiogram.utils.markdown import hlink
from bs4 import BeautifulSoup
from requests import get

from .. import loader, utils
from ..inline import GeekInlineQuery, rand

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class CustomRomsMod(loader.Module):
    """Miscellaneous stuff for custom ROMs"""

    strings = {
        "name": "InlineROMs",
        "download": "⬇️ <b>Download<b> :",
        "no_device": "No device.",
        "no_device_info": "ℹ Please check the correct codename or availability of the site",
        "no_codename": "Pls codename((",
        "write_codename": "Write the code name of your device",
        "latest_releases": "ℹ Latest {} releases",
        "latest_releases_device": "ℹ Latest {} {} releases for {}",
        "gapps_version": "GApps version",
        "vanilla_version": "Vanilla version",
        "general_info": "General info about {} builds",
        "general_info_description": "ℹ Maintainer, latest version, etc",
        "not_updating": "❌ : There will be no updates at this time",
        "updated": "✅ : Updated"
    }

    twrp_api = "https://dl.twrp.me/"

    # ROMs
    @loader.unrestricted
    @loader.ratelimit
    async def sakuracmd(self, message):
        """Project Sakura"""

        args = utils.get_args(message)
        if args:
            device = args[0].lower()
            data = get(
                "https://raw.githubusercontent.com/ProjectSakura/OTA/11/devices.json"
            ).json()
            for item in data:
                if item["codename"] == device:
                    releases = f"Latest Project Sakura for {item['name']} ({item['codename']}) \n"
                    releases += f"👤 by {item['maintainer_name']} \n"
                    releases += f"{self.strings['download']} (https://projectsakura.xyz/download/#/{item['codename']}) \n"
                    await utils.answer(message, releases)
                    return
            await utils.answer(message, f"{self.strings['no_device']}")
            await asyncio.sleep(5)
            await message.delete()
        else:
            await utils.answer(message, f"{self.strings['no_codename']}")
            await asyncio.sleep(5)
            await message.delete()

    @loader.unrestricted
    @loader.ratelimit
    async def dotoscmd(self, message):
        """DotOS"""
        args = utils.get_args(message)
        if args:
            device = args[0].lower()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.droidontime.com/api/ota/{}".format(device)
                ) as get:
                    if get.ok:
                        data = await get.json()
                    else:
                        await utils.answer(message, f"{self.strings['no_device']}")
                        await asyncio.sleep(5)
                        await message.delete()
                    await session.close()

            releases = f"<b>Latest DotOS for {data['brandName']} {data['deviceName']}</b> (<code>{data['codename']}</code>) \n"
            releases += f"👤 : {data['maintainerInfo']['name']} \n"
            releases += f"🆚 : {data['latestVersion']} \n"
            releases += f"{self.strings['download']} "
            releases += f"<a href={data['releases'][0]['url']}>{data['releases'][1]['type'].capitalize()}<a/>"
            releases += f" / <a href={data['releases'][1]['url']}>{data['releases'][1]['type'].capitalize()}<a/>"
            await utils.answer(message, releases)
        else:
            await utils.answer(message, f"{self.strings['no_codename']}")
            await asyncio.sleep(5)
            await message.delete()

    # Recovery
    @loader.unrestricted
    @loader.ratelimit
    async def twrpcmd(self, message):
        """TWRP Devices"""
        args = utils.get_args(message)
        if args:
            device = args[0].lower()
            url = get(f"{self.twrp_api}{device}/")

            if url.status_code == 404:
                reply = f"`Couldn't find twrp downloads for {device}!`\n"
                await utils.answer(message, reply)
                await asyncio.sleep(5)
                await message.delete()
                return

            page = BeautifulSoup(url.content, "lxml")
            download = page.find("table").find_all("tr")
            reply = f"『 Team Win Recovery Project for {device}: 』\n"
            for item in download:
                dl_link = f"{self.twrp_api}{item.find('a')['href']}"
                dl_file = item.find("td").text
                size = item.find("span", {"class": "filesize"}).text
                reply += f"⦁ <a href={dl_link}>{dl_file}</a> - <tt>{size}</tt>\n"

                await utils.answer(message, reply)

    @loader.unrestricted
    @loader.ratelimit
    async def shrpcmd(self, message):
        """SHRP Devices"""

        args = utils.get_args(message)
        if args:
            device = args[0].lower()
            data = get(
                "https://raw.githubusercontent.com/SHRP-Devices/device_data/master/deviceData.json"
            ).json()
            for item in data[:-1]:
                if item["codeName"] == device:
                    releases = f"『 SkyHawk Recovery Project for {item['model']} ({device}): 』\n"
                    releases += f"👤 <b>by<b> {item['maintainer']} \n"
                    releases += f"ℹ️ <b>Version<b> : {item['currentVersion']} \n"
                    releases += f"{self.strings['download']} : <a href={item['latestBuild']}>SourceForge</a> \n"
                    await utils.answer(message, releases)
                    return
            await utils.answer(message, f"{self.strings['no_device']}")
            await asyncio.sleep(5)
            await message.delete()

    @loader.unrestricted
    @loader.ratelimit
    async def pbrpcmd(self, message):
        """PBRP Devices"""
        args = utils.get_args(message)
        if args:
            device = args[0].lower()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://pitchblackrecovery.com/{device}/"
                ) as get:
                    pbrp_page = await get.text()
                    await session.close()

            page = BeautifulSoup(pbrp_page, "lxml")
            status_error = page.find("h1", class_="error-code")
            if status_error is not None:
                return  # No device

            main_info = page.find_all(
                "h3", class_="elementor-heading-title elementor-size-default"
            )
            download_info = page.find(
                "section",
                class_="has_eae_slider elementor-section elementor-inner-section elementor-element elementor-element-714ebe14 elementor-section-boxed elementor-section-height-default elementor-section-height-default",
            )

            version = main_info[0].text
            date = main_info[2].text
            status = main_info[4].text
            maintainer = main_info[6].text
            file_size = download_info.find_all(
                "div", class_="elementor-text-editor elementor-clearfix"
            )[1].text[10:]
            md5 = download_info.find_all(
                "div", class_="elementor-text-editor elementor-clearfix"
            )[2].text[4:]
            sourceforge = download_info.find_all(
                "a", class_="elementor-button-link elementor-button elementor-size-md"
            )[0]["href"]
            github = download_info.find_all(
                "a", class_="elementor-button-link elementor-button elementor-size-md"
            )[1]["href"]

            releases = f"『 Pitch Black Recovery Project for ({device}): 』\n"
            releases += f"👤 <b>by</b> {maintainer} \n"
            releases += f"ℹ️ <b>Status</b> : {status} \n"
            releases += f"ℹ️ <b>Version</b> : {version} \n"
            releases += f"ℹ️ <b>Date</b> : {date} \n"
            releases += f"ℹ️ <b>MD5</b> : {md5} \n"
            releases += f"ℹ️ <b>Size</b> : {file_size} \n"
            releases += f"{self.strings['download']} : <a href={sourceforge}>SourceForge</a> | <a href={github}>GitHub</a>\n"

            await utils.answer(message, releases)

    # Other
    @loader.unrestricted
    @loader.ratelimit
    async def magiskcmd(self, message):
        """Magisk by topjohnwu"""
        magisk_repo = "https://raw.githubusercontent.com/topjohnwu/magisk-files/"
        magisk_dict = {
            "⦁ 𝗦𝘁𝗮𝗯𝗹𝗲": magisk_repo + "master/stable.json",
            "⦁ 𝗕𝗲𝘁𝗮": magisk_repo + "master/beta.json",
            "⦁ 𝗖𝗮𝗻𝗮𝗿𝘆": magisk_repo + "master/canary.json",
        }
        releases = "<code><i>𝗟𝗮𝘁𝗲𝘀𝘁 𝗠𝗮𝗴𝗶𝘀𝗸 𝗥𝗲𝗹𝗲𝗮𝘀𝗲:</i></code>\n\n"
        for name, release_url in magisk_dict.items():
            data = get(release_url).json()

            releases += f'{name}: <a href={data["magisk"]["link"]}>APK v{data["magisk"]["version"]}</a> | <a href={data["magisk"]["note"]}>Changelog</a>\n'
        await utils.answer(message, releases)

    # Inline commands
    async def opengapps_inline_handler(self, query: GeekInlineQuery) -> None:
        """
        OpenGApps (Inline)
        @allow: all
        """
        text = query.args

        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.opengapps.org/list") as get:
                opengapps_list = await get.json()
                await session.close()

        arch_dict = {}
        version_text = "<b>Avilable versions</b> :\n"
        for arch in opengapps_list["archs"]:
            apis_list = []
            for apis in opengapps_list["archs"][arch]["apis"]:
                apis_list.append(str(apis))
            arch_dict[arch] = apis_list
            version_text += f"<b>{arch}</b> : {', '.join(apis_list)}\n"

        if not text:
            await query.answer(
                [
                    InlineQueryResultArticle(
                        id=rand(20),
                        title="Select android version for your device",
                        description="ℹ For example : 10.0. Click for more versions",
                        input_message_content=InputTextMessageContent(
                            version_text, "HTML", disable_web_page_preview=True
                        ),
                        thumb_url="https://img.icons8.com/android/128/26e07f/android.png",
                        thumb_width=128,
                        thumb_height=128,
                    )
                ],
                cache_time=0,
            )
            return

        if len(text.split()) == 1:

            archs_inline = []
            archs_photo = {
                "arm": "https://img.icons8.com/android/128/26e07f/32bit.png",
                "arm64": "https://img.icons8.com/android/128/26e07f/64bit.png",
                "x86": "https://img.icons8.com/android/128/26e07f/x86.png",
                "x86_64": "https://img.icons8.com/android/128/26e07f/x64.png",
            }

            for arch in opengapps_list["archs"]:  # arm arm64 x86 etc
                if text in arch_dict[arch]:
                    markup = InlineKeyboardMarkup(row_width=3)
                    for variant in opengapps_list["archs"][arch]["apis"][text][
                        "variants"
                    ]:  # pico nano etc
                        markup.insert(
                            InlineKeyboardButton(variant["name"], url=variant["zip"])
                        )

                    archs_inline.append(
                        InlineQueryResultArticle(
                            id=rand(20),
                            title=arch,
                            description="ℹ Select arch for your device",
                            input_message_content=InputTextMessageContent(
                                f"OpenGApps for Android {text} {arch}",
                                "HTML",
                                disable_web_page_preview=True,
                            ),
                            thumb_url=archs_photo[arch],
                            thumb_width=128,
                            thumb_height=128,
                            reply_markup=markup,
                        )
                    )
                    markup = None
            await query.answer(archs_inline, cache_time=0)

    async def dotos_inline_handler(self, query: GeekInlineQuery) -> None:
        """
        DotOS (Inline)
        @allow: all
        """
        text = query.args

        if not text:
            await query.answer(
                [
                    InlineQueryResultArticle(
                        id=rand(20),
                        title=self.strings["write_codename"],
                        description=self.strings["latest_releases"].format("DotOS"),
                        input_message_content=InputTextMessageContent(
                            self.strings["no_codename"], "HTML", disable_web_page_preview=True
                        ),
                        thumb_url="https://img.icons8.com/android/128/26e07f/android.png",
                        thumb_width=128,
                        thumb_height=128,
                    )
                ],
                cache_time=0,
            )
            return

        if len(text.split()) == 1:
            device = text
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.droidontime.com/api/ota/{}".format(device)
                ) as get:
                    if get.ok:
                        data = await get.json()
                    else:
                        await query.answer(
                            [
                                InlineQueryResultArticle(
                                    id=rand(20),
                                    title=self.strings["no_device"],
                                    description=self.strings["no_device_info"],
                                    input_message_content=InputTextMessageContent(
                                        self.strings["no_device_info"],
                                        "HTML",
                                        disable_web_page_preview=True,
                                    ),
                                    thumb_url="https://img.icons8.com/android/128/fa314a/cancel-2.png",
                                    thumb_width=128,
                                    thumb_height=128,
                                )
                            ],
                            cache_time=0,
                        )
                        await session.close()
                        return
                    await session.close()

            vanilla_markup = InlineKeyboardMarkup(row_width=3)
            gapps_markup = InlineKeyboardMarkup(row_width=3)
            for releases in data['releases']:
                if releases['type'] == "vanilla":
                    vanilla_markup.insert(
                            InlineKeyboardButton(releases["version"], url=releases["url"])
                        )
                else:
                    gapps_markup.insert(
                            InlineKeyboardButton(releases["version"], url=releases["url"])
                        )

            about_info = f"<b>DotOS for {data['brandName']} {data['deviceName']}</b> (<code>{data['codename']}</code>) \n"
            about_info += f"👤 : {hlink(data['maintainerInfo']['name'], data['maintainerInfo']['profileURL'])} \n"
            about_info += f"🆚 : {data['latestVersion']} \n"
            about_info += self.strings['not_updating'] if data['discontinued'] else self.strings['updated']
            about_info += f"\n🔗 : {hlink('XDA',data['links']['xda'])} / {hlink('Telegram',data['links']['telegram'])} \n"

            await query.answer( # About, Vanilla, Gapps
                [
                    InlineQueryResultArticle(
                        id=rand(20),
                        title=self.strings["general_info"].format("DotOS"),
                        description=self.strings["general_info_description"],
                        input_message_content=InputTextMessageContent(
                            about_info,
                            "HTML",
                            disable_web_page_preview=True,
                        ),
                        thumb_url="https://img.icons8.com/android/128/26e07f/info.png",
                        thumb_width=128,
                        thumb_height=128,
                    ),
                    InlineQueryResultArticle(
                        id=rand(20),
                        title=self.strings["vanilla_version"],
                        description=self.strings["latest_releases"].format("DotOS"),
                        input_message_content=InputTextMessageContent(
                            self.strings["latest_releases_device"].format("DotOS", "Vanilla", device),
                            "HTML",
                            disable_web_page_preview=True,
                        ),
                        thumb_url="https://img.icons8.com/android/128/26e07f/forward.png",
                        thumb_width=128,
                        thumb_height=128,
                        reply_markup=vanilla_markup
                    ),
                    InlineQueryResultArticle(
                        id=rand(20),
                        title=self.strings["gapps_version"],
                        description=self.strings["latest_releases"].format("DotOS"),
                        input_message_content=InputTextMessageContent(
                            self.strings["latest_releases_device"].format("DotOS", "GApps", device),
                            "HTML",
                            disable_web_page_preview=True,
                        ),
                        thumb_url="https://img.icons8.com/android/128/26e07f/forward.png",
                        thumb_width=128,
                        thumb_height=128,
                        reply_markup=gapps_markup
                    )
                ],
                cache_time=0,
            )
