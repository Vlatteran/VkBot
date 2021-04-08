import asyncio
import random
import time

import aiohttp
from requests import get

import Logger
from schedule import Schedule


class VkSession:
    def __init__(self, access_token: str, api_version: int = 5.126):
        self.access_token: str = access_token
        self.api_version = api_version

    async def method(self, method: str, params: dict):
        url = f'https://api.vk.com/method/{method}'
        params |= {'access_token': self.access_token,
                   'v': self.api_version}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                return await resp.json()


class VkGroupSession(VkSession):
    def __init__(self, access_token: str, group_id: int, api_version: int = 5.126):
        super().__init__(access_token, api_version=api_version)
        self.group_id = group_id

    async def method(self, method: str, params: dict):
        params |= {'group_id': self.group_id}
        return await super().method(method=method, params=params)


class VkBot:
    def __init__(self, access_token: str, group_id, bot_admin, logger=None, log_file='', log_to_file=False,
                 log_to_console=True):
        if logger is None:
            logger = Logger.Logger(log_to_console, log_to_file, log_file)
        self.logger: Logger = logger
        self.vk_session = VkGroupSession(access_token=access_token,
                                         group_id=group_id)
        self.bot_admin: int = bot_admin
        self.server: LongPollServer = LongPollServer(self.vk_session, logger=logger)
        self.schedule = Schedule()
        self.is_running = False
        self.commands: dict = {}
        self.tasks: list = []

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

    def __init__(self, vk_session: VkGroupSession, logger: Logger):
        self.vk_session = vk_session
        self.logger: Logger = logger
        self.get_long_poll_server()

    def get_long_poll_server(self):
        long_poll_serv = None
        try:
            method = 'groups.getLongPollServer'

            long_poll_serv = asyncio.run(self.vk_session.method(method=method, params={}))

            long_poll_serv = long_poll_serv['response']
            self.server = long_poll_serv['server']
            self.key = long_poll_serv['key']
            self.ts = long_poll_serv['ts']
        except KeyError:
            pass
            # self.vk_session.tasks.append(
            #     asyncio.create_task(
            #         self.vk_session.logger.log(
            #             long_poll_serv,
            #             method_name='LongPollServer.get_long_poll_server()')
            #     )
            # )

    async def check(self):
        result = None
        retries = 0
        while result is None:
            try:
                params = {'act': 'a_check',
                          'key': self.key,
                          'ts': self.ts,
                          'wait': 25}
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.server, params=params) as resp:
                        result = await resp.json()
            except Exception as e:
                # self.vk_session.tasks.append(
                #     asyncio.create_task(
                #         self.vk_session.logger.log(f'try{retries + 1}: failed with:\n{e}',
                #                                    method_name='LongPollServer.check()')
                #     )
                # )

                retries += 1
                if retries == 5:
                    pass
                    # self.vk_session.tasks.append(
                    #     asyncio.create_task(
                    #         self.vk_session.logger.log('to many tries', method_name='LongPollServer.check()')
                    #     )
                    # )

        if 'failed' in result:
            # self.vk_session.tasks.append(
            #     asyncio.create_task(
            #         self.vk_session.logger.log(f'failed with:{result}', method_name='LongPollServer.check()')
            #     )
            # )
            error = result['failed']
            if error == 1:
                self.ts = result['ts']
            elif error in (2, 3):
                await self.get_long_poll_server()
            else:
                pass
                # self.vk_session.tasks.append(
                #     asyncio.create_task(
                #         self.vk_session.logger.log(f'Unexpected error code: {error}\n{result}',
                #                                    method_name='LongPollServer.check()')
                #     )
                # )

        else:
            self.ts = result['ts']
            events = result['updates']
            for event in events:
                if event['type'] == 'message_new':
                    yield 'message_new', Message(event['object']['message'], self.vk_session)

    async def listen(self):
        while True:
            result = self.check()
            if result is not None:
                async for event in result:
                    yield event


class Message:
    text: str

    def __init__(self, message_dict, vk_session: VkSession):
        self.vk_session = vk_session
        self.date = time.localtime(message_dict['date'])
        self.text = message_dict['text']
        self.sender = User(message_dict['from_id'], vk_session)
        self.chat = Chat(message_dict['peer_id'], vk_session)
        self.conversation_message_id = message_dict['conversation_message_id']

    async def reply(self, text, attachment=None):
        forward_message = (f'{{"peer_id":{self.chat.chat_id},'
                           f'"conversation_message_ids":[{self.conversation_message_id}],'
                           f'"is_reply":1}}')

        return await self.chat.send(text=text, forward_message=forward_message, attachment=attachment)


class Chat:
    def __init__(self, chat_id, vk_session: VkSession):
        self.vk_session = vk_session
        url = 'https://api.vk.com/method/messages.getConversationsById'
        params = {'peer_ids': chat_id,
                  'access_token': vk_session.access_token,
                  'v': 5.126}
        result = get(url, params).json()

        result = result['response']['items'][0]
        self.chat_id = chat_id
        if result['peer']['type'] == 'chat':
            self.title = result['chat_settings']['title']
            self.admins = [User(admin_id, vk_session) for admin_id in result['chat_settings']['admin_ids'] if
                           admin_id > 0]
            self.member_count = result['chat_settings']['members_count']
        else:
            self.title = 'ЛС'

    async def send(self, text, attachment=None, forward_message: str = None):
        method = 'messages.send'
        params = {
            f'peer_id': self.chat_id,
            f'message': text,
            f'random_id': random.randint(1, 2147123123),
        }
        if attachment is not None:
            params['attachment'] = attachment
        if forward_message is not None:
            params['forward'] = forward_message
        return await self.vk_session.method(method=method, params=params)


class User:
    def __init__(self, user_id, vk_session: VkSession):
        url = f'https://api.vk.com/method/users.get'
        params = {
            'user_ids': {user_id},
            f'access_token': {vk_session.access_token},
            f'v': 5.126
        }
        result = get(url, params=params).json()['response'][0]
        self.id = user_id
        self.first_name = result['first_name']
        self.last_name = result['last_name']
