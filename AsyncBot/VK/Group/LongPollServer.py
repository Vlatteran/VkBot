import asyncio

import aiohttp

from AsyncBot import Logger
from AsyncBot.VK.Message import Message
from AsyncBot.VK.Session import Session


class LongPollServer:
    server: str
    key: str
    ts: str

    def __init__(self, vk_session: Session, logger: Logger):
        self.vk_session = vk_session
        self.logger: Logger = logger
        self.get_long_poll_server()

    def get_long_poll_server(self):
        try:
            method = 'groups.getLongPollServer'

            long_poll_serv = asyncio.run(self.vk_session.method(method=method, params={}))

            long_poll_serv = long_poll_serv['response']
            self.server = long_poll_serv['server']
            self.key = long_poll_serv['key']
            self.ts = long_poll_serv['ts']
        except KeyError:
            asyncio.run(
                self.logger.log(
                    "Can't get a LongPollServer",
                    method_name='LongPollServer.get_long_poll_server()')
            )

    async def check(self) -> (str, dict):
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
                asyncio.run(
                    self.logger.log(f'try{retries + 1}: failed with:\n{e}',
                                    method_name='LongPollServer.check()')
                )

                retries += 1
                if retries == 5:
                    asyncio.run(
                        self.logger.log('to many tries', method_name='LongPollServer.check()')
                    )

        if 'failed' in result:
            asyncio.run(
                self.logger.log(f'failed with:{result}', method_name='LongPollServer.check()')
            )
            error = result['failed']
            if error == 1:
                self.ts = result['ts']
            elif error in (2, 3):
                self.get_long_poll_server()
            else:
                await self.logger.log(f'Unexpected error code: {error}\n{result}',
                                      method_name='LongPollServer.check()')

        else:
            self.ts = result['ts']
            events = result['updates']
            print(events)
            for event in events:
                if event['type'] == 'message_new':
                    yield event['type'], {'message': Message(event['object']['message'], self.vk_session)}
                elif event['type'] in ('message_reply', 'message_edit'):
                    yield event['type'], {'message': Message(event['object']['message'], self.vk_session)}
                elif event['type'] == 'message_typing_state':
                    pass

    async def listen(self) -> (str, dict):
        while True:
            result = self.check()
            if result is not None:
                async for event in result:
                    yield event
