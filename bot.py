from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, ContextTypes

# Определяем этапы разговора
NAME, GENDER, RACE, CLASS = range(4)

# Опции для выбора
GENDERS = ["Мужчина", "Женщина"]
RACES = ["Человек", "Эльф", "Гном", "Полурослик", "Полуорк"]
CLASSES = ["Воин", "Лучник", "Вор", "Волшебник", "Бард"]

# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите имя персонажа:")
    return NAME

# Обработчик ввода имени
async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    keyboard = [[InlineKeyboardButton(gender, callback_data=gender) for gender in GENDERS]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите пол персонажа:", reply_markup=reply_markup)
    return GENDER

# Обработчик выбора пола
async def select_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['gender'] = query.data

    keyboard = [[InlineKeyboardButton(race, callback_data=race) for race in RACES]]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Выберите расу персонажа:", reply_markup=reply_markup)
    return RACE

# Обработчик выбора расы
async def select_race(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    # Проверка на кнопку "Назад"
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

# Обработчик выбора класса
async def select_class(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    # Проверка на кнопку "Назад"
    if query.data == "back":
        keyboard = [[InlineKeyboardButton(race, callback_data=race) for race in RACES]]
        keyboard.append([InlineKeyboardButton("Назад", callback_data="back")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите расу персонажа:", reply_markup=reply_markup)
        return RACE

    context.user_data['class'] = query.data

    # Завершаем создание персонажа
    character_info = (
        f"Ваш персонаж:\n"
        f"Имя: {context.user_data['name']}\n"
        f"Пол: {context.user_data['gender']}\n"
        f"Раса: {context.user_data['race']}\n"
        f"Класс: {context.user_data['class']}"
    )
    await query.edit_message_text(character_info)
    return ConversationHandler.END

# Команда для просмотра информации о текущем персонаже
async def show_character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    character_info = (
        f"Ваш персонаж:\n"
        f"Имя: {context.user_data.get('name', 'Не задано')}\n"
        f"Пол: {context.user_data.get('gender', 'Не задано')}\n"
        f"Раса: {context.user_data.get('race', 'Не задано')}\n"
        f"Класс: {context.user_data.get('class', 'Не задано')}"
    )
    await update.message.reply_text(character_info)

# Команда отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Создание персонажа отменено.")
    return ConversationHandler.END

def main():
    # Создание приложения бота
    application = Application.builder().token("7779425304:AAFLmdtoLH6bhyvj4jYVR4kb5GOniA1M6C4").build()

    # Обработчик разговоров для пошагового выбора персонажа
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_name)],
            GENDER: [CallbackQueryHandler(select_gender)],
            RACE: [CallbackQueryHandler(select_race)],
            CLASS: [CallbackQueryHandler(select_class)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Добавляем обработчики
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("character", show_character))

    application.run_polling()

if __name__ == "__main__":
    main()


