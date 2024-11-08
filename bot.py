import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler, ConversationHandler,
    MessageHandler, filters
)
from character import Character

# Хранилище персонажей
character_data = {}

# Состояния для ConversationHandler
NAME, GENDER, RACE, CLASS = range(4)

# Функция начала работы бота
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Создать персонажа", callback_data="create_character")],
        [InlineKeyboardButton("Мой персонаж", callback_data="view_character")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# Обработчик для кнопок в меню
def menu(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "create_character":
        if query.from_user.id in character_data:
            query.edit_message_text("Персонаж уже создан.")
            return ConversationHandler.END
        else:
            query.edit_message_text("Введите имя вашего персонажа:")
            return NAME
    elif query.data == "view_character":
        if query.from_user.id in character_data:
            char_info = character_data[query.from_user.id].get_info()
            query.edit_message_text(f"Ваш персонаж:\n\n{char_info}")
        else:
            query.edit_message_text("У вас еще нет персонажа.")
    return ConversationHandler.END

# Обработчики для создания персонажа
def set_name(update, context):
    user_id = update.message.from_user.id
    context.user_data['name'] = update.message.text
    update.message.reply_text("Введите пол вашего персонажа:")
    return GENDER

def set_gender(update, context):
    context.user_data['gender'] = update.message.text
    update.message.reply_text("Введите расу вашего персонажа:")
    return RACE

def set_race(update, context):
    context.user_data['race'] = update.message.text
    update.message.reply_text("Введите класс вашего персонажа:")
    return CLASS

def set_class(update, context):
    user_id = update.message.from_user.id
    name = context.user_data['name']
    gender = context.user_data['gender']
    race = context.user_data['race']
    char_class = update.message.text

    # Создаем экземпляр персонажа и сохраняем его
    character_data[user_id] = Character(name, gender, race, char_class)
    update.message.reply_text("Персонаж создан!")
    return ConversationHandler.END

def main():
    # Создание приложения с токеном
    application = Application.builder().token("7779425304:AAFLmdtoLH6bhyvj4jYVR4kb5GOniA1M6C4").build()

    # Обработчик команды /start
    start_handler = CommandHandler("start", start)

    # Обработчик для меню
    menu_handler = CallbackQueryHandler(menu)

    # Обработчик для создания персонажа
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(menu, pattern="create_character")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_name)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_gender)],
            RACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_race)],
            CLASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_class)],
        },
        fallbacks=[],
        per_chat=True  # Используем per_chat=True для отслеживания чата, не сообщений
    )

    # Добавляем обработчики в приложение
    application.add_handler(start_handler)
    application.add_handler(menu_handler)
    application.add_handler(conv_handler)

    # Настройка вебхука
    host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    webhook_url = f"https://{host}:443/webhook"
    application.run_webhook(
        listen="0.0.0.0",
        port=443,
        url_path="/webhook",
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()
