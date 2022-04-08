"""

    █▀▀ ▄▀█ █▄▀ █▀▀ █▀ ▀█▀ █░█░█ █ ▀▄▀
    █▄▄ █▀█ █░█ ██▄ ▄█ ░█░ ▀▄▀▄▀ █ █░█

    Copyleft 2022 t.me/CakesTwix                                                            
    This program is free software; you can redistribute it and/or modify 

"""

__version__ = (1, 0, 1)

# requires: transmission-rpc
# scope: inline
# scope: geektg_only
# scope: geektg_min 3.1.15
# meta pic: https://iconarchive.com/download/i80732/johnathanmac/mavrick/Transmission.ico
# meta developer: @CakesTwix

import logging
from .. import loader, utils
import asyncio
from telethon.tl.functions.channels import CreateChannelRequest
from ..inline import GeekInlineQuery, rand
from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.utils.exceptions import MessageNotModified

from transmission_rpc import Client
from transmission_rpc.utils import format_size
from transmission_rpc.error import TransmissionConnectError

logger = logging.getLogger(__name__)                  

@loader.unrestricted
@loader.ratelimit
@loader.tds
class TransmissionMod(loader.Module):
    """Simple torrent client for Transmission"""
    
    strings = {"name": "Transmission",
                "cfg_username":"Username",
                "cfg_password":"Password",
                "cfg_port":"Post (9091)",
                "cfg_host":"Host (localhost)",
                "cfg_protocol":"Protocol (http)",
                "cfg_rpc":"RPC url (/transmission/)",
                "not_ready":"Pls check config",
                "torrent_name": "<b>Name:</b> ",
                "torrent_status": "<b>Status:</b> ",
                "torrent_hash": "<b>Hash:</b> ",
                "torrent_dir": "<b>Directory:</b> ",
                "torrent_size": "<b>Size:</b> ",
                "kb_update": "🔄 Update",
                "kb_close": "🚫 Close",
                "torrent_eta": "ETA: ",
                "torrent_error": "<b>Torrent not found in result</b>",
                "kb_start": "▶️",
                "kb_stop": "⏹",
                "kb_delete": "❌ Delete torrent ❌",
                "kb_delete_data": "❌ Delete torrent with data ❌",
                "answer_start": "Torrent starting",
                "answer_stop": "Torrent stopped",
                "answer_delete": "Torrent removed",
                "inline_title": "Torrent Manager",
                "inline_desc": "ℹ Click to view the parameters",
                "inline_answer": "ℹ No changes"
                }

    def stringTorrent(self, torrent):
        torrent_text = f"{self.strings['torrent_name']}{torrent.name} \n"
        torrent_text += f"{self.strings['torrent_status']}{torrent.status} \n"
        torrent_text += f"{self.strings['torrent_eta']}{torrent.format_eta()} \n"
        torrent_text += f"{self.strings['torrent_hash']}{torrent.hashString} \n"
        torrent_text += f"{self.strings['torrent_size']}{format_size(torrent.total_size)[0]} {format_size(torrent.total_size)[1]} \n"
        torrent_text += f"{self.strings['torrent_dir']}{torrent.download_dir} \n"

        return torrent_text

    def __init__(self):
        self.config = loader.ModuleConfig("username", None, lambda m: self.strings("cfg_username", m),
                                          "password", None, lambda m: self.strings("cfg_password", m),
                                          "port", 9091, lambda m: self.strings("cfg_port", m),
                                          "host", "127.0.0.1", lambda m: self.strings("cfg_host", m),
                                          "protocol", "http", lambda m: self.strings("cfg_protocol", m),
                                          "rpc", "/transmission/", lambda m: self.strings("cfg_rpc", m))
        self.name = self.strings["name"]
        
        # Check Transmission Server
        self.is_ready = False
        try:
            self.TransmissionClientUserBot = Client(host=self.config["host"], 
                   port=self.config["port"], 
                   username=self.config["username"], 
                   password=self.config["password"],
                   path=self.config["rpc"],
                   protocol=self.config["protocol"])
            self.is_ready = True
        except TransmissionConnectError:
            pass

    async def client_ready(self, client, db):
        self._client = client
        self._me = await client.get_me(True)


    @loader.unrestricted
    @loader.ratelimit
    async def tinfocmd(self, message):
        """Useful information about transmission server"""
        if self.is_ready:
            session_stats = self.TransmissionClientUserBot.session_stats()

            timeout = self.TransmissionClientUserBot.timeout
            rpc_version = self.TransmissionClientUserBot.rpc_version
            is_port_open = self.TransmissionClientUserBot.port_test()
            port = session_stats.peer_port
            download_dir = session_stats.download_dir
            free_space = self.TransmissionClientUserBot.free_space(download_dir)

            string = "Info about your Transmission Server\n\n"
            string += f"RPC version : {rpc_version}\n"
            string += f"Current timeout for HTTP queries : {timeout}\n"
            string += f"Port is open : {is_port_open}\n"
            string += f"Port : {port}\n"
            string += f"Download path : {download_dir}\n"
            string += f"Free space : {format_size(free_space)[0]} {format_size(free_space)[1]}\n"
            await utils.answer(message, string)
        else:
            await utils.answer(message, self.strings["not_ready"])
            await asyncio.sleep(5)
            await message.delete()


    @loader.unrestricted
    @loader.ratelimit
    async def tdownloadcmd(self, message):
        """Download Torrent file"""

        reply, args = await message.get_reply_message(), utils.get_args_raw(message)
        if reply:
            if reply.media.document.mime_type == 'application/x-bittorrent':
                path = await self._client.download_media(reply.media, "scam.torrent")
                torrent = self.TransmissionClientUserBot.add_torrent("file://scam.torrent", download_dir=args if args else None)

                kb = [
                    [{"text": self.strings['kb_update'], "callback": self.inline_update_torrent, "args": [torrent.id]}],
                    [{"text": self.strings['kb_start'], "callback": self.inline__start, "args": [torrent.id]},
                     {"text": self.strings['kb_stop'], "callback": self.inline__stop, "args": [torrent.id]}],
                    [{"text": self.strings['kb_delete_data'], "callback": self.inline__delete, "args": [torrent.id, True]},
                     {"text": self.strings['kb_delete'], "callback": self.inline__delete, "args": [torrent.id, False]}],
                    [{"text": self.strings['kb_close'], "callback": self.inline__close}],
                ]

                await self.inline.form(
                    self.stringTorrent(self.TransmissionClientUserBot.get_torrent(torrent.id)),
                    message=message,
                    reply_markup=kb,
                    always_allow=self._client.dispatcher.security._owner,
                )

    async def transmission_inline_handler(self, query: GeekInlineQuery) -> None:
        """
        General info (Inline)
        """
        args = query.args
        param = {"list": "List of 10 torrents",
                 "search": "Search torrents by name"
        }
        param_text = "<b>Available parameters: </b>\n"
        for item in param:
            param_text += f"⦁ {item} - {param[item]}\n"

        if not args:
            await query.answer([
                    InlineQueryResultArticle(
                        id=1,
                        title=self.strings["inline_title"],
                        description=self.strings["inline_desc"],
                        input_message_content=InputTextMessageContent(
                            param_text, "HTML", disable_web_page_preview=True
                        ),
                        thumb_url="https://img.icons8.com/ios-filled/128/26e07f/torrent.png",
                        thumb_width=128,
                        thumb_height=128,
                    )
                ], cache_time=0)
            return

        if "list" in args:
            kb_torrent_list = []
            for torrent in self.TransmissionClientUserBot.get_torrents():
                
                torrent_markup = InlineKeyboardMarkup(row_width=3)
                torrent_markup.insert(
                    InlineKeyboardButton(self.strings['kb_update'], callback_data="cake_update" + str(torrent.id)),
                )
                torrent_markup.add(
                    InlineKeyboardButton(self.strings['kb_start'], callback_data="cake_start" + str(torrent.id)),
                    InlineKeyboardButton(self.strings['kb_stop'], callback_data="cake_stop" + str(torrent.id))
                )
                torrent_markup.add(
                    InlineKeyboardButton(self.strings['kb_delete_data'], callback_data="cake_delete" + str(torrent.id)),
                    InlineKeyboardButton(self.strings['kb_delete'], callback_data="cake_remove" + str(torrent.id))
                )

                kb_torrent_list.append(
                    InlineQueryResultArticle(
                        id=rand(10),
                        title=torrent.name,
                        description=self.strings["inline_desc"],
                        input_message_content=InputTextMessageContent(
                            self.stringTorrent(self.TransmissionClientUserBot.get_torrent(torrent.id)), "HTML", disable_web_page_preview=True
                        ),
                        reply_markup=torrent_markup,
                    )
                )
                if len(kb_torrent_list) == 10:
                    break
            
            await query.answer(kb_torrent_list[:10], cache_time=0)
            return
        
        if "search" in args:
            search_arg = " ".join(args.split()[1:]) # transmission search BlaBlaBla
            kb_torrent_list = []
            for torrent in self.TransmissionClientUserBot.get_torrents():
                if search_arg in torrent.name:

                    torrent_markup = InlineKeyboardMarkup(row_width=3)
                    
                    torrent_markup.insert(
                        InlineKeyboardButton(self.strings['kb_update'], callback_data="cake_update" + str(torrent.id)),
                    )
                    torrent_markup.add(
                        InlineKeyboardButton(self.strings['kb_start'], callback_data="cake_start" + str(torrent.id)),
                        InlineKeyboardButton(self.strings['kb_stop'], callback_data="cake_stop" + str(torrent.id))
                    )
                    torrent_markup.add(
                        InlineKeyboardButton(self.strings['kb_delete_data'], callback_data="cake_delete" + str(torrent.id)),
                        InlineKeyboardButton(self.strings['kb_delete'], callback_data="cake_remove" + str(torrent.id))
                    )

                    kb_torrent_list.append(
                        InlineQueryResultArticle(
                            id=rand(20),
                            title=torrent.name,
                            description=self.strings["inline_desc"],
                            input_message_content=InputTextMessageContent(
                                self.stringTorrent(self.TransmissionClientUserBot.get_torrent(torrent.id)), "HTML", disable_web_page_preview=True
                            ),
                            reply_markup=torrent_markup,
                        )
                    )
            
            return await query.answer(kb_torrent_list[:10], cache_time=0)
            

    
    # Inline button handler 
    async def inline__close(self, call) -> None:
        await call.delete()

    async def inline_update_torrent(self, call, torrent_id) -> None:
        kb = [
            [{"text": self.strings['kb_update'], "callback": self.inline_update_torrent, "args": [torrent_id]}],
            [{"text": self.strings['kb_start'], "callback": self.inline__start, "args": [torrent_id]},
             {"text": self.strings['kb_stop'], "callback": self.inline__stop, "args": [torrent_id]}],
            [{"text": self.strings['kb_delete_data'], "callback": self.inline__delete, "args": [torrent_id, True]},
             {"text": self.strings['kb_delete'], "callback": self.inline__delete, "args": [torrent_id, False]}],
            [{"text": self.strings['kb_close'], "callback": self.inline__close}],
        ]
        try:
            await call.edit(self.stringTorrent(self.TransmissionClientUserBot.get_torrent(torrent_id)), reply_markup=kb)
        except KeyError:
            await call.edit(self.strings['torrent_error'])

    async def inline__start(self, call, torrent_id) -> None:
        self.TransmissionClientUserBot.get_torrent(torrent_id).start()
        await call.answer(self.strings['answer_start'])
    
    async def inline__stop(self, call, torrent_id) -> None:
        self.TransmissionClientUserBot.get_torrent(torrent_id).stop()
        await call.answer(self.strings['answer_stop'])

    async def inline__delete(self, call, torrent_id, delete_data) -> None:
        self.TransmissionClientUserBot.remove_torrent(torrent_id, delete_data)
        await call.answer(self.strings['answer_delete'])


    # Callback buttons (for Inline search)
    async def button_callback_handler(self, call: CallbackQuery) -> None:
        """
        Process button presses
        """
        # await call.answer(call.data, show_alert=True) # Debug

        # Update
        if call.data[:11] == "cake_update":

            torrent_markup = InlineKeyboardMarkup(row_width=3)
            torrent_markup.insert(
                InlineKeyboardButton(self.strings['kb_update'], callback_data="cake_update" + str(call.data[11:])),
            )
            torrent_markup.add(
                InlineKeyboardButton(self.strings['kb_start'], callback_data="cake_start" + str(call.data[10:])),
                InlineKeyboardButton(self.strings['kb_stop'], callback_data="cake_stop" + str(call.data[9:]))
            )
            torrent_markup.add(
                InlineKeyboardButton(self.strings['kb_delete_data'], callback_data="cake_detete" + str(call.data[11:])),
                InlineKeyboardButton(self.strings['kb_delete'], callback_data="cake_remove" + str(call.data[11:]))
            )

            try:
                torrent = self.TransmissionClientUserBot.get_torrent(int(call.data[11:]))
                await self.inline.bot.edit_message_text(self.stringTorrent(torrent), reply_markup=torrent_markup, inline_message_id=call.inline_message_id, parse_mode="HTML")
            except KeyError:
                await self.inline.bot.edit_message_text(self.strings['torrent_error'], inline_message_id=call.inline_message_id, parse_mode="HTML")
            except MessageNotModified:
                await call.answer(self.strings["inline_answer"])
        
        # Start
        if call.data[:10] == "cake_start":
            self.TransmissionClientUserBot.get_torrent(int(call.data[11:])).start()
            return await call.answer(self.strings['answer_start'])

        # Stop
        if call.data[:9] == "cake_stop":
            self.TransmissionClientUserBot.get_torrent(int(call.data[11:])).stop()
            return await call.answer(self.strings['answer_stop'])

        # Delete torrent with data
        if call.data[:11] == "cake_delete":
            self.TransmissionClientUserBot.remove_torrent(int(call.data[11:]), True)
            return await call.answer(self.strings['answer_delete'])

        # Just delete torrent
        if call.data[:11] == "cake_remove":
            self.TransmissionClientUserBot.remove_torrent(int(call.data[11:]), False)
            return await call.answer(self.strings['answer_delete'])