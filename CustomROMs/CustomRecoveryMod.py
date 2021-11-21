import logging
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
                    releases += f"👤 by {item['maintainer']} \n"
                    releases += f"ℹ️ Version : {item['currentVersion']} \n"
                    releases += f"⬇️ Download <a href={item['latestBuild']}>SourceForge</a> \n"
                    await utils.answer(message, releases)
                    return
            await utils.answer(message, "No device...")


