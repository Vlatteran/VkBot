from AsyncBot.VK.Group.Bot import Bot
from config import token, group_id as group, bot_admin as admin
from schedule import Schedule


def main():
    bot = Bot(access_token=token, group_id=group, bot_admin=admin)

    @bot.command('пары')
    async def lectures(args, message):
        result = ''
        for text in Schedule().show(args):
            result += text + '\n\n'
        await message.reply(result)

    @bot.command('уведомления')
    async def notifications(args, message):
        await message.reply('Уведомления включены')
        async for text in Schedule().time_to_next_lecture():
            await message.chat.send(text)

    bot.start()


if __name__ == '__main__':
    main()
