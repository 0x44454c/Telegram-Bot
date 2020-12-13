from src import MSG
from src.auxiliary import AUX
from pydrive.auth import GoogleAuth
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode, ChatAction, InlineKeyboardButton
import logging

# Creating Log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

# init bot
updater = Updater(token=AUX.TOKEN, use_context=True)
dp = updater.dispatcher

# define updates
def start(update, context):  # start command
	# sends typing action before sending message
	context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
	# send welcome messsage
	context.bot.send_message(chat_id=update.effective_chat.id, text=MSG.START.format(
	update.message.from_user.first_name), parse_mode=ParseMode.HTML)

def download(update, context):
	# authorize gdrive
	AUX().gdAuth(GoogleAuth())


# define handlers
start_handler = CommandHandler('start', start)
dp.add_handler(start_handler)

# fire-up the bot
updater.start_polling()
updater.idle()