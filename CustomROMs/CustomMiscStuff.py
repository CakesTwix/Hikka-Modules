import logging
from requests import get
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class CustomRomsMiscMod(loader.Module):
    """Miscellaneous stuff for custom ROMs"""

    strings = {"name": "Misc Custom staff",
               }


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

