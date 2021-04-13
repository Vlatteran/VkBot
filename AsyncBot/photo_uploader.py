import aiohttp
import json

import AsyncBot.VK.Message
from AsyncBot.VK.Group import VkBot


class TestBot(VkBot.VkBot):
    async def on_message_new(self, message: AsyncBot.VK.Message.Message):
        await super().on_message_new(message)
        if len(message.text) > 0 and message.text[0] == '!':
            command = message.text[
                      1:len(message.text) if message.text.find(' ') == -1 else message.text.find(' ')]
            print(command)
            if command == 'testphoto':
                print(await message.reply('', attachments=[await self.upload('img.png')]))

    async def upload(self, photo):
        get_serv = f'photos.getMessagesUploadServer'
        save_photo = 'photos.saveMessagesPhoto'
        params = {
            'peer_id': 0
        }
        file = {'photo': open(photo, 'rb')}
        upload_url = (await self.vk_session.method(method=get_serv, params=params))['response']['upload_url']
        async with aiohttp.ClientSession() as session:
            resp = await session.post(url=upload_url, data=file)
            photo: dict = json.loads(await resp.text())
        response = (await self.vk_session.method(method=save_photo, params=photo))['response'][0]
        return f'photo{response["owner_id"]}_{response["id"]}'


def main():
    from testconf import token, group_id as group, bot_admin as admin
    bot = TestBot(access_token=token, group_id=group, bot_admin=admin)
    bot.start()


if __name__ == '__main__':
    main()
