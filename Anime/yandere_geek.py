__version__ = (1, 0, 1)

# requires: aiohttp
# scope: inline_control


import logging
import aiohttp, asyncio
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class MoebooruMod(loader.Module):
    """Module for obtaining art from the ImageBoard yande.re"""

    strings = {"name": "Yandere",
               "url": "https://yande.re/post.json",
               "vote_url": "https://yande.re/post/vote.json?login={login}&password_hash={password_hash}",
               "vote_text":"Vote for this art. The buttons are only available to me",
               "vote_ok":"OK!",
               "vote_login":"Login or password incorrect.",
               "vote_error":"ERROR, .logs 40 or .logs error",
               "cfg_yandere_login":"Login from yande.re",
               "cfg_yandere_password_hash": "SHA1 hashed password",
               }

    def __init__(self):
        self.config = loader.ModuleConfig("yandere_login", "None", lambda m: self.strings("cfg_yandere_login", m),
                                          "yandere_password_hash", "None", lambda m: self.strings("cfg_yandere_password_hash", m))
        self.name = self.strings["name"]
   

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client


    def string_builder(self, json):
        string = f"Tags : {json['tags']}\n"
        string += f"©️ : {json['author'] if json['author'] else 'No author'}\n"
        string += f"🔗 : {json['source'] if json['source'] else 'No source'}\n\n"
        string += f"🆔 : <a href=https://yande.re/post/show/{json['id']}>{json['id']}</a>"

        return string

    @loader.unrestricted
    @loader.ratelimit
    async def ylastcmd(self, message):
        """The last posted art"""
        args = utils.get_args(message)
        await message.delete()

        params = f"?login={self.config['yandere_login']}&password_hash={self.config['yandere_password_hash']}&tags="
        async with aiohttp.ClientSession() as session:
                async with session.get(self.strings["url"] + params) as get:
                    art_data = await get.json()
                    await session.close()  

        await message.client.send_file(message.chat_id, art_data[0]['sample_url'], caption=self.string_builder(art_data[0]))


    @loader.unrestricted
    @loader.ratelimit
    async def yrandomcmd(self, message):
        """Random posted art"""
        
        args = utils.get_args(message)
        await message.delete()

        params = f"?login={self.config['yandere_login']}&password_hash={self.config['yandere_password_hash']}&tags=order:random"
        async with aiohttp.ClientSession() as session:
                async with session.get(self.strings["url"] + params) as get:
                    art_data = await get.json()
                    await session.close()  

        await message.client.send_file(message.chat_id, art_data[0]['sample_url'], caption=self.string_builder(art_data[0]))
        
    @loader.unrestricted
    @loader.ratelimit
    async def yvotecmd(self, message) -> None:
        """
        Vote for art

        Bad = -1, None = 0, Good = 1, Great = 2, Favorite = 3
        """
        reply = await message.get_reply_message()
        args = utils.get_args(message)
        if reply and args:
            yandere_id = reply.raw_text.split("🆔")[1][2:]

            params = {'id': yandere_id,
                      'score': args[0]}
            async with aiohttp.ClientSession() as session:
                async with session.post(self.strings["vote_url"].format(login=self.config['yandere_login'], 
                                                                        password_hash=self.config['yandere_password_hash']),
                                        data=params) as post:
                    result_code = post.status
                    await session.close()  
            if result_code == 200:
                await utils.answer(message, self.strings('vote_ok'))
            elif result_code == 403:
                await utils.answer(message, self.strings('vote_login'))
            else:
                await utils.answer(message, self.strings('vote_error'))
            await asyncio.sleep(5)
            await message.delete()
            return
        elif reply:
            yandere_id = reply.raw_text.split("🆔")[1][2:]
            kb = [
            [{
                'text': 'Bad',
                'callback': self.vote,
                'args': [-1, yandere_id]
            }],
            [{
                'text': 'Good',
                'callback': self.vote,
                'args': [1, yandere_id]
            }],
            [{
                'text': 'Great',
                'callback': self.vote,
                'args': [2, yandere_id]
            }],
            [{
                'text': 'Favorite',
                'callback': self.vote,
                'args': [3, yandere_id]
            }]
            ]
            await self.inline.form(self.strings["vote_text"], message=message, reply_markup=kb, always_allow=loader.dispatcher.security._owner)
            return

        await utils.answer(message, "Pls code! Check help Yandere")
        await asyncio.sleep(5)
        await message.delete()

    async def vote(self, call, score, _id) -> None:
        params = {'id': _id, 'score': score}
        async with aiohttp.ClientSession() as session:
            async with session.post(self.strings["vote_url"].format(login=self.config['yandere_login'], 
                                    password_hash=self.config['yandere_password_hash']),
                                    data=params) as post:
                result_code = post.status
                await session.close()
        kb = [[{
            'text': '🚫 Close',
            'callback': self.inline__close
        }]]

        if result_code == 200:
            await call.edit(self.strings('vote_ok'), reply_markup=kb)
        elif result_code == 403:
            await call.edit(self.strings('vote_login'), reply_markup=kb)
        else:
            await call.edit(self.strings('vote_error'), reply_markup=kb)

        


    async def inline__close(self, call: "aiogram.types.CallbackQuery") -> None:
        await call.delete()

