# import requests
from os import path
from os.path import basename
import time
from src import MSG
from src.auxiliary import AUX
from pydrive.auth import GoogleAuth
from pySmartDL import SmartDL, utils
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from telegram import ParseMode, ChatAction, InlineKeyboardButton
import logging


# Creating Log
logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# create objects
au = AUX()

# define updates


def start(update, context):  # start command
	# sends typing action before sending message
	context.bot.send_chat_action(
		chat_id=update.effective_chat.id, action=ChatAction.TYPING)
	# send welcome messsage
	context.bot.send_message(chat_id=update.effective_chat.id, text=MSG.START.format(
		update.message.from_user.first_name), parse_mode=ParseMode.HTML)


def download(update, context):
	# url from user
	url = (update.message.text).strip()
	# destination of downloading locally
	ID = update.message.from_user.id
	dest = path.join(au.CWP, 'Downloads', str(ID), '')

	# retrieve filename and size from url
	filename = basename(url)
	size = utils.sizeof_human(utils.get_filesize(url))

	# send processing status to the user
	context.bot.send_chat_action(
		chat_id=update.effective_chat.id, action=ChatAction.TYPING)
	sent_message = context.bot.send_message(
		chat_id=update.effective_chat.id, text=MSG.PROCESSING, parse_mode=ParseMode.HTML)

	# initiate downloading if url has a correct filename at last and if it doesn't redirects
	if filename is not None and "." in filename:
		try:
			DL = SmartDL(url, dest, progress_bar=False)
			DL.start(blocking=False)

			while not DL.isFinished(): # sends the user downloading status
				sent_message.edit_text(MSG.DOWNLOADING.format(DL.get_status().upper(), filename, size, DL.get_speed(human=True), utils.time_human(DL.get_eta(), fmt_short=True), DL.get_dl_size(human=True), size, round(DL.get_progress()*100, 2), DL.get_progress_bar()), parse_mode=ParseMode.HTML)
				time.sleep(1)

			if DL.isSuccessful(): # sends succesful status to the user
				sent_message.edit_text(MSG.DOWNLOADED.format(DL.get_status().upper(), filename, size, DL.get_speed(human=True), DL.get_dl_time(human=True)), parse_mode=ParseMode.HTML)

			"""
			### Download using requests library, comparatively slow and less featured
			response = requests.get(url, stream=True)
			length = int(response.headers["content-length"])

			# Start counter time
			start = time.time()
			with open(filename, 'wb') as f: # open file and start downloading
				downloaded = 0
				progressBar = f"[0KB][{downloaded}%]\n[{20*'_'}]"
				sent_message.edit_text(MSG.DOWNLOADING.format(filename, au.size(length),'0 KB', progressBar), parse_mode=ParseMode.HTML)
				for data in response.iter_content(1024*1024): # start reading chunk and writing in file
					downloaded += len(data)
					f.write(data)
					done = int(20*downloaded/length)
					progressBar = '[{} of {}] [{}%]\n[{}{}]'.format(au.size(downloaded), au.size(length), round(100*downloaded/length, 1), '█'*done, '_'*(20-done))
					# update message for downloading status
					sent_message.edit_text(MSG.DOWNLOADING.format(filename, au.size(length),au.size(downloaded/(time.time()-start)), progressBar), parse_mode = ParseMode.HTML)
				f.close()
			sent_message = context.bot.send_message(chat_id=update.effective_chat.id, text=MSG.DOWNLOADED, parse_mode=ParseMode.HTML)"""

		except Exception as e: # send error msg with error
			sent_message.edit_text(MSG.DOWN_ERR.format(e))
	else: # send incorrect url msg
		sent_message.edit_text(MSG.URL_ERR)

	# # authorize gdrive
	gauth = GoogleAuth()
	au.gdAuth(gauth, 'credentials.json')


# init bot
updater = Updater(token=AUX.TOKEN, workers=8, use_context=True)
dp = updater.dispatcher

# define handlers
start_handler = CommandHandler('start', start, run_async=True)
dp.add_handler(start_handler)
downloader_handler = MessageHandler(
	Filters.regex(r'http'), download, run_async=True)
dp.add_handler(downloader_handler)

# fire-up the bot
updater.start_polling()
updater.idle()
