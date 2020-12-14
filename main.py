from os.path import basename
import requests
import time
from src import MSG
from src.auxiliary import AUX
from pydrive.auth import GoogleAuth
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from telegram import ParseMode, ChatAction, InlineKeyboardButton
import logging

# Creating Log
logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
#create objects
au = AUX()

# init bot
updater = Updater(token=AUX.TOKEN, use_context=True)
dp = updater.dispatcher

# define updates


def start(update, context):  # start command
	# sends typing action before sending message
	context.bot.send_chat_action(
		chat_id=update.effective_chat.id, action=ChatAction.TYPING)
	# send welcome messsage
	context.bot.send_message(chat_id=update.effective_chat.id, text=MSG.START.format(
		update.message.from_user.first_name), parse_mode=ParseMode.HTML)


def download(update, context):
	url = (update.message.text).strip()
	filename = basename(url)
	context.bot.send_chat_action(
		chat_id=update.effective_chat.id, action=ChatAction.TYPING)
	sent_message = context.bot.send_message(
		chat_id=update.effective_chat.id, text=MSG.PROCESSING, parse_mode=ParseMode.HTML)
	if filename is not None and "." in filename:
		try:
			print('ddd')
			response = requests.get(url, stream=True)
			print("hhhh")
			length = int(response.headers["content-length"])
			start = time.time()
			with open(filename, 'wb') as f:
				downloaded = 0
				progressBar = f"[0KB][{downloaded}%][{20*'_'}]"
				sent_message.edit_text(MSG.DOWNLOADING.format(filename, au.size(length),'0 KB', progressBar), parse_mode=ParseMode.HTML)
				for data in response.iter_content(1024*1024):
					downloaded += len(data)
					f.write(data)
					done = int(20*downloaded/length)
					progressBar = '[{} of {}] [{}%]\n[{}{}]'.format(au.size(downloaded), au.size(length), round(100*downloaded/length, 1), '█'*done, '_'*(20-done))
					# print(filename, au.size(length), progressBar)
					sent_message.edit_text(MSG.DOWNLOADING.format(filename, au.size(length),au.size(downloaded/(time.time()-start)), progressBar), parse_mode = ParseMode.HTML)
				f.close()
			
			# sent_message.edit_text(MSG.DOWNLOADED, parse_mode=ParseMode.HTML)
			sent_message = context.bot.send_message(chat_id=update.effective_chat.id, text=MSG.DOWNLOADED, parse_mode=ParseMode.HTML)
		except Exception as e:
			print(e)
			sent_message.edit_text(MSG.DOWN_ERR)
	else:
		sent_message.edit_text(MSG.URL_ERR)

	# # authorize gdrive
	# gauth = GoogleAuth()
	# au.gdAuth(gauth, 'credentials.json')


# define handlers
start_handler = CommandHandler('start', start)
dp.add_handler(start_handler)
downloader_handler = MessageHandler(Filters.regex(r'http'), download)
dp.add_handler(downloader_handler)
# fire-up the bot
updater.start_polling()
updater.idle()
