import asyncio

from AsyncBot.VK.Group import VkBot
from schedule import Schedule


class MyBot(VkBot.VkBot):

    def __init__(self, access_token: str, group_id, bot_admin, logger=None, log_file='', log_to_file=False,
                 log_to_console=True):
        super().__init__(access_token, group_id, bot_admin, logger, log_file, log_to_file, log_to_console)
        self.schedule = Schedule()

    async def on_message_new(self, message, client_info):
        await super().on_message_new(message, client_info)
        if len(message.text) > 0 and message.text[0] == '!':
            command = message.text[
                      1:len(message.text) if message.text.find(' ') == -1 else message.text.find(' ')]
            print(command)
            if command in ('пары', 'расписание'):
                await message.reply(self.schedule.show(message.text.replace(f'!{command}', '').strip()))
            elif command == "уведомления":
                await message.reply('Уведомления включены')
                async for text in self.schedule.time_to_next_lecture():
                    await message.chat.send(text)
            elif command == 'stop':
                if message.sender.id == self.bot_admin:
                    await asyncio.sleep(10)
                    await message.reply('Bot has been stopped')
                else:
                    await message.reply("You don't have permissions to stop bot")


def main():
    from config import token, group_id as group, bot_admin as admin
    bot = MyBot(access_token=token, group_id=group, bot_admin=admin)
    bot.start()


if __name__ == '__main__':
    main()
