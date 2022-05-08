"""

    █▀▀ ▄▀█ █▄▀ █▀▀ █▀ ▀█▀ █░█░█ █ ▀▄▀
    █▄▄ █▀█ █░█ ██▄ ▄█ ░█░ ▀▄▀▄▀ █ █░█

    Copyleft 2022 t.me/CakesTwix
    This program is free software; you can redistribute it and/or modify

"""

__version__ = (1, 0, 1)

# meta pic: https://img.icons8.com/fluency/50/000000/youtube.png
# meta developer: @CakesTwix
# requires: yt_dlp
# scope: hikka_min 1.1.11
# scope: hikka_only 

import asyncio
import logging
import os

import yt_dlp
from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return "%.1f%s" % (value, s)
    return "%sB" % n


def progressbar(iteration: int, length: int) -> str:
    percent = ("{0:." + str(1) + "f}").format(100 * (iteration / float(100)))
    filledLength = int(length * iteration // 100)
    return "█" * filledLength + "▒" * (length - filledLength)


@loader.tds
class YouTubeMod(loader.Module):
    """Download YouTube videos with video and audio quality selection"""

    strings = {
        "name": "InlineYouTube",
        "args": "🎞 <b>You need to specify link</b>",
        "downloading": "🎞 <b>Downloading...</b>",
        "not_found": "🎞 <b>Video not found...</b>",
        "format": "<b>Format</b>:",
        "ext": "<b>Ext</b>:",
        "video_codec": "<b>Video codec</b>:",
        "audio": "Audio",
        "file_size": "<b>File size</b>:",
        "uploading": "<b>Uploading File... Progress</b>",
        "downloading": "<b>Downloading File...</b>"
    }

    strings_ru = {
        "name": "InlineYouTube",
        "args": "🎞 <b>Вам необходимо указать ссылку</b>",
        "downloading": "🎞 <b>Загружаю...</b>",
        "not_found": "🎞 <b>Видео не найдено...</b>",
        "format": "<b>Формат</b>:",
        "ext": "<b>Расширение</b>:",
        "video_codec": "<b>Видео кодек</b>:",
        "audio": "Аудио",
        "file_size": "<b>Размер</b>:",
        "uploading": "<b>Закачка файла... Прогресс</b>",
        "downloading": "<b>Загружаю файл...</b>"
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    @loader.unrestricted
    async def ytcmd(self, message: Message):
        """<link> - Download video from youtube"""
        args = utils.get_args_raw(message)
        await utils.answer(message, self.strings("downloading"))

        if not args:
            return await utils.answer(message, self.strings("args"))

        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(args, download=False)
            formats_list = []
            for item in info_dict["formats"]:
                if item["ext"] in ["mp4", "webm"] and item["vcodec"] != "none":
                    formats_list.append(
                        {
                            "text": f"{item['format_note']} ({item['video_ext']})",
                            "callback": self.format_change,
                            "args": (
                                item,
                                info_dict,
                                message.chat.id,
                                item["format_id"],
                            ),
                        }
                    )

            caption = f"<b>{info_dict['title']}</b>\n\n"
            # caption += info_dict["description"]
            await self.inline.form(
                text=caption,
                photo=f"https://img.youtube.com/vi/{info_dict['id']}/maxresdefault.jpg",
                message=message,
                reply_markup=utils.chunks(formats_list, 2),
            )

    async def format_change(
        self,
        call: InlineCall,
        quality: dict,
        info_dict: dict,
        chat_id: int,
        format_id: int,
    ):
        string = f"{self.strings['format']} {quality['format']}\n"
        string += f"{self.strings['ext']} {quality['ext']}\n"
        string += f"{self.strings['video_codec']} {quality['vcodec']}\n"
        string += f"{self.strings['file_size']} {bytes2human(quality['filesize'])}\n"

        audio_keyboard = []
        for audio in info_dict["formats"]:
            if audio["ext"] == "m4a":
                audio_keyboard.append(
                    {
                        "text": f"{self.strings['audio']} ({audio['format_note']})",
                        "callback": self.download,
                        "args": (
                            info_dict["id"],
                            quality["ext"],
                            quality["format_id"],
                            audio["format_id"],
                            chat_id,
                        ),
                    },
                )
        audio_keyboard.append(
            {
                "text": "Back",
                "callback": self.back,
                "args": (
                    info_dict,
                    chat_id,
                ),
            },
        )

        await call.edit(
            text=string,
            reply_markup=audio_keyboard,
        )

    async def back(self, call: InlineCall, info_dict: dict, chat_id: int):
        formats_list = []
        for item in info_dict["formats"]:
            if item["ext"] in ["mp4", "webm"] and item["vcodec"] != "none":
                formats_list.append(
                    {
                        "text": f"{item['format_note']} ({item['video_ext']})",
                        "callback": self.format_change,
                        "args": (item, info_dict, chat_id, item["format_id"]),
                    }
                )

        caption = f"<b>{info_dict['title']}</b>\n\n"
        # caption += info_dict["description"]

        await call.edit(text=caption, reply_markup=utils.chunks(formats_list, 2))

    async def download(
        self,
        call: InlineCall,
        video_id: str,
        ext: str,
        video_format: int,
        audio_format: int,
        chat_id: int,
    ):
        processed = []

        async def my_callback(current: int, total: int):
            nonlocal call, processed
            percentage = round(current * 100 / total)
            if percentage in processed:
                return

            processed += [percentage]
            if percentage % 10 == 0:
                await call.edit(
                    text=f"{self.strings['uploading']} <b>{progressbar(percentage,20)} {percentage}%</b>",
                )

        meta = {}

        def download():
            nonlocal meta
            with yt_dlp.YoutubeDL(
                {
                    "format": "{}+{}".format(str(video_format), str(audio_format)),
                    "outtmpl": "%(resolution)s.%(id)s.%(ext)s",
                }
            ) as yd:
                meta = yd.extract_info(
                    "https://www.youtube.com/watch?v=" + video_id, download=False
                )
                yd.download("https://www.youtube.com/watch?v=" + video_id)

        await call.edit(
            text=f"{self.strings['downloading']}",
        )
        await utils.run_sync(download)

        with open(
            "{0}x{1}.{2}.{3}".format(
                (meta["width"]),
                (meta["height"]),
                (meta["id"]),
                (meta["ext"].replace("webm", "mkv")),
            ),
            "rb",
        ) as input_file:
            content = input_file.read()
            input_file.seek(0)
            await self._client.send_file(
                chat_id,
                await self.fast_upload(
                    input_file, my_callback, f"video.{ext.replace('webm','mkv')}"
                ),
                supports_streaming=True,
            )
            os.remove(
                "{0}x{1}.{2}.{3}".format(
                    (meta["width"]),
                    (meta["height"]),
                    (meta["id"]),
                    (meta["ext"].replace("webm", "mkv")),
                )
            )
            await call.delete()
