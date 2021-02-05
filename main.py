from VkBot import VkBot
import os


bot = VkBot(access_token=os.environ['token'], group_id=os.environ['group'])
bot.run()
