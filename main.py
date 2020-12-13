from src import MSG
from src.config import CON
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
import logging

# Creating Log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

# init bot
updater = Updater(token=CON.TOKEN, use_context=True)
dp = updater.dispatcher

# define updates
def start(update, context): # start command
    context.bot.send_message(chat_id=update.effective_chat.id, text=MSG.START.format(update.message.from_user.first_name), parse_mode=ParseMode.HTML)


# define handlers
start_handler = CommandHandler('start', start)
dp.add_handler(start_handler)

# fire-up the bot
updater.start_polling()
updater.idle()