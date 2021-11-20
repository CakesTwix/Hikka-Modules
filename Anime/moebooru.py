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
        art_data = get(self.url).json()
        await message.delete()
        
        tags = ''
        args = utils.get_args(message)
        if "-t" in args:
            tags = art_data[0]['tags']
        
        await message.client.send_file(message.chat_id, art_data[0]['sample_url'], caption = tags)

    @loader.unrestricted
    @loader.ratelimit
    async def mrandomcmd(self, message):
        """Random posted art"""
        art_data = get(self.url + "?tags=order:random").json()
        await message.delete()

        tags = ''
        args = utils.get_args(message)
        if "-t" in args:
            tags = art_data[0]['tags']

        await message.client.send_file(message.chat_id, art_data[0]['sample_url'], caption=tags)


