import json
import time

from AsyncBot.VK.Chat import Chat
from AsyncBot.VK.Session import Session
from AsyncBot.VK.User import User


class Message:
    """
    Representing existing message from VK_API
    """

    def __init__(self, message_dict, vk_session: Session):
        self.vk_session = vk_session
        self.date: time.struct_time = time.localtime(message_dict['date'])
        self.text: str = message_dict['text']
        self.sender: User = User(message_dict['from_id'], vk_session)
        self.chat: Chat = Chat(message_dict['peer_id'], vk_session)
        self.conversation_message_id: int = message_dict['conversation_message_id']

    async def reply(self, text: str = '', attachments: list = None):
        """
        Replying to this message
        :param text:
        :param attachments:
        :return:
        """
        forward_message = json.dumps(
            {'peer_id': self.chat.chat_id,
             'conversation_message_ids': [self.conversation_message_id],
             'is_reply': 1})

        return await self.chat.send(text=text,
                                    forward_message=forward_message,
                                    attachments=attachments)
