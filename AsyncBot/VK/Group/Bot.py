import asyncio
import logging
import time
import typing


from AsyncBot.VK.Group.EventHandler import EventHandler
from AsyncBot.VK.Group.GroupSession import GroupSession
from AsyncBot.VK.Group.LongPollServer import LongPollServer
from AsyncBot.VK.Message import Message


class Bot(EventHandler):
    """
    Class, that implements the GroupBot.

    Attributes:

    """

    def __init__(self, access_token: str, group_id, bot_admin:int, log_file='', loglevel=logging.INFO):
        self.session = GroupSession(access_token=access_token,
                                    group_id=group_id)
        self.bot_admin: int = bot_admin
        self.server: LongPollServer = LongPollServer(self.session)

        self.is_running = False
        self.commands: dict = {}
        log_form = "{asctime} - [{levelname}] - ({filename}:{lineno}).{funcName} - {message}" # noqa
        logging.basicConfig(filename=log_file, # noqa
                            level=loglevel,
                            format=log_form,
                            style='{',
                            datefmt='%Y-%m-%d %H:%M:%S'
                            )

        @self.command(name='stop')
        async def stop(args, message: Message):
            if message.sender.id == self.bot_admin:
                self.is_running = False
            else:
                await message.reply("You don't have permissions to stop bot")

    def start(self):
        """
        Function that stars event loop of bot
        """
        asyncio.run(self.run())

    async def run(self):
        """
        Function that contains main loop
        """
        self.is_running = True
        async for event, context in self.server.listen():
            try:
                asyncio.create_task(event(context, self))
            except KeyError as e:
                print(e)
            except Exception as e:
                print(e)
            if not self.is_running:
                asyncio.get_event_loop().close()
                break

    async def on_message_new(self, message: Message, client_info: dict):
        logging.info(
            msg=f'Message from {message.sender.first_name} {message.sender.last_name} ({message.sender.id}) '
                f'in {message.chat.title}:\n{message.text}')
        if len(message.text) > 1 and message.text[0] == '!':
            temp = message.text[1:].split(' ')
            command = temp[0]
            args = temp[1:]
            try:
                await self.commands[command](args, message)
            except KeyError:
                await message.reply('There is no command with such name')

    async def on_message_edit(self, message: Message):
        logging.info(
            f'Message edited by {message.sender.first_name} {message.sender.last_name} ({message.sender.id}) '
            f'in {message.chat.title} '
            f'at {time.strftime("%x %X", message.date)}:\n{message.text}')

    def command(self, name: str):
        """
        Decorator, that adds function to list of commands

        Args:
            name: alias for calling command
        """

        def decorator(func: typing.Callable[[list, Message], None]):
            self.commands[name] = func

            async def wrapper(args: list, message: Message):
                return func(args, message)

            return wrapper

        return decorator
