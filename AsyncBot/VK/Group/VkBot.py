import asyncio
import time
from typing import *

import AsyncBot.VK.Message
from AsyncBot import Logger
from AsyncBot.VK.Group.GroupSession import GroupSession
from AsyncBot.VK.Group.LongPollServer import LongPollServer
from AsyncBot.VK.Group.Events import Events


class VkBot:
    def __init__(self, access_token: str, group_id, bot_admin, logger=None, log_file='', log_to_file=False,
                 log_to_console=True):
        if logger is None:
            logger = Logger.Logger(log_to_console, log_to_file, log_file)
        self.logger: Logger = logger
        self.vk_session = GroupSession(access_token=access_token,
                                       group_id=group_id)
        self.bot_admin: int = bot_admin
        self.server: LongPollServer = LongPollServer(self.vk_session, logger=logger)
        self.commands: dict = {}
        self.is_running = False
        self.events: Dict[str: Coroutine] = {
            Events.MESSAGE_NEW: self.on_message_new,
            Events.MESSAGE_EDIT: self.on_message_edit
        }

    def start(self):
        asyncio.run(self.run())

    async def run(self):
        self.is_running = True
        try:
            async for event, context in self.server.listen():
                try:
                    await self.events[event](**context)
                except KeyError:
                    pass
                if not self.is_running:
                    asyncio.get_event_loop().close()
                    break
        except Exception as e:
            await self.logger.log(f'Crushed with:\n{e}', method_name='VkBot.run()')

    async def on_message_new(self, message: AsyncBot.VK.Message.Message):
        asyncio.create_task(
            self.logger.log(
                text=f'Message from {message.sender.first_name} {message.sender.last_name} ({message.sender.id}) '
                     f'in {message.chat.title} '
                     f'at {time.strftime("%x %X", message.date)}:\n{message.text}',
                method_name='VkBot.run()')
        )

    async def on_message_edit(self, message: AsyncBot.VK.Message.Message):
        asyncio.create_task(
            self.logger.log(
                text=f'Message edited by {message.sender.first_name} {message.sender.last_name} ({message.sender.id}) '
                     f'in {message.chat.title} '
                     f'at {time.strftime("%x %X", message.date)}:\n{message.text}',
                method_name='VkBot.run()')
        )
