from requests import get
from Main.config import token, group_id
import random
from Main.schedule import Schedule

schedule = Schedule()

longPollServer = get(f'https://api.vk.com/method/groups.getLongPollServer?'
                     f'group_id={group_id}'
                     f'&v=5.126'
                     f'&access_token={token}').json()['response']


def reply(peer_id, text, conversation_message_id, group_id, access_token):
    response = get(f'https://api.vk.com/method/messages.send?'
                   f'peer_id={peer_id}&'
                   f'message={text}&'
                   f'forward={{"peer_id":{peer_id},'
                   f'"conversation_message_ids":[{conversation_message_id}],'
                   f'"is_reply":1}}&'
                   f'group_id={group_id}&'
                   f'access_token={access_token}&'
                   f'random_id={random.randint(1, 2147123123)}&'
                   f'v=5.126')
    return response.json()


while True:
    event = get(
        f"{longPollServer['server']}?"
        f"act=a_check&"
        f"key={longPollServer['key']}&"
        f"ts={longPollServer['ts']}&"
        f"wait=25").json()
    if 'updates' in event:
        if len(event['updates']) > 0:
            print(event)
            message = event['updates'][0]['object']['message']
            command = message['text'].split(' ')[0]
            context = ' '.join(message['text'].split(' ')[1:]) if len(message['text'].split(' ')) > 0 else ''
            print(command)
            if command in ('!пары', '!расписание'):
                reply(message['peer_id'], schedule.show(context), message['conversation_message_id'], group_id, token)
    longPollServer['ts'] = event['ts']
