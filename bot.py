from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Добро пожаловать в игру. Напиши /play, чтобы начать.")

# Функция для команды /play
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Первый вопрос: Сколько будет 2 + 2? Напиши свой ответ.")

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if user_message == "4":
        await update.message.reply_text("Правильно! Ты выиграл!")
    else:
        await update.message.reply_text("Неправильно. Попробуй снова!")

# Создаем приложение
application = Application.builder().token("7779425304:AAFLmdtoLH6bhyvj4jYVR4kb5GOniA1M6C4").build()

# Добавляем обработчики команд и сообщений
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("play", play))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Запускаем бота
application.run_polling()

