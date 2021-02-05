from requests import get
import random
from schedule import Schedule

from config import token, group_id as group


class VkBot:

    def __init__(self, access_token, group_id):
        self.access_token = access_token
        self.group_id = group_id
        self.server = LongPollServer(access_token, group_id)
        self.schedule = Schedule()

    def run(self):
        for event, context in self.server.listen():
            if event == 'message_new':
                if context.text[0] == '!':
                    command = context.text[
                              1:len(context.text) if context.text.find(' ') == -1 else context.text.find(' ')]
                    if command in ('пары', 'расписание'):
                        context.reply(self.schedule.show(context.text.replace(f'!{command}', '').strip()), self)


class LongPollServer:
    server: str
    key: str
    ts: str

    def __init__(self, access_token, group_id):
        self.access_token = access_token
        self.group_id = group_id
        self.get_long_poll_server()

    def get_long_poll_server(self):
        long_poll_serv = \
            get(f'https://api.vk.com/method/groups.getLongPollServer?'
                f'group_id={self.group_id}'
                f'&v=5.126'
                f'&access_token={self.access_token}').json()['response']
        self.server = long_poll_serv['server']
        self.key = long_poll_serv['key']
        self.ts = long_poll_serv['ts']

    def check(self):
        result = get(f"{self.server}?"
                     f"act=a_check&"
                     f"key={self.key}&"
                     f"ts={self.ts}&"
                     f"wait=25").json()
        if 'failed' in result:
            error = result['failed']
            if error == 1:
                self.ts = result['ts']
            elif error in (2, 3):
                self.get_long_poll_server()
            else:
                print(f'[VkBot.LongPollServer.check()] unexpected error code: {error}\n{result}')
        else:
            self.ts = result['ts']
            events = result['updates']
            for event in events:
                if event['type'] == 'message_new':
                    return 'message_new', Message(event['object']['message'])

    def listen(self):
        while True:
            result = self.check()
            print(result)
            if result is None:
                continue
            yield result


class Message:
    text: str

    def __init__(self, message_dict):
        self.date = message_dict['date']
        self.text = message_dict['text']
        self.from_id = message_dict['from_id']
        self.peer_id = message_dict['peer_id']
        self.conversation_message_id = message_dict['conversation_message_id']

    def reply(self, text, vk: VkBot):
        return get(f'https://api.vk.com/method/messages.send?'
                   f'peer_id={self.peer_id}&'
                   f'message={text}&'
                   f'forward={{"peer_id":{self.peer_id},'
                   f'"conversation_message_ids":[{self.conversation_message_id}],'
                   f'"is_reply":1}}&'
                   f'group_id={vk.group_id}&'
                   f'access_token={vk.access_token}&'
                   f'random_id={random.randint(1, 2147123123)}&'
                   f'v=5.126').json()


class Chat:
    def __init__(self):
        pass

    def send(self):
        pass


if __name__ == '__main__':
    bot = VkBot(access_token=token, group_id=group)
    print(bot.server.listen)
    bot.run()
