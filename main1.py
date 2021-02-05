from VkBot import VkBot
from boto.s3.connection import S3Connection
import os


bot = VkBot(access_token=S3Connection(os.environ['token']), group_id=S3Connection(os.environ['group']))
bot.run()