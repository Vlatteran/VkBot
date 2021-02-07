import VkBot


class MyBot(VkBot.VkBot):
    def on_new_message(self, context):
        super().on_new_message(context)
        if context.text[0] == '!':
            command = context.text[
                      1:len(context.text) if context.text.find(' ') == -1 else context.text.find(' ')]
            if command in ('пары', 'расписание'):
                context.reply(self.schedule.show(context.text.replace(f'!{command}', '').strip()), self)
            elif command == 'stop':
                if context.sender.id == self.bot_admin:
                    context.reply('Bot has been stopped', self)
                    self.is_running = False
                else:
                    context.reply("You don't have permissions to stop bot", self)


if __name__ == '__main__':
    from config import token, group_id as group, bot_admin as admin

    bot = MyBot(access_token=token, group_id=group, bot_admin=admin)
    bot.run()
