import telebot
from telebot import types

import config
from config import stickerpacks, liveURLs, contentURLs, payments_token
from database import BotDB
from info import getTeamInfo, getDriverInfo, getCalendar, tickets_to_BahrainGP
from aiogram.types.message import ContentType

bot = telebot.TeleBot(config.token)
button_teams = types.KeyboardButton("Команды 🏎")
button_back = types.KeyboardButton("Меню 🧾")
button_drivers = types.KeyboardButton("Пилоты 👨‍🚀")
button_calendar = types.KeyboardButton("Календарь 📆")
button_stickers = types.KeyboardButton("Стикеры 😁")
button_live = types.KeyboardButton("Трансляции 📺")
button_content = types.KeyboardButton("Фильмы/сериалы 🎬")
button_toBahrain = types.KeyboardButton("Билеты на Гран-при Бахрейна 🇧🇭")
button_finishOrder = types.KeyboardButton("Завершить составление заказа 🏁")


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_menu = types.KeyboardButton("Меню 🧾")
    markup.add(button_menu)
    bot.send_message(message.chat.id,
                     text="<b>Привет, {0.first_name}!</b>\nЖми кнопку \"Меню\", чтобы начать работу со мной".format(
                         message.from_user), reply_markup=markup, parse_mode="HTML")
    bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEGph1jidiYrjUtZsw6JhY6XUMHMZT6awACEyIAAiO60ErugP0LGPd1mysE")


@bot.message_handler(commands=['hidebuttons', 'showbuttons'])
def buttons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if message.text == '/hidebuttons':
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,
                         text="<b>Кнопки успешно убраны!</b>\n\nЧтобы вернуть их на экран, нажмите на кнопку меню, расположенную в левой части поля ввода сообщений, и выберите нужное вам действие",
                         reply_markup=markup, parse_mode='HTML')
    elif message.text == '/showbuttons':
        markup.add(button_calendar, button_stickers, button_teams, button_drivers, button_live, button_content)
        bot.send_message(message.chat.id,
                         text="<b>Кнопки успешно возвращены!</b>\n\nЧтобы убрать их с экрана, нажмите на кнопку меню, расположенную в левой части поля ввода сообщений, и выберите нужное вам действие",
                         reply_markup=markup, parse_mode='HTML')


@bot.message_handler(content_types=['text'])
def func(message):
    bahrainInfo = tickets_to_BahrainGP()
    ticket_texts = {
        f"{bahrainInfo[0][ticket][0]} | {bahrainInfo[0][ticket][1]} | {bahrainInfo[0][ticket][2]}  {bahrainInfo[1][ticket]}":
            f"{bahrainInfo[0][ticket][0]}{bahrainInfo[0][ticket][1]}{bahrainInfo[0][ticket][2]}"
        for ticket in range(len(bahrainInfo[0]))}
    if (message.text in ["Меню 🧾", "Вернуться в главное меню 🔙", "Меню"]):
        with open("current_order", 'w'):
            pass
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(button_calendar, button_stickers, button_teams, button_drivers, button_live, button_content,
                   button_toBahrain)
        bot.send_message(message.chat.id, text="Что вас интересует?", reply_markup=markup)

    elif ((message.text == "Календарь 📆") or (message.text in list(map(str, range(1950, 2100))))):
        if message.text != "Календарь 📆":
            bot.send_message(message.chat.id, f"Одну минутку, сейчас поищу календарь на сезон {message.text}")
            calendar = getCalendar(message.text)
            if calendar != f"<b>Я не нашел календарь Формулы-1 сезона {message.text} 😞</b>\nПопросите его у меня позже, возможно я смогу его вам показать":
                calendar = f"<b>Вот, что мне удалось найти</b> 🕵️‍♂️\n\n\n{getCalendar(message.text)}"
            bot.send_message(message.chat.id, calendar, parse_mode="HTML")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(button_calendar, button_stickers, button_teams, button_drivers, button_live, button_content,
                       button_toBahrain)
            bot.send_message(message.chat.id, text="Выберите действие", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f"Введите интересующий вас год \n1950 — {config.current_year}")

    elif (message.text == "Стикеры 😁"):
        for sticker in stickerpacks:
            bot.send_sticker(message.chat.id, sticker)
        bot.send_message(message.chat.id,
                         text="<b>Вот стикерпаки, которые есть в наличии!</b>  🏎\n\nЧтобы добавить их к себе в библиотеку, нажми на любой из понравившихся стикеров и используй кнопку <b>\"Добавить стикеры\"</b>",
                         parse_mode="HTML")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(button_calendar, button_stickers, button_teams, button_drivers, button_live, button_content,
                   button_toBahrain)
        bot.send_message(message.chat.id, text="Выберите действие", reply_markup=markup)

    elif (message.text == "Команды 🏎"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        team_buttons = [types.KeyboardButton(f"{team}") for team in config.teamURLs.keys()]
        markup.add(*team_buttons)
        markup.add(button_back, row_width=2)
        bot.send_message(message.chat.id, text="Какой коллектив вас интересует?", reply_markup=markup)
    elif (message.text in config.teamURLs.keys()):
        teamInfo = getTeamInfo(config.teamURLs.get(message.text), config.teamPhotoURLs.get(message.text))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        button_Driver1 = types.KeyboardButton(f"{teamInfo[3][0]}")
        button_Driver2 = types.KeyboardButton(f"{teamInfo[3][1]}")
        markup.add(button_Driver1, button_Driver2, button_teams, button_back)
        bot.send_photo(message.chat.id, photo=open(f"teamPics/{teamInfo[1]}.jpg", 'rb'),
                       caption=f"{teamInfo[2]}",
                       parse_mode='HTML')
        bot.send_message(message.chat.id, f"{teamInfo[0][0]}", parse_mode='HTML')
        for textID in range(1, teamInfo[4] + 1):
            bot.send_message(message.chat.id, teamInfo[0][textID], parse_mode='HTML')
        bot.send_message(message.chat.id, text=f"Хотите узнать подробнее о пилотах <b>{teamInfo[1]}</b>?",
                         reply_markup=markup, parse_mode='HTML')
    elif (message.text in config.driverPhotoURLs.keys()):
        driverInfo = getDriverInfo(config.driverURLs.get(message.text), config.driverPhotoURLs.get(message.text))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(button_teams, button_drivers, button_back)
        bot.send_photo(message.chat.id, photo=open(f'driverPics/{driverInfo[1]}.jpg', 'rb'), caption=driverInfo[2],
                       parse_mode='HTML')
        bot.send_message(message.chat.id, text=driverInfo[0], parse_mode='HTML', reply_markup=markup)
    elif (message.text == "Пилоты 👨‍🚀"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        driver_buttons = [types.KeyboardButton(f"{driver}") for driver in config.driverPhotoURLs.keys()]
        markup.add(*driver_buttons)
        markup.add(button_back, row_width=2)
        bot.send_message(message.chat.id, text="Какой пилот вас интересует?", reply_markup=markup)
    elif (message.text == "Трансляции 📺"):
        markup = types.InlineKeyboardMarkup()
        live_buttons = [types.InlineKeyboardButton(text=f"{liveURL}", url=f"{liveURLs.get(liveURL)}") for liveURL in
                        liveURLs]
        markup.add(*live_buttons, row_width=1)
        bot.send_message(message.chat.id,
                         "<b>Где можно посмотреть Формулу-1? 📺</b>\n\nНиже представлены кнопки, ведущие на ресурсы с качественными прямыми трансляциями гоночных уик-эндов",
                         reply_markup=markup, parse_mode='HTML')
    elif (message.text == "Фильмы/сериалы 🎬"):
        markup = types.InlineKeyboardMarkup()
        content_buttons = [types.InlineKeyboardButton(text=f"{content}", url=f"{contentURLs.get(content)}") for content
                           in contentURLs]
        markup.add(*content_buttons, row_width=1)
        bot.send_message(message.chat.id,
                         f"<b>Не знаете, что посмотреть о мире Формулы-1? 🎬</b>"
                         f"\n\nНиже представлена подборка лучших фильмов/сериалов о знаковых фигурах и событиях из мира королевского автоспорта."
                         f"\n\n<b>К большому сожалению, не весь перечисленный контент доступен к просмотру в РФ официально, но, как мы знаем, кто ищет, тот всегда найдет.</b> 😉",
                         reply_markup=markup, parse_mode='HTML')
    elif (message.text == "Билеты на Гран-при Бахрейна 🇧🇭"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        bahrainInfo = tickets_to_BahrainGP()
        ticket_texts = [
            f"{bahrainInfo[0][ticket][0]} | {bahrainInfo[0][ticket][1]} | {bahrainInfo[0][ticket][2]}  {bahrainInfo[1][ticket]}"
            for ticket in range(len(bahrainInfo[0]))]
        ticket_buttons = [types.KeyboardButton(text=f"{ticket_texts[ticket]}") for ticket in range(len(bahrainInfo[0]))
                          if ticket_texts[ticket - 1] != ticket_texts[ticket]]
        tickets = f"<b>Билеты</b>\nТрибуна | Тип билета | Дни посещения  Цена"
        markup.add(*ticket_buttons, row_width=2)
        bot.send_photo(message.chat.id, photo=open('GPPics/BahrainGP.JPG', 'rb'), caption=f"{tickets}",
                       reply_markup=markup, parse_mode='HTML')
    elif (message.text in ticket_texts.keys()):
        database = BotDB('F1Assistant.db')
        ticketInfo = database.get_ticketType_info(ticket_texts.get(message.text))
        with open("current_order", "w") as file:
            file.write(f"{message.text} ")
            if len(ticketInfo) != 0:
                markup = types.ReplyKeyboardMarkup(row_width=8, resize_keyboard=True)
                markup.add(button_toBahrain, button_finishOrder, button_back, row_width=1)
                bot.send_message(message.chat.id,
                                 text=f"Вы можете выбрать другую трибуну или приступить к оплате выбранного билета\nДоступно к покупке: {len(ticketInfo)}",
                                 reply_markup=markup, parse_mode="HTML")
            else:
                markup = types.ReplyKeyboardMarkup(row_width=8, resize_keyboard=True)
                markup.add(button_toBahrain, row_width=1)
                bot.send_message(message.chat.id, "К сожалению, на этой трибуне закончились места.\nПопробуйте купить билет на других.")
    elif (message.text == "Завершить составление заказа 🏁"):
        with open("current_order", 'r') as file:
            order = list(file.read().split('\n'))
            ("".join(order)).split('$')
            PRICES = [types.LabeledPrice(label=f"{(''.join(position)).split(' $')[0]}", amount=f"{int(''.join(((''.join(order)).split('$')[-1]).split(',')))}")
                      for position in order]
            bot.send_invoice(message.chat.id,
                             title="Ваш заказ!",
                             provider_token=payments_token,
                             currency="usd",
                             is_flexible=False,
                             prices=PRICES,
                             description="Билет на гран-при",
                             invoice_payload="test-invoice-payload")
    else:
        bot.send_message(message.chat.id, text="Простие, я вас не понимаю 😔")

@bot.pre_checkout_query_handler(lambda query: True)
def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@bot.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
def successful_payment(message: types.Message):
    key = open("current_order", 'r').read()
    key = ''.join(((''.join(list(key))).split(' $')[0]).split(' | '))[:-1]
    database = BotDB('F1Assistant.db')
    database.ticketIsBought(key)
    database.add_boughtTicket_toLogs(key, message.from_user.id)
    with open("current_order", 'w') as file:
        bot.send_message(message.chat.id, f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!\nСкоро с вами свяжется менеджер для уточнения посадочных мест.")


bot.polling(none_stop=True)
