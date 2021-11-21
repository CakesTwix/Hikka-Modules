import logging
import aiohttp
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class TranslatorMod(loader.Module):
    """Module for text translation"""

    strings = {"name": "Translator",
               }

    @loader.unrestricted
    @loader.ratelimit
    async def npcmd(self, message):
        """DeepL"""
        pass


