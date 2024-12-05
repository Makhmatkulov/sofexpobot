from dotenv import load_dotenv
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["O'zbekcha", "English", "Русский"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Xush kelibsiz! Tilni tanlang.\nWelcome! Please choose a language.\nДобро пожаловать! Выберите язык.",
        reply_markup=reply_markup
    )
    context.user_data['step'] = 'language'


# Handle text input
# Handle text input
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('step')
    text = update.message.text.strip()

    if step == 'language':  # Language selection step
        language_map = {"O'zbekcha": 'uz', "English": 'en', "Русский": 'ru'}
        context.user_data['language'] = language_map.get(text, 'en')

        expos = {
            'uz': ["AGRO PRO EXPO - 25-27 fevral", "WORLD EDU EXPO - 4-5 aprel",
                   "e-com & retail - 6-7 may", "PROMOTORS SHOW - 29-may - 1-iyun",
                   "Samarkand Hospitality Days - 9-12 oktyabr"],
            'en': ["AGRO PRO EXPO - February 25-27", "WORLD EDU EXPO - April 4-5",
                   "e-com & retail - May 6-7", "PROMOTORS SHOW - May 29-June 1",
                   "Samarkand Hospitality Days - October 9-12"],
            'ru': ["AGRO PRO EXPO - 25-27 февраля", "WORLD EDU EXPO - 4-5 апреля",
                   "e-com & retail - 6-7 мая", "PROMOTORS SHOW - 29 мая-1 июня",
                   "Samarkand Hospitality Days - 9-12 октября"]
        }
        lang = context.user_data['language']
        reply_markup = ReplyKeyboardMarkup([[expo] for expo in expos[lang]],
                                           resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            {"uz": "Qaysi ekspo-ga tashrif buyurasiz?",
             "en": "Which expo will you visit?",
             "ru": "Какую выставку вы посетите?"}[lang],
            reply_markup=reply_markup
        )
        context.user_data['step'] = 'expo'

    elif step == 'expo':  # Expo selection step
        context.user_data['expo'] = text
        lang = context.user_data['language']
        await update.message.reply_text(
            {"uz": "Ismingizni kiriting:", "en": "Enter your name:", "ru": "Введите ваше имя:"}[lang]
        )
        context.user_data['step'] = 'name'

    elif step == 'name':  # Name input step
        context.user_data['name'] = text
        lang = context.user_data['language']
        contact_button = KeyboardButton(
            {"uz": "Kontaktni ulashing", "en": "Share Contact", "ru": "Поделиться контактом"}[lang],
            request_contact=True
        )
        reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            {"uz": "Kontakt ma'lumotlaringizni ulashing:",
             "en": "Share your contact information:",
             "ru": "Поделитесь вашими контактными данными:"}[lang],
            reply_markup=reply_markup
        )
        context.user_data['step'] = 'contact'

    elif step == 'email':  # Email input step
        if text.lower() == "pass":
            context.user_data['email'] = None
        else:
            context.user_data['email'] = text
        lang = context.user_data['language']
        await update.message.reply_text(
            {"uz": "Kompaniya nomini kiriting:", "en": "Enter your company name:", "ru": "Введите название вашей компании:"}[lang]
        )
        context.user_data['step'] = 'company'

    elif step == 'company':  # Company input step
        context.user_data['company'] = text
        lang = context.user_data['language']
        confirmation_text = {
            'uz': f"Tasdiqlaysizmi?\n\n"
                  f"Ism: {context.user_data['name']}\n"
                  f"Kontakt: {context.user_data['contact']}\n"
                  f"Email: {context.user_data.get('email', 'Mavjud emas')}\n"
                  f"Kompaniya: {context.user_data['company']}\n"
                  f"Ekspo: {context.user_data['expo']}",
            'en': f"Do you confirm?\n\n"
                  f"Name: {context.user_data['name']}\n"
                  f"Contact: {context.user_data['contact']}\n"
                  f"Email: {context.user_data.get('email', 'Not provided')}\n"
                  f"Company: {context.user_data['company']}\n"
                  f"Expo: {context.user_data['expo']}",
            'ru': f"Вы подтверждаете?\n\n"
                  f"Имя: {context.user_data['name']}\n"
                  f"Контакт: {context.user_data['contact']}\n"
                  f"Email: {context.user_data.get('email', 'Не указано')}\n"
                  f"Компания: {context.user_data['company']}\n"
                  f"Выставка: {context.user_data['expo']}"
        }

        confirm_button = {"uz": "Tasdiqlash", "en": "Confirm", "ru": "Подтвердить"}[lang]
        retry_button = {"uz": "Qaytadan", "en": "Retry", "ru": "Повторить"}[lang]

        reply_markup = ReplyKeyboardMarkup([[confirm_button, retry_button]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(confirmation_text[lang], reply_markup=reply_markup)
        context.user_data['step'] = 'confirmation'


    elif step == 'confirmation':  # Confirmation step
        lang = context.user_data['language']
        if text.lower() == {"uz": "tasdiqlash", "en": "confirm", "ru": "подтвердить"}[lang].lower():
            # Confirmation message
            confirmation_messages = {
                'uz': "Ma'lumotlaringiz muvaffaqiyatli qabul qilindi. Rahmat!",
                'en': "Your data has been submitted successfully. Thank you!",
                'ru': "Ваши данные успешно отправлены. Спасибо!"
            }
            await update.message.reply_text(confirmation_messages[lang])
            # Determine the appropriate image to send based on the selected expo
            expo_to_image = {
                "AGRO PRO EXPO": "images/AGRO.png",
                "WORLD EDU EXPO": "images/WORLDEDUTICKET.png",
                "e-com & retail": "images/E-COMREATILEXPOTICKET.png",
                "Samarkand Hospitality Days": "images/HOREKATICKET.png",
            }
            # Get the selected expo and normalize to match the dictionary keys
            selected_expo = context.user_data['expo']
            image_path = None
            for keyword, path in expo_to_image.items():
                if keyword in selected_expo:
                    image_path = path
                    break
            # Send the image only if it exists
            if image_path:
                with open(image_path, 'rb') as photo:
                    await update.message.reply_photo(photo=photo)
            # Provide restart option
            restart_buttons = {
                'uz': [["/start"]],
                'en': [["/start"]],
                'ru': [["/start"]]
            }
            await update.message.reply_text(
                {"uz": "Yana bir bor ishlatmoqchimisiz?",
                 "en": "Would you like to start again?",
                 "ru": "Хотите начать снова?"}[lang],
                reply_markup=ReplyKeyboardMarkup(restart_buttons[lang], one_time_keyboard=True, resize_keyboard=True)
            )
            # Clear user data for a fresh start
            context.user_data.clear()

        elif text.lower() == {"uz": "qaytadan", "en": "retry", "ru": "повторить"}[lang].lower():
            await update.message.reply_text(
                {"uz": "Ismingizni kiriting:", "en": "Enter your name:", "ru": "Введите ваше имя:"}[lang]
            )
            context.user_data['step'] = 'name'


# Handle contact sharing
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    context.user_data['contact'] = contact.phone_number
    lang = context.user_data['language']
    reply_markup = ReplyKeyboardMarkup([["Pass"]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        {"uz": "Emailingizni kiriting (Ixtiyoriy):",
         "en": "Enter your email (Optional):",
         "ru": "Введите ваш email (Необязательный):"}[lang],
        reply_markup=reply_markup
    )
    context.user_data['step'] = 'email'



# Main function
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    application.run_polling()


if __name__ == "__main__":
    main()