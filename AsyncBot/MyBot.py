import asyncio

import VkBot


class MyBot(VkBot.VkBot):
    async def on_new_message(self, context: VkBot.Message):
        await super().on_new_message(context)
        if len(context.text) > 0 and context.text[0] == '!':
            command = context.text[
                      1:len(context.text) if context.text.find(' ') == -1 else context.text.find(' ')]
            print(command)
            if command in ('пары', 'расписание'):
                self.tasks.append(
                    asyncio.create_task(
                        context.reply(self.schedule.show(context.text.replace(f'!{command}', '').strip()))
                    )
                )
            elif command == "уведомления":
                self.tasks.append(
                    asyncio.create_task(
                        context.reply('Уведомления включны')
                    )
                )
                async for text in self.schedule.time_to_next_lecture():
                    self.tasks.append(
                        asyncio.create_task(
                            context.chat.send(text, self)
                        )
                    )
            elif command == 'stop':
                if context.sender.id == self.bot_admin:
                    await asyncio.sleep(10)
                    self.is_running = False
                    self.tasks.append(
                        asyncio.create_task(
                            context.reply('Bot has been stopped')
                        )
                    )
                else:
                    self.tasks.append(
                        asyncio.create_task(
                            context.reply("You don't have permissions to stop bot")
                        )
                    )


def main():
    from config import token, group_id as group, bot_admin as admin
    bot = MyBot(access_token=token, group_id=group, bot_admin=admin)
    bot.start()


if __name__ == '__main__':
    main()
