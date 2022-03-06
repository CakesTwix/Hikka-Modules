# requires: aiohttp

import logging
import aiohttp
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class CustomRomsMiscMod(loader.Module):
    """Module for determining the location of parcels via the mail API"""

    strings = {
        "name": "Mail",
    }

    @loader.unrestricted
    @loader.ratelimit
    async def npcmd(self, message):
        """Нова Пошта"""
        args = utils.get_args(message)
        if args:
            document_number = args[0].lower()

            data = {
                "apiKey": "abe3a74549c55e4b703ed042c5169406",
                "modelName": "TrackingDocument",
                "calledMethod": "getStatusDocuments",
                "methodProperties": {
                    "Documents": [{"DocumentNumber": document_number, "Phone": ""}]
                },
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.novaposhta.ua/v2.0/json/", json=data
                ) as get:
                    answer = await get.json()
                    await session.close()
            item = answer["data"][0]

            caption = f"Экспресс-накладная: {item['Number']}"
            caption += f"\nСтатус: {item['Status']}"
            if "DateCreated" in item:
                caption += f"\nБыло создано: {item['DateCreated']}"
                caption += f"\nОжид. дата доставки: {item['ScheduledDeliveryDate']}"
                caption += f"\n{item['CitySender']} -> {item['CityRecipient']}"

            if item.get("DocumentCost") is not None:
                caption += f"\nЦена доставки: {item['DocumentCost']} грн."

            await utils.answer(message, caption)
