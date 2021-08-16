#!/usr/bin/python3

BOT_TOKEN = "(TELEGRAM BOT TOKEN HERE)"

API_URL = "(SHAREX FLASK ENDPOINT HERE)" # eg https://localhost/share
API_KEY = "(SHAREX FLASK API KEY HERE)"

USER_WHITELIST = (123456789,) # AUTHORISED USER IDS HERE

API_FORM = {'k': API_KEY}


from datetime import datetime
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, CallbackContext, Filters
from telegram.utils.helpers import escape_markdown
import random
import string
import os
import requests
import io

if not os.path.isdir("./temp"): os.mkdir("./temp")


def authorised(update):
    if update.effective_user.id in USER_WHITELIST: 
        return True
    else:
        update.message.reply_text("Unauthorised")
        return False


def upload(update: Update, context: CallbackContext) -> None:
    if not authorised(update): return
    msg = update.message
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    ext = ""
    if msg.photo: 
        file = msg.photo[-1]
        ext = "jpg"
    if msg.audio: 
        file = msg.audio
    if msg.video: 
        file = msg.video
    if msg.voice: 
        file = msg.voice
    if msg.document: 
        file = msg.document
    if msg.video_note:
        file = msg.video_note
        ext = "mp4"

    if hasattr(file, "file_name"):
        filename = file.file_name
    else:
        if not ext: ext = file.mime_type.split("/")[-1]
        filename = f"telegram_{timestamp}.{ext}"

    file = context.bot.getFile(file.file_id)
    
    reply = update.message.reply_text("Uploading...")
    
    temp = io.BytesIO()
    files = {'f': (filename, temp)}
    file.download(out=temp)
    temp.seek(0)
    
    try:
        req = requests.post(API_URL, files=files, data=API_FORM, verify=False)
        reply.edit_text(req.text)
    except:
        reply.edit_text("API/Connection error")
        
    temp.close()


def unsupported(update: Update, context: CallbackContext) -> None:
    if not authorised(update): return
    update.message.reply_text("Unsupported type (upload a photo or something)")


supported_uploads = Filters.document | Filters.photo | Filters.video | Filters.audio | Filters.voice | Filters.video_note


def main() -> None:
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher


    updater.dispatcher.add_handler(MessageHandler(supported_uploads, upload))
    updater.dispatcher.add_handler(MessageHandler(~supported_uploads, unsupported))
    
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
