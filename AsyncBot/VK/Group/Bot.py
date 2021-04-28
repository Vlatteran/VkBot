import asyncio
import time

from AsyncBot import Logger
from AsyncBot.VK.Group.EventHandler import EventHandler
from AsyncBot.VK.Group.GroupSession import GroupSession
from AsyncBot.VK.Group.LongPollServer import LongPollServer
from AsyncBot.VK.Message import Message


class Bot(EventHandler):

    def __init__(self, access_token: str, group_id, bot_admin, logger=None, log_file='', log_to_file=False,
                 log_to_console=True):
        if logger is None:
            logger = Logger.Logger(log_to_console, log_to_file, log_file)
        self.logger: Logger = logger
        self.session = GroupSession(access_token=access_token,
                                    group_id=group_id)
        self.bot_admin: int = bot_admin
        self.server: LongPollServer = LongPollServer(self.session, logger=logger)

        self.is_running = False
        self.commands: dict = {}

        @self.command(name='stop')
        async def stop(args, message):
            if message.sender.id == self.bot_admin:
                self.is_running = False
            else:
                await message.reply("You don't have permissions to stop bot")

    def start(self):
        asyncio.run(self.run())

    async def run(self):
        self.is_running = True
        try:
            async for event, context in self.server.listen():
                try:
                    await event(context, self)
                except KeyError as e:
                    print(e)
                except Exception as e:
                    print(e)
                if not self.is_running:
                    asyncio.get_event_loop().close()
                    break
        except Exception as e:
            await self.logger.log(f'Crushed with:\n{e}', method_name='Bot.run()')

    async def on_message_new(self, message: Message, client_info: dict):
        asyncio.create_task(
            self.logger.log(
                text=f'Message from {message.sender.first_name} {message.sender.last_name} ({message.sender.id}) '
                     f'in {message.chat.title} '
                     f'at {time.strftime("%x %X", message.date)}:\n{message.text}',
                method_name='Bot.run()')
        )
        if len(message.text) > 1 and message.text[0] == '!':
            temp = message.text[1:].split(' ')
            command = temp[0]
            args = temp[1:]
            try:
                await self.commands[command](args, message)
            except KeyError:
                pass

    async def on_message_edit(self, message: Message):
        asyncio.create_task(
            self.logger.log(
                text=f'Message edited by {message.sender.first_name} {message.sender.last_name} ({message.sender.id}) '
                     f'in {message.chat.title} '
                     f'at {time.strftime("%x %X", message.date)}:\n{message.text}',
                method_name='Bot.run()')
        )

    def command(self, name: str):
        def decorator(func):
            self.commands[name] = func

            async def wrapper(args: list, message: Message):
                return func(args, message)

            return wrapper

        return decorator
