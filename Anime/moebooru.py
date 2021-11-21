# requires: requests

import logging
from requests import get
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class MoebooruMod(loader.Module):
    """Module for obtaining art from the ImageBoard Moebooru"""

    strings = {"name": "Moebooru",
               }
    url = 'https://yande.re/post.json'

    @loader.unrestricted
    @loader.ratelimit
    async def mlastcmd(self, message):
        """The last posted art"""
        args = utils.get_args(message)
        await message.delete()

        params = "?tags="
        if "-sfw" in args:
            params += " rating:s"
        art_data = get(self.url + params).json()

        tags = ''
        if "-t" in args:
            tags = art_data[0]['tags']  

        await message.client.send_file(message.chat_id, art_data[0]['sample_url'], caption=tags)

    @loader.unrestricted
    @loader.ratelimit
    async def mrandomcmd(self, message):
        """Random posted art"""
        
        args = utils.get_args(message)
        await message.delete()

        params = "?tags=order:random"
        if "-sfw" in args:
            params += " rating:s"
        art_data = get(self.url + params).json()

        tags = ''
        if "-t" in args:
            tags = art_data[0]['tags']  

        await message.client.send_file(message.chat_id, art_data[0]['sample_url'], caption=tags)


