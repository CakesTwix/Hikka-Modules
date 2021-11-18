import logging
from requests import get
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class CustomRomsMod(loader.Module):
    """Information of officially supported devices"""

    strings = {"name": "ROMs",
               }

    @loader.unrestricted
    @loader.ratelimit
    async def sakuracmd(self, message):
        """Project Sakura"""

        """
        Latest Project Sakura for LeEco Le 2 (s2)
        👤 by CakesTwix
        ℹ️ Version : 5.2
        ❕ Variant: GApps Core
        ⬇️ Download (https://projectsakura.xyz/download/#/s2)

        ✅ This device is currently officially supported
        """
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


