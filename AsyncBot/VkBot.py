import asyncio
import random
import time

import aiohttp
from requests import get

import Logger
from schedule import Schedule


class VkBot:
    def __init__(self, access_token, group_id, bot_admin, logger=None, log_file='', log_to_file=False,
                 log_to_console=True):
        if logger is None:
            logger = Logger.Logger(log_to_console, log_to_file, log_file)
        self.logger = logger
        self.access_token = access_token
        self.group_id = group_id
        self.bot_admin = bot_admin
        self.server = LongPollServer(access_token, group_id, self)
        self.schedule = Schedule()
        self.is_running = False
        self.commands = {}
        self.tasks = []

    def start(self):
        asyncio.run(self.run())

    async def run(self):
        self.is_running = True
        try:
            async for event, context in self.server.listen():
                if event == 'message_new':
                    self.tasks.append(asyncio.create_task(self.on_new_message(context)))
                if not self.is_running:
                    for task in self.tasks:
                        await task
                    break
        except Exception as e:

            self.tasks.append(
                asyncio.create_task(
                    self.logger.log(f'Crushed with:\n{e}', method_name='VkBot.run()')
                )
            )

    async def on_new_message(self, context):
        self.tasks.append(
            asyncio.create_task(
                self.logger.log(
                    text=f'Message from {context.sender.first_name} {context.sender.last_name} ({context.sender.id}) '
                         f'in {context.chat.title} '
                         f'at {time.strftime("%x %X", context.date)}:\n{context.text}',
                    method_name='VkBot.run()')
            )
        )


class LongPollServer:
    server: str
    key: str
    ts: str

    def __init__(self, access_token, group_id, vk):
        self.vk = vk
        self.access_token = access_token
        self.group_id = group_id
        asyncio.run(self.get_long_poll_server())

    async def get_long_poll_server(self):
        long_poll_serv = None
        try:
            url = f'https://api.vk.com/method/groups.getLongPollServer'
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params={'group_id': self.group_id,
                                                    'v': 5.126,
                                                    'access_token': self.access_token}) as resp:
                    long_poll_serv = await resp.json()

            long_poll_serv = long_poll_serv['response']
            self.server = long_poll_serv['server']
            self.key = long_poll_serv['key']
            self.ts = long_poll_serv['ts']
        except KeyError:
            self.vk.tasks.append(
                asyncio.create_task(
                    self.vk.logger.log(
                        long_poll_serv,
                        method_name='LongPollServer.get_long_poll_server()')
                )
            )

    async def check(self):
        result = None
        retries = 0
        while result is None:
            try:
                url = f"{self.server}?" \
                      f"act=a_check&" \
                      f"key={self.key}&" \
                      f"ts={self.ts}&" \
                      f"wait=25"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        result = await resp.json()
            except Exception as e:
                self.vk.tasks.append(
                    asyncio.create_task(
                        self.vk.logger.log(f'try{retries + 1}: failed with:\n{e}',
                                           method_name='LongPollServer.check()')
                    )
                )

                retries += 1
                if retries == 5:
                    self.vk.tasks.append(
                        asyncio.create_task(
                            self.vk.logger.log('to many tries', method_name='LongPollServer.check()')
                        )
                    )

        if 'failed' in result:
            self.vk.tasks.append(
                asyncio.create_task(
                    self.vk.logger.log(f'failed with:{result}', method_name='LongPollServer.check()')
                )
            )
            error = result['failed']
            if error == 1:
                self.ts = result['ts']
            elif error in (2, 3):
                await self.get_long_poll_server()
            else:
                self.vk.tasks.append(
                    asyncio.create_task(
                        self.vk.logger.log(f'Unexpected error code: {error}\n{result}',
                                           method_name='LongPollServer.check()')
                    )
                )

        else:
            self.ts = result['ts']
            events = result['updates']
            for event in events:
                if event['type'] == 'message_new':
                    yield 'message_new', Message(event['object']['message'], self.vk)

    async def listen(self):
        while True:
            result = self.check()
            if result is not None:
                async for event in result:
                    yield event


class Message:
    text: str

    def __init__(self, message_dict, vk: VkBot):
        self.vk = vk
        self.date = time.localtime(message_dict['date'])
        self.text = message_dict['text']
        self.sender = User(message_dict['from_id'], vk)
        self.chat = Chat(message_dict['peer_id'], vk)
        self.conversation_message_id = message_dict['conversation_message_id']

    async def reply(self, text):
        url = f'https://api.vk.com/method/messages.send?' \
              f'peer_id={self.chat.chat_id}&' \
              f'message={text}&' \
              f'forward={{"peer_id":{self.chat.chat_id},' \
              f'"conversation_message_ids":[{self.conversation_message_id}],' \
              f'"is_reply":1}}&' \
              f'group_id={self.vk.group_id}&' \
              f'access_token={self.vk.access_token}&' \
              f'random_id={random.randint(1, 2147123123)}&' \
              f'v=5.126'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()


class Chat:
    def __init__(self, chat_id, vk: VkBot):
        self.vk = vk
        result = get(f'https://api.vk.com/method/messages.getConversationsById?'
                     f'peer_ids={chat_id}&'
                     f'access_token={vk.access_token}&'
                     f'v=5.126').json()
        result = result['response']['items'][0]
        self.chat_id = chat_id
        if result['peer']['type'] == 'chat':
            self.title = result['chat_settings']['title']
            self.admins = [User(admin_id, vk) for admin_id in result['chat_settings']['admin_ids'] if admin_id > 0]
            self.member_count = result['chat_settings']['members_count']
        else:
            self.title = 'ЛС'

    async def send(self, text):
        url = f'https://api.vk.com/method/messages.send?' \
              f'peer_id={self.chat_id}&' \
              f'message={text}&' \
              f'group_id={self.vk.group_id}&' \
              f'access_token={self.vk.access_token}&' \
              f'random_id={random.randint(1, 2147123123)}&' \
              f'v=5.126'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.json()
                self.vk.tasks.append(
                    asyncio.create_task(
                        self.vk.logger.log(response)
                    )
                )
                return response


class User:
    def __init__(self, user_id, vk: VkBot):
        url = f'https://api.vk.com/method/users.get?' \
              f'user_ids={user_id}&' \
              f'access_token={vk.access_token}&' \
              f'v=5.126'
        result = get(url).json()['response'][0]
        self.id = user_id
        self.first_name = result['first_name']
        self.last_name = result['last_name']
