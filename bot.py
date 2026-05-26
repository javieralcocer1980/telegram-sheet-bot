import os
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SHEET_ID = os.environ.get("SHEET_ID")
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")

def get_sheet_data():
    import json
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.loads(GOOGLE_CREDENTIALS)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    return sheet.get_all_values()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.lower().strip()
    try:
        datos = get_sheet_data()
        for i in range(1, len(datos)):
            clave = datos[i][0].lower().strip()
            if mensaje in clave or clave in mensaje:
                await update.message.reply_text(datos[i][1])
                return
        await update.message.reply_text("No encontré información sobre eso.")
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("Error al consultar el Sheet.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
