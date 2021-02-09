from requests import get
import random
from schedule import Schedule
import time
import Logger


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

    def run(self):
        self.is_running = True
        try:
            for event, context in self.server.listen():
                if event == 'message_new':
                    self.on_new_message(context)

                if not self.is_running:
                    break
        except Exception as e:
            self.logger.log(f'Crushed with:\n{e}', method_name='VkBot.run()')

    def on_new_message(self, context):
        self.logger.log(
            text=f'Message from {context.sender.first_name} {context.sender.last_name} ({context.sender.id}) '
                 f'at {time.strftime("%x %X", context.date)}:\n{context.text}\n',
            method_name='VkBot.run()')


class LongPollServer:
    server: str
    key: str
    ts: str

    def __init__(self, access_token, group_id, vk):
        self.vk = vk
        self.access_token = access_token
        self.group_id = group_id
        self.get_long_poll_server()

    def get_long_poll_server(self):
        try:
            long_poll_serv = \
                get(f'https://api.vk.com/method/groups.getLongPollServer?'
                    f'group_id={self.group_id}'
                    f'&v=5.126'
                    f'&access_token={self.access_token}').json()
            long_poll_serv = long_poll_serv['response']
            self.server = long_poll_serv['server']
            self.key = long_poll_serv['key']
            self.ts = long_poll_serv['ts']
        except KeyError:
            self.vk.logger.log(long_poll_serv, method_name='LongPollServer.get_long_poll_server()')

    def check(self):
        result = None
        retries = 0
        while result is None:
            try:
                result = get(f"{self.server}?"
                             f"act=a_check&"
                             f"key={self.key}&"
                             f"ts={self.ts}&"
                             f"wait=25").json()
            except Exception as e:
                self.vk.logger.log(f'try{retries + 1}: failed with:\n{e}', method_name='LongPollServer.check()')
                retries += 1
                if retries == 5:
                    self.vk.logger.log('to many tries', method_name='LongPollServer.check()')
        if 'failed' in result:
            self.vk.logger.log(f'failed with:{result}', method_name='LongPollServer.check()')
            error = result['failed']
            if error == 1:
                self.ts = result['ts']
            elif error in (2, 3):
                self.get_long_poll_server()
            else:
                self.vk.logger.log(f'Unexpected error code: {error}\n{result}', method_name='LongPollServer.check()')
        else:
            # if len(result['updates']) > 0:
            #     self.vk.logger.log(f'new event: {result}', method_name='LongPollServer.check()')
            self.ts = result['ts']
            events = result['updates']
            for event in events:
                if event['type'] == 'message_new':
                    yield 'message_new', Message(event['object']['message'], self.vk)

    def listen(self):
        while True:
            result = self.check()
            if result is not None:
                for event in result:
                    yield event


class Message:
    text: str

    def __init__(self, message_dict, vk):
        self.date = time.localtime(message_dict['date'])
        self.text = message_dict['text']
        self.sender = User(message_dict['from_id'], vk)
        self.chat = Chat(message_dict['peer_id'], vk)
        self.conversation_message_id = message_dict['conversation_message_id']

    def reply(self, text, vk: VkBot):
        return get(f'https://api.vk.com/method/messages.send?'
                   f'peer_id={self.chat.chat_id}&'
                   f'message={text}&'
                   f'forward={{"peer_id":{self.chat.chat_id},'
                   f'"conversation_message_ids":[{self.conversation_message_id}],'
                   f'"is_reply":1}}&'
                   f'group_id={vk.group_id}&'
                   f'access_token={vk.access_token}&'
                   f'random_id={random.randint(1, 2147123123)}&'
                   f'v=5.126').json()


class Chat:
    def __init__(self, chat_id, vk: VkBot):
        result = get(f'https://api.vk.com/method/messages.getConversationsById?'
                     f'peer_ids={chat_id}&'
                     f'access_token={vk.access_token}&'
                     f'v=5.126').json()
        result = result['response']['items'][0]
        self.chat_id = chat_id
        self.title = result['chat_settings']['title']
        self.admins = [User(admin_id, vk) for admin_id in result['chat_settings']['admin_ids'] if admin_id > 0]
        self.member_count = result['chat_settings']['members_count']

    def send(self, text, vk):
        return get(f'https://api.vk.com/method/messages.send?'
                   f'peer_id={self.chat_id + 2000000000}&'
                   f'message={text}&'
                   f'group_id={vk.group_id}&'
                   f'access_token={vk.access_token}&'
                   f'random_id={random.randint(1, 2147123123)}&'
                   f'v=5.126').json()


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
