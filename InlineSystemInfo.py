"""

    █▀▀ ▄▀█ █▄▀ █▀▀ █▀ ▀█▀ █░█░█ █ ▀▄▀
    █▄▄ █▀█ █░█ ██▄ ▄█ ░█░ ▀▄▀▄▀ █ █░█

    Copyleft 2022 t.me/CakesTwix
    This program is free software; you can redistribute it and/or modify

"""

__version__ = (1, 0, 2)

# requires: psutil py-cpuinfo tqdm
# meta pic: https://icon-library.com/images/system-information-icon/system-information-icon-19.jpg
# meta developer: @CakesTwix
# scope: inline
# scope: hikka_min 1.1.2
# scope: hikka_only 

import datetime
import logging
from typing import Union

import cpuinfo
import psutil
import tqdm
from aiogram.utils.markdown import quote_html

from .. import loader, utils

logger = logging.getLogger(__name__)

# From Hikka https://github.com/hikariatama/Hikka/blob/master/hikka/utils.py#L459-L461
def chunks(_list: Union[list, tuple, set], n: int, /) -> list:
    """Split provided `_list` into chunks of `n`"""
    return [_list[i : i + n] for i in range(0, len(_list), n)]


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


@loader.tds
class InlineSystemInfoMod(loader.Module):
    """Get detailed information about your server"""

    strings = {
        "name": "InlineSystemInfo",
        2: "IPv4",
        10: "IPv6",
        17: "Link",
    }

    def menu_keyboard(self) -> list:
        return [
            {"text": "🧠 CPU", "callback": self.change_stuff, "args": ("CPU",)},
            {"text": "💽 Disk", "callback": self.change_stuff, "args": ("Disk",)},
            {
                "text": "🌐 Network Address",
                "callback": self.change_stuff,
                "args": ("Network Address",),
            },
            {
                "text": "🌐 Network Stats",
                "callback": self.change_stuff,
                "args": ("Network Stats",),
            },
            {"text": "🗄 Memory", "callback": self.change_stuff, "args": ("Memory",)},
            {"text": "🌡 Sensors", "callback": self.change_stuff, "args": ("Sensors",)},
        ]

    def cpu_string(self):
        string = "🧠  <b>CPU Info</b>\n"
        string += f"⦁ <b>Name</b>: {self.cpu_info.get('brand_raw', 'Undetermined.')} ({self.cpu_info['arch_string_raw']})\n"
        string += f"⦁ <b>Count</b>: {self.cpu_count_logic} ({self.cpu_count})\n"
        string += f"⦁ <b>Freq</b>: {self.cpu_freq[0]} (max: {self.cpu_freq[2]} / min: {self.cpu_freq[1]})\n" if self.cpu_freq else ""
        string += f"⦁ <b>Flags</b>: {' '.join(self.cpu_info['flags'])}\n"
        string += f"⦁ <b>Load avg</b>: {self.loadavg[0]} {self.loadavg[1]} {self.loadavg[2]}\n"

        return string

    def disks_string(self):
        string = "💽  <b>Disk Info</b>\n"
        for disk in self.disk_partitions:
            disk_usage = psutil.disk_usage(disk.mountpoint)

            string += f"<b>{disk.device}</b>\n"
            string += f"├── <b>Mount</b> {disk.mountpoint}\n"
            string += f"├── <b>FS</b> {disk.fstype}\n"
            string += f"├── <b>Disk Usage</b> {disk_usage.percent}% ({bytes2human(disk_usage.used)}/{bytes2human(disk_usage.total)})\n"
            string += f"│       └──{tqdm.tqdm(total=100, initial=disk_usage.percent, bar_format='[{bar}] {n_fmt}/{total_fmt}')}\n"
            string += f"└── <b>Options</b> {disk.opts}\n\n"

        return string

    def network_addr_string(self):
        string = "🌐  <b>Network Info</b>\n"
        string += "<b>Address</b>:\n"
        for interf in self.net_if_addrs:
            interface = self.net_if_addrs[interf]
            string += f"<b>{interf}</b>\n"
            for addr in interface:
                attr = [
                    a
                    for a in dir(psutil.net_if_addrs()[interf][0])
                    if not a.startswith("__")
                    and not a.startswith("_")
                    and not callable(getattr(psutil.net_if_addrs()[interf][0], a))
                ]
                string += f"{self.strings[getattr(addr, 'family')]}\n"
                for item in attr[:-1]:
                    string += f"├── {item}: {getattr(addr, item)}\n"
                else:
                    string += f"└── {attr[-1]}: {getattr(addr, attr[-1])}\n"
            string += "\n"

        return string

    def memory_string(self):
        string = "🗄  <b>Memory Info</b>\n"
        string += f'<b>RAM</b>: {tqdm.tqdm(ncols=30, total=100, initial=self.virtual_memory.percent, bar_format="[{bar}] {n_fmt}/{total_fmt}")} <code>({bytes2human(self.virtual_memory.used)}/{bytes2human(self.virtual_memory.total)})</code>\n'
        string += f'<b>Swap</b>: {tqdm.tqdm(ncols=30, total=100, initial=self.swap_memory.percent, bar_format="[{bar}] {n_fmt}/{total_fmt}")} <code>({bytes2human(self.swap_memory.used)}/{bytes2human(self.swap_memory.total)})</code>\n'

        return string

    def sensors_string(self):
        string = "🌡  <b>Sensors Info</b>\n"
        string += "<b>Temperature</b>:\n"
        for sensor_name in self.sensors_temperatures:
            sensor = self.sensors_temperatures[sensor_name]
            string += f"<b>{sensor_name}</b>\n"
            for sensor_info in sensor:
                attr = [
                    a
                    for a in dir(sensor_info)
                    if not a.startswith("__")
                    and not a.startswith("_")
                    and not callable(getattr(sensor_info, a))
                ]
                for item in attr[:-1]:
                    string += f"├── {item}: {getattr(sensor_info, item)}\n"
                else:
                    string += f"└── {attr[-1]}: {getattr(sensor_info, attr[-1])}\n"
            string += "\n"

        if self.sensors_fans:
            string += "<b>Fans</b>:"
            for sensor_name in self.sensors_fans:
                sensor = self.sensors_fans[sensor_name]
                string += f"<b>{sensor_name}</b>\n"
                for sensor_info in sensor:
                    attr = [
                        a
                        for a in dir(sensor_info)
                        if not a.startswith("__")
                        and not a.startswith("_")
                        and not callable(getattr(sensor_info, a))
                    ]
                    for item in attr[:-1]:
                        string += f"├── {item}: {getattr(sensor_info, item)}\n"
                    else:
                        string += f"└── {attr[-1]}: {getattr(sensor_info, attr[-1])}\n"

        return string

    def network_stats_string(self):
        string = "🌐  <b>Network Info</b>\n"
        string += "<b>Stats</b>:\n"
        for interf in self.net_if_stats:
            interface = self.net_if_stats[interf]
            string += f"<b>{interf}</b>\n"
            string += f"└── {quote_html(interface)}\n\n"

        return string

    def __init__(self):
        # CPU stuff
        self.cpu_percent = psutil.cpu_percent(interval=None)
        self.cpu_count_logic = psutil.cpu_count()
        self.cpu_count = psutil.cpu_count(logical=False)
        self.cpu_freq = psutil.cpu_freq()
        self.cpu_info = cpuinfo.get_cpu_info()

        # Linux stuff
        self.loadavg = psutil.getloadavg()

        # Memory
        self.virtual_memory = psutil.virtual_memory()
        self.swap_memory = psutil.swap_memory()

        # Disks
        self.disk_partitions = psutil.disk_partitions()

        # Network
        self.net_if_addrs = psutil.net_if_addrs()
        self.net_if_stats = psutil.net_if_stats()

        # Sensors
        self.sensors_temperatures = psutil.sensors_temperatures()
        self.sensors_fans = psutil.sensors_fans()
        self.sensors_battery = psutil.sensors_battery()

        # Other
        self.boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.version_info = psutil.version_info

        # Generate string

        self.info_string = {
            "CPU": self.cpu_string(),
            "Disk": self.disks_string(),
            "Network Address": self.network_addr_string(),
            "Network Stats": self.network_stats_string(),
            "Memory": self.memory_string(),
            "Sensors": self.sensors_string(),
        }

    async def serverstatscmd(self, message):
        """Get information about your server"""
        await self.inline.form(
            text=self.cpu_string(),
            message=message,
            reply_markup=chunks(self.menu_keyboard(), 2),
        )

    # Inline callback

    async def change_stuff(self, call, stuff):
        await call.edit(
            text=self.info_string[stuff],
            reply_markup=chunks(self.menu_keyboard(), 2),
        )
