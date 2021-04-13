import random

from requests import get

from AsyncBot.VK.Session import Session
from AsyncBot.VK.User import User


class Chat:
    def __init__(self, chat_id, vk_session: Session):
        self.vk_session = vk_session
        method = 'messages.getConversationsById'
        params = {'peer_ids': chat_id}
        result = get(url=f'{vk_session.base_url}{method}',
                     params=params | vk_session.session_params).json()
        result = result['response']['items'][0]
        self.chat_id = chat_id
        if result['peer']['type'] == 'chat':
            self.title = result['chat_settings']['title']
            self.admins = [User(admin_id, vk_session) for admin_id in result['chat_settings']['admin_ids'] if
                           admin_id > 0]
            self.member_count = result['chat_settings']['members_count']
        else:
            self.title = 'ЛС'

    async def send(self, text: str = '', attachments: list = None, forward_message: str = None):
        if text == '' and attachments is None:
            raise ValueError("Can't send empty message")
        method = 'messages.send'
        params = {
            f'peer_id': self.chat_id,
            f'message': text,
            f'random_id': random.randint(1, 2147123123),
        }
        if attachments is not None:
            params['attachment'] = attachments
        if forward_message is not None:
            params['forward'] = forward_message
        return await self.vk_session.method(method=method, params=params)
