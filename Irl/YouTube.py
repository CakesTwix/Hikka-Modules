"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.

    Modified by @CakesTwix. 
"""

# <3 title: YouTube
# <3 pic: https://img.icons8.com/fluency/50/000000/youtube.png
# <3 desc: Скачать видео с YouTube

from PIL import Image
from .. import loader, utils
import requests
import json
from pytube import YouTube
import os
from io import BytesIO
import subprocess
# requires: pytube PIL

@loader.tds
class YouTubeMod(loader.Module):
    """Download YouTube video"""
    strings = {
        'name': 'YouTube',
        'args': '🎞 <b>You need to specify link</b>',
        'downloading': '🎞 <b>Downloading...</b>',
        'not_found': '🎞 <b>Video not found...</b>'
    }

    thumbnail_url = ''

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.unrestricted
    async def ytcmd(self, message):
        """[mp3] <link> - Download video from youtube"""
        args = utils.get_args_raw(message)
        message = await utils.answer(message, self.strings('downloading'))
        try:
            message = message[0]
        except: pass
        ext = False
        if len(args.split()) > 1:
            ext, args = args.split(maxsplit=1)

        if not args:
            return await utils.answer(message, self.strings('args'))

        def dlyt(self, videourl, path):
            yt = YouTube(videourl)
            self.thumbnail_url = yt.thumbnail_url
            yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            return yt.download(path)

        def convert_video_to_audio_ffmpeg(video_file, output_ext="mp3"):
            filename, ext = os.path.splitext(video_file)
            out = f"{filename}.{output_ext}"
            subprocess.call(["ffmpeg", "-y", "-i", video_file, out], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            os.remove(video_file)
            return out

        path = '/tmp'
        try:
            path = await utils.run_sync(dlyt, self, args, path)
        except:
            return await utils.answer(message, self.strings('not_found'))

        filename, ext_ = os.path.splitext(path)
        response = requests.get(self.thumbnail_url)

        im = Image.open(BytesIO(response.content))
        # im = im.resize((320,320)) 

        with BytesIO() as output:
            im.save(output, 'png')
            contents = output.getvalue()


        if ext == 'mp3':
            path = convert_video_to_audio_ffmpeg(path)

        await self.client.send_file(message.peer_id, path, supports_streaming=True, 
                                    caption=filename[5:], thumb=contents)
        os.remove(path)
        await message.delete()


