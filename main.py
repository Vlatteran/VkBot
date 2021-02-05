from VkBot import VkBot
import os


print('some shit')
bot = VkBot(access_token=os.environ['token'], group_id=os.environ['group'])
bot.run()
