import logging
from typing import *

import aiohttp

from AsyncBot.VK.Group.Event import Event
from AsyncBot.VK.Message import Message
from AsyncBot.VK.Session import Session


class LongPollServer:

    def __init__(self, vk_session: Session):
        self.vk_session: Session = vk_session
        self.get_long_poll_server()
        self.server: str = ''
        self.key: str = ''
        self.ts: int = 0

    def get_long_poll_server(self):
        try:
            long_poll_serv = self.vk_session.method_sync('groups.getLongPollServer')['response']
            self.server = long_poll_serv['server']
            self.key = long_poll_serv['key']
            self.ts = long_poll_serv['ts']
        except KeyError:
            logging.exception("Can't get a LongPollServer")

    async def check(self) -> AsyncIterable[tuple[Callable, Dict]]:
        """
        Checks for new events on long_poll_server, updates long_poll_server information if failed to get events

        Yields:
            tuple
                event and context dictionary
        """
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
            except Exception:
                logging.exception(f'try {(retries := retries + 1)}')

        if 'failed' in result:
            error_code = result['failed']
            if error_code == 1:
                logging.info('Updating ts')
                self.ts = result['ts']
            elif error_code in (2, 3):
                logging.info('Updating long_poll_server')
                self.get_long_poll_server()
            else:
                logging.error(f'Unexpected error_code code: {error_code} in {result}')

        else:
            self.ts = result['ts']
            events = result['updates']
            for event in events:
                if event['type'] == 'message_new':
                    yield Event[event['type'].upper()], {'message': Message(event['object']['message'],
                                                                            self.vk_session),
                                                         'client_info': event['object']['client_info']}
                elif event['type'] in ('message_reply', 'message_edit'):
                    yield Event[event['type'].upper()], {'message': Message(event['object']['message'],
                                                                            self.vk_session)}

    async def listen(self) -> AsyncIterable[tuple[Callable, Dict]]:
        """
        Yields:
            tuple
                event and context dictionary
        """
        while True:
            async for event in self.check():
                yield event
