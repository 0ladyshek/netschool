import logging
import os
from vkbottle import Bot
from pluginsvk import bps

bot = Bot("")
logging.basicConfig(level=logging.INFO)

for bp in bps:
    bp.load(bot)
    
bot.run_forever()