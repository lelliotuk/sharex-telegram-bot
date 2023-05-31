#!/usr/bin/python3

BOT_TOKEN = "(TELEGRAM BOT TOKEN HERE)"

API_URL = "(SHAREX FLASK ENDPOINT HERE)" # eg https://localhost/share
API_KEY = "(SHAREX FLASK API KEY HERE)"

API_FORM = {'k': API_KEY}

USER_WHITELIST = (123456789,) # AUTHORISED USER IDS HERE


from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackContext, filters
import requests
from io import BytesIO


async def authorised(update):
    if update.effective_user.id in USER_WHITELIST: 
        return True
    else:
        await update.message.reply_text("Unauthorised")
        return False


async def upload(update: Update, context: CallbackContext):
    if not authorised(update): return
    msg = update.message
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


    if type(msg.effective_attachment) is tuple:
        attachment = msg.effective_attachment[-1]
    else:
        attachment = msg.effective_attachment
    
    if hasattr(attachment, "get_file"):
        file = await attachment.get_file()
    else:
        reply = await update.message.reply_text("No file...")
        return
    
    if hasattr(file, "file_name"):
        filename = file.file_name
    else:
        ext = file.file_path.rsplit(".",1)[-1]
        filename = f"telegram_{timestamp}.{ext}"
    
    reply = await update.message.reply_text("Uploading...")
    
    temp = BytesIO()
    files = {'f': (filename, temp)}
    await file.download_to_memory(out=temp)
    temp.seek(0)
    
    try:
        req = requests.post(API_URL, files=files, data=API_FORM)
        await reply.edit_text(req.text)
    except:
        await reply.edit_text("API/Connection error")
        
    temp.close()


async def unsupported(update: Update, context: CallbackContext):
    if not authorised(update): return
    await update.message.reply_text("Unsupported type (upload a photo or something)")


SUPPORTED_UPLOADS = filters.ATTACHMENT


def main(): 
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(MessageHandler(SUPPORTED_UPLOADS, upload))
    application.add_handler(MessageHandler(~SUPPORTED_UPLOADS, unsupported))
    
    application.run_polling()


if __name__ == '__main__':
    main()
