from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Добро пожаловать в игру. Напиши /play, чтобы начать.")

def play(update: Update, context: CallbackContext):
    update.message.reply_text("Первый вопрос: Сколько будет 2 + 2? Напиши свой ответ.")

def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    if user_message == "4":
        update.message.reply_text("Правильно! Ты выиграл!")
    else:
        update.message.reply_text("Неправильно. Попробуй снова!")

updater = Updater("7779425304:AAFLmdtoLH6bhyvj4jYVR4kb5GOniA1M6C4")

updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("play", play))
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

updater.start_polling()
updater.idle()
 
