from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
import os

# Хранилище персонажей (в реальной версии лучше использовать базу данных)
character_data = {}

# Статус для ConversationHandler
CREATE_CHARACTER, NAME, GENDER, RACE, CLASS = range(5)

def start(update, context):
    # Кнопки для выбора действий
    keyboard = [
        [InlineKeyboardButton("Создать персонажа", callback_data="create_character")],
        [InlineKeyboardButton("Мой персонаж", callback_data="view_character")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

def menu(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "create_character":
        if query.from_user.id in character_data:
            query.edit_message_text("Персонаж уже создан.")
        else:
            query.edit_message_text("Введите имя вашего персонажа:")
            return NAME
    elif query.data == "view_character":
        if query.from_user.id in character_data:
            char_info = character_data[query.from_user.id].get_info()
            query.edit_message_text(f"Ваш персонаж:\n\n{char_info}")
        else:
            query.edit_message_text("У вас еще нет персонажа.")

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

def check_webhook(application):
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        print(f"Webhook URL: {webhook_url}")
        # Пытаемся установить вебхук, если URL не пустой
        try:
            # Устанавливаем вебхук для бота (если настроен URL)
            application.bot.set_webhook(url=webhook_url)
            print("Webhook успешно установлен.")
        except Exception as e:
            print(f"Ошибка при установке вебхука: {e}")
    else:
        print("WEBHOOK_URL не задан, использование polling.")

def main():
    # Получаем URL хоста из переменной окружения
    host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    webhook_url = f"https://{host}:443/webhook"  # Пример вебхука

    # Стартуем приложение
    application = Application.builder().token("7779425304:AAEg3FA1vicST5AkwORBNaeDTLuvoTEbzKM").build()

    # Проверяем webhook
    check_webhook(application)

    # Команды и обработчики
    menu_handler = CallbackQueryHandler(menu)
    conv_handler = ConversationHandler(
        entry_points=[menu_handler],
        states={
            NAME: [MessageHandler(filters.TEXT, set_name)],
            GENDER: [MessageHandler(filters.TEXT, set_gender)],
            RACE: [MessageHandler(filters.TEXT, set_race)],
            CLASS: [MessageHandler(filters.TEXT, set_class)],
        },
        fallbacks=[]
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(menu_handler)

    # Запуск polling
    application.run_polling()

if __name__ == "__main__":
    main()
