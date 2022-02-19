# requires: requests

import logging
from requests import get
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class CustomRomsMod(loader.Module):
    """Miscellaneous stuff for custom ROMs"""

    strings = {"name": "ROMs",
               }

    twrp_api = "https://dl.twrp.me/"


    @loader.unrestricted
    @loader.ratelimit
    async def sakuracmd(self, message):
        """Project Sakura"""

        args = utils.get_args(message)
        if args:
            device = args[0].lower()
            data = get("https://raw.githubusercontent.com/ProjectSakura/OTA/11/devices.json").json()
            for item in data:
                if item["codename"] == device:
                    releases = f"Latest Project Sakura for {item['name']} ({item['codename']}) \n"
                    releases += f"👤 by {item['maintainer_name']} \n"
                    releases += f"⬇️ Download (https://projectsakura.xyz/download/#/{item['codename']}) \n"
                    await utils.answer(message, releases)
                    return
            await utils.answer(message, "No device...")
            await asyncio.sleep(5)
            await message.delete()
        else:
            await utils.answer(message, "Pls codename")
            await asyncio.sleep(5)
            await message.delete()

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
                dl_file = item.find('td').text
                size = item.find("span", {"class": "filesize"}).text
                reply += (f"⦁ <a href={dl_link}>{dl_file}</a> - <tt>{size}</tt>\n")

                await utils.answer(message, reply)
    
    @loader.unrestricted
    @loader.ratelimit
    async def shrpcmd(self, message):
        """SHRP Devices"""

        args = utils.get_args(message)
        if args:
            device = args[0].lower()
            data = get("https://raw.githubusercontent.com/SHRP-Devices/device_data/master/deviceData.json").json()
            for item in data[:-1]:
                if item["codeName"] == device:
                    releases = f"『 SkyHawk Recovery Project for {item['model']} ({device}): 』\n"
                    releases += f"👤 <b>by<b> {item['maintainer']} \n"
                    releases += f"ℹ️ <b>Version<b> : {item['currentVersion']} \n"
                    releases += f"⬇️ <b>Download<b> : <a href={item['latestBuild']}>SourceForge</a> \n"
                    await utils.answer(message, releases)
                    return
            await utils.answer(message, "No device...")
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
                async with session.get(f"https://pitchblackrecovery.com/{device}/") as get:
                    pbrp_page = await get.text()
                    await session.close()
    
            page = BeautifulSoup(pbrp_page, "lxml")
            status_error = page.find("h1", class_="error-code")
            if status_error is not None:
                return # No device


            main_info = page.find_all("h3", class_="elementor-heading-title elementor-size-default")
            download_info = page.find("section", class_="has_eae_slider elementor-section elementor-inner-section elementor-element elementor-element-714ebe14 elementor-section-boxed elementor-section-height-default elementor-section-height-default")

            version = main_info[0].text
            date = main_info[2].text
            status = main_info[4].text
            maintainer = main_info[6].text
            file_size = download_info.find_all("div", class_="elementor-text-editor elementor-clearfix")[1].text[10:]
            md5 = download_info.find_all("div", class_="elementor-text-editor elementor-clearfix")[2].text[4:]
            sourceforge = download_info.find_all("a", class_="elementor-button-link elementor-button elementor-size-md")[0]['href']
            github = download_info.find_all("a", class_="elementor-button-link elementor-button elementor-size-md")[1]['href']

            releases = f"『 Pitch Black Recovery Project for ({device}): 』\n"
            releases += f"👤 <b>by</b> {maintainer} \n"
            releases += f"ℹ️ <b>Status</b> : {status} \n"
            releases += f"ℹ️ <b>Version</b> : {version} \n"
            releases += f"ℹ️ <b>Date</b> : {date} \n"
            releases += f"ℹ️ <b>MD5</b> : {md5} \n"
            releases += f"ℹ️ <b>Size</b> : {file_size} \n"
            releases += f"⬇️ <b>Download</b> : <a href={sourceforge}>SourceForge</a> | <a href={github}>GitHub</a>\n"

            await utils.answer(message, releases)


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

            releases += (
                f'{name}: <a href={data["magisk"]["link"]}>APK v{data["magisk"]["version"]}</a> | <a href={data["magisk"]["note"]}>Changelog</a>\n'
            )
        await utils.answer(message, releases)

