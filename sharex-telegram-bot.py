#!/usr/bin/python3

BOT_TOKEN = "(TELEGRAM BOT TOKEN HERE)"

API_URL = "(SHAREX FLASK ENDPOINT HERE)" # eg https://localhost/share
API_KEY = "(SHAREX FLASK API KEY HERE)"

API_FORM = {'k': API_KEY}

USER_WHITELIST = (232800987,)

from uuid import uuid4
from datetime import datetime
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, CallbackContext, Filters
from telegram.utils.helpers import escape_markdown
import random
import string
import os
import requests
import systemd.daemon

if not os.path.isdir("./temp"): os.mkdir("./temp")


def rnd(l=32): return ''.join(random.choices(string.ascii_letters + string.digits, k=l))

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
    
    temp = './temp/' + rnd()
    
    file.download(temp)
    
    tempfile = open(temp,'rb')
    files = {'f': (filename, tempfile)}
    
    reply = update.message.reply_text("Uploading...")
    
    resp = requests.post(API_URL, files=files, data=API_FORM, verify=False)
    reply.edit_text(resp.text)
    tempfile.close()
    os.remove(temp)


def unsupported(update: Update, context: CallbackContext) -> None:
    if not authorised(update): return
    update.message.reply_text("Unsupported type (upload a photo or something)")

supported_uploads = Filters.document | Filters.photo | Filters.video | Filters.audio | Filters.voice | Filters.video_note

def main() -> None:
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher


    updater.dispatcher.add_handler(MessageHandler(supported_uploads, upload))
    updater.dispatcher.add_handler(MessageHandler(~supported_uploads, unsupported))
    
    systemd.daemon.notify('READY=1')
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
