from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, ContextTypes
import os

# Определяем этапы разговора
NAME, GENDER, RACE, CLASS = range(4)

# Опции для выбора
GENDERS = ["Мужчина", "Женщина"]
RACES = ["Человек", "Эльф", "Гном", "Полурослик", "Полуорк"]
CLASSES = ["Воин", "Лучник", "Вор", "Волшебник", "Бард"]

# Начальная команда с бар-меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "name" in context.user_data:
        keyboard = [
            [InlineKeyboardButton("Посмотреть персонажа", callback_data="show_character")],
            [InlineKeyboardButton("Создать нового персонажа", callback_data="create_character")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Персонаж не найден. Давайте создадим нового!")
        await create_character(update, context)

async def create_character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите имя персонажа:")
    return NAME

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    keyboard = [[InlineKeyboardButton(gender, callback_data=gender) for gender in GENDERS]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите пол персонажа:", reply_markup=reply_markup)
    return GENDER

async def select_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['gender'] = query.data

    keyboard = [[InlineKeyboardButton(race, callback_data=race) for race in RACES]]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Выберите расу персонажа:", reply_markup=reply_markup)
    return RACE

async def select_race(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "back":
        keyboard = [[InlineKeyboardButton(gender, callback_data=gender) for gender in GENDERS]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите пол персонажа:", reply_markup=reply_markup)
        return GENDER

    context.user_data['race'] = query.data
    keyboard = [[InlineKeyboardButton(class_, callback_data=class_) for class_ in CLASSES]]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Выберите класс персонажа:", reply_markup=reply_markup)
    return CLASS

async def select_class(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "back":
        keyboard = [[InlineKeyboardButton(race, callback_data=race) for race in RACES]]
        keyboard.append([InlineKeyboardButton("Назад", callback_data="back")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите расу персонажа:", reply_markup=reply_markup)
        return RACE

    context.user_data['class'] = query.data
    character_info = (
        f"Ваш персонаж:\n"
        f"Имя: {context.user_data['name']}\n"
        f"Пол: {context.user_data['gender']}\n"
        f"Раса: {context.user_data['race']}\n"
        f"Класс: {context.user_data['class']}"
    )
    await query.edit_message_text(character_info)
    return ConversationHandler.END

async def show_character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    character_info = (
        f"Ваш персонаж:\n"
        f"Имя: {context.user_data.get('name', 'Не задано')}\n"
        f"Пол: {context.user_data.get('gender', 'Не задано')}\n"
        f"Раса: {context.user_data.get('race', 'Не задано')}\n"
        f"Класс: {context.user_data.get('class', 'Не задано')}"
    )
    await update.message.reply_text(character_info)

async def menu_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "show_character":
        character_info = (
            f"Ваш персонаж:\n"
            f"Имя: {context.user_data.get('name', 'Не задано')}\n"
            f"Пол: {context.user_data.get('gender', 'Не задано')}\n"
            f"Раса: {context.user_data.get('race', 'Не задано')}\n"
            f"Класс: {context.user_data.get('class', 'Не задано')}"
        )
        await query.edit_message_text(character_info)
    elif query.data == "create_character":
        await create_character(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Создание персонажа отменено.")
    return ConversationHandler.END

def main():
    application = Application.builder().token("7779425304:AAFLmdtoLH6bhyvj4jYVR4kb5GOniA1M6C4").build()

    # Указываем URL вашего бота на Render
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"

    cconv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(create_character, pattern="create_character")],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_name)],
        GENDER: [CallbackQueryHandler(select_gender)],
        RACE: [CallbackQueryHandler(select_race)],
        CLASS: [CallbackQueryHandler(select_class)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=True  # Добавляем этот параметр
)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(menu_button_handler))

    # Устанавливаем вебхук
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path="/webhook",
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()
