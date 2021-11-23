# requires: requests bs4 aiohttp

import logging
import aiohttp
from requests import get
from bs4 import BeautifulSoup
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.unrestricted
@loader.ratelimit
@loader.tds
class CustomRomsRecoveryMod(loader.Module):
    """Recovery for custom ROMs"""

    strings = {"name": "Recovery",
               }
    twrp_api = "https://dl.twrp.me/"

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
                print("No device")
                return
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