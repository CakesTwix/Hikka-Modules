# requires: qrcode

import logging
from .. import loader, utils
import qrcode
import io

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class QrCodeMod(loader.Module):
    """Module for creating Qr codes"""

    strings = {"name": "QrCode",
               }

    @loader.unrestricted
    @loader.ratelimit
    async def qrcmd(self, message):
        """Create QrCode"""
        reply = await message.get_reply_message()
        text = ""
        if reply:
            text = reply.text
        else:
            text = message.text[2:]

        img = qrcode.make(text)
        with io.BytesIO() as output:
            img.save(output)
            contents = output.getvalue()
        await message.client.send_file(message.chat_id, contents, caption = text)