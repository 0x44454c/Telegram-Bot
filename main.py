# import requests
import os
import shutil
import time
from src import MSG
from src.auxiliary import AUX
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pySmartDL import SmartDL, utils
from telegram.ext import (Updater, CommandHandler, Filters, MessageHandler, CallbackQueryHandler)
from telegram import (ParseMode, ChatAction, InlineKeyboardButton)
import logging


# Creating Log
logging.basicConfig(filename="bot.log", filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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


def download(update, context)->None:
	# url from user
	url = (update.message.text).strip()
	# destination of downloading locally
	ID = update.message.from_user.id
	dest = os.path.join(au.CWP, 'Downloads', str(ID), '')

	# retrieve filename and size from url
	filename = os.path.basename(url)
	size = utils.sizeof_human(utils.get_filesize(url))

	# send processing status to the user
	context.bot.send_chat_action(
		chat_id=update.effective_chat.id, action=ChatAction.TYPING)
	sent_message = update.message.reply_text(text=MSG.PROCESSING, parse_mode=ParseMode.HTML)

	# initiate downloading if url has a correct filename at last and if it doesn't redirects
	if filename is not None and "." in filename:
		try:
			DL = SmartDL(url, dest, progress_bar=False)
			DL.start(blocking=False)
			while not DL.isFinished(): # sends the user downloading status
				if DL.get_status() == 'downloading':
					sent_message.edit_text(MSG.DOWNLOADING.format(DL.get_status().upper(), filename, size, DL.get_speed(human=True), utils.time_human(DL.get_eta(), fmt_short=True), DL.get_dl_size(human=True), size, round(DL.get_progress()*100, 2), DL.get_progress_bar()), parse_mode=ParseMode.HTML)
					time.sleep(1)

			if DL.isSuccessful(): # sends succesful status to the user
				sent_message.edit_text(MSG.DOWNLOADED.format(DL.get_status().upper(), filename, size, DL.get_speed(human=True), DL.get_dl_time(human=True)), parse_mode=ParseMode.HTML)

				# # upon successful download authenticate gdrive and try uploading
				# authorize gdrive
				context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
				sent_message1 = context.bot.send_message(chat_id=update.effective_chat.id, text=MSG.TRY_UPLOAD, parse_mode=ParseMode.HTML)
				gauth = GoogleAuth()
				au.gdAuth(gauth, 'credentials.json')
				drive = GoogleDrive(gauth)
				http = drive.auth.Get_Http_Object()
				# check whether the file exists
				if os.path.isfile(dest+filename):
					file_to_upload = drive.CreateFile({
										'title': filename,
										'parents': [{
											'kind': 'drive#fileLink',
											'teamDriveId': AUX.SHARED_DRIVE_ID,
											'id' : AUX.SHARED_DRIVE_FOLDER_ID
										}]
									})
					file_to_upload.SetContentFile(dest+filename)
					try:
						sent_message1.edit_text(MSG.UPLOADING, parse_mode=ParseMode.HTML)
						# uploads file
						file_to_upload.Upload(param={'supportsTeamDrives': True, 'http': http})
						sent_message1.edit_text(MSG.UPLOADED.format(file_to_upload['webContentLink']), parse_mode=ParseMode.HTML)
						# delete file after uploading
						try:
							os.remove(dest+filename)
						except:
							logging.error("Can't remove file!", exc_info=True)
							try:
								shutil.rmtree(dest+filename)
							except:
								logging.critical("Impossible to remove the file!")
								
					except: # sends error msg
						logging.error("Uploading Exception occured", exc_info=True)
						sent_message1.edit_text(MSG.UPLOAD_ERR, parse_mode=ParseMode.HTML)
				else: # sends file non existing msg
					logging.error("File doesn't exists!")
					sent_message1.edit_text(MSG.FILE_NOT_EXISTS, parse_mode=ParseMode.HTML)

				######
			else: # sends unsuccessful msg
				logging.warning("Downloading was unsuccessful!")
				sent_message.edit_text(MSG.DOWNLOAD_UNSUCCESSFUL, parse_mode=ParseMode.HTML)
				try:
					os.remove(dest+filename)
				except:
					logging.error("Can't remove file!", exc_info=True)
					try:
						shutil.rmtree(dest+filename)
					except:
						logging.critical("Impossible to remove the file!")

		except: # send error msg
			logging.error("Downloading Exception occured", exc_info=True)
			sent_message.edit_text(MSG.DOWN_ERR)
			try:
				os.remove(dest+filename)
			except:
				logging.error("Can't remove file!", exc_info=True)
				try:
					shutil.rmtree(dest+filename)
				except:
					logging.critical("Impossible to remove the file!")

	else: # send correct url msg
		logging.warning("User sending incorrect url.")
		sent_message.edit_text(MSG.URL_ERR)


def main():
	# init bot
	updater = Updater(token=AUX.TOKEN, workers=32, use_context=True)
	dp = updater.dispatcher

	# define handlers
	start_handler = CommandHandler('start', start, run_async=True)
	dp.add_handler(start_handler)
	downloader_handler = MessageHandler(Filters.regex(r'http'), download, run_async=True)
	dp.add_handler(downloader_handler)

	# fire-up the bot
	updater.start_polling()
	updater.idle()


if __name__ == "__main__":
	main()