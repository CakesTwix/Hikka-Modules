# requires: qrcode

import asyncio
import io
import logging

import qrcode

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class QrCodeMod(loader.Module):
    """Module for creating Qr codes"""

    strings = {
        "name": "QrCode",
    }

    @loader.unrestricted
    @loader.ratelimit
    async def qrcmd(self, message):
        """Create QrCode"""
        reply = await message.get_reply_message()

        if len(message.text) > 3:
            text = message.text[4:]  # .qr_
        elif reply and reply.text != "":
            text = reply.text
        else:
            text = None

        if text != None:
            img = qrcode.make(text)
            with io.BytesIO() as output:
                img.save(output)
                contents = output.getvalue()
            await message.delete()
            await message.client.send_file(message.chat_id, contents, caption=text)
        else:
            await utils.answer(message, "Pls text")
            await asyncio.sleep(5)
            await message.delete()
