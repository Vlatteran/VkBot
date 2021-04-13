import json
import time

from AsyncBot.VK.Chat import Chat
from AsyncBot.VK.Session import Session
from AsyncBot.VK.User import User


class Message:
    text: str

    def __init__(self, message_dict, vk_session: Session):
        self.vk_session = vk_session
        self.date = time.localtime(message_dict['date'])
        self.text = message_dict['text']
        self.sender = User(message_dict['from_id'], vk_session)
        self.chat = Chat(message_dict['peer_id'], vk_session)
        self.conversation_message_id = message_dict['conversation_message_id']

    async def reply(self, text: str = '', attachments: list = None):
        forward_message = json.dumps(
            {'peer_id': self.chat.chat_id,
             'conversation_message_ids': [self.conversation_message_id],
             'is_reply': 1})

        return await self.chat.send(text=text,
                                    forward_message=forward_message,
                                    attachments=attachments)
