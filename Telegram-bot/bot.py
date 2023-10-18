#bot
import telebot
from telebot import types
from string import Template
from background import keep_alive  #импорт функции для поддержки работоспособности

#basic
import pandas as pd
import re


df = pd.read_csv('bufer.csv')

token = 'TOKEN'  # Токен бота  # Замените на свой токен

bot = telebot.TeleBot(token)


# Команда /start
@bot.message_handler(commands=["start"])
def start(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  item1 = types.KeyboardButton("Найти блогера по имени")
  # item2 = types.KeyboardButton("Найти блогера по ссылке")
  # item3 = types.KeyboardButton("Найти блогера по тематике")
  # item4 = types.KeyboardButton("Найти блогеров по определённым соц. сетям")
  item5 = types.KeyboardButton("Поиск по определённому виду рекламы")
  # item6 = types.KeyboardButton("Поиск по определённому бюджету")
  # item7 = types.KeyboardButton("Добавить блогера в бота")
  markup.add(item1)
  # markup.add(item2)
  # markup.add(item3)
  # markup.add(item4)
  markup.add(item5)
  # markup.add(item6)
  # markup.add(item7)
  img = open('blog-articles.png', 'rb')  # Подтягиваем фотку для приветствия
  bot.send_photo(
      message.chat.id,
      img,
      "Добрый день, {0.first_name}! \n\nЯ - бот для поиска блогеров.\n\nНа данный момент я в режиме Бета-тестирования. Ожидаемое время запуска - 30.10.2023. \n\nВыберите один из вариантов поиска:"
      .format(message.from_user),
      reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.text == "Найти блогера по имени")
def find_blogger_by_name(message):

  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  item = types.KeyboardButton("Вернуться в главное меню")
  markup.add(item)

  bot.send_message(
      message.chat.id,
      "{0.first_name}, отправьте мне имя блогера. Чтобы вернуться в главное меню, нажмите кнопку ниже."
      .format(message.from_user),
      reply_markup=markup)

  bot.register_next_step_handler(message, search_blogger)


# Глобальная переменная для хранения имени блогера
current_blogger_name = None


#Функция для поиска блогера в DataFrame
def search_blogger(message):
  global current_blogger_name  # Используем глобальную переменную

  if message.text.lower() == "вернуться в главное меню":
    return_to_main_menu(message)

  else:
    # Получаем введенное имя блогера от пользователя
    blogger_name = message.text.lower()
    current_blogger_name = message

    # Ищем блогера в DataFrame
    filtered_df = df[df['блогер'].str.contains(blogger_name, na=False)]

    if not filtered_df.empty:
      first_words = []

      columns_to_exclude = [column for column in filtered_df.columns if column.startswith("Unnamed:")]
      filtered_df = filtered_df.drop(columns=columns_to_exclude)
      
      for index, row in filtered_df.iterrows():
        if not pd.isna(row).all():  # Проверяем, что текущая строка не пуста (не все значения NaN)
            for column in filtered_df.columns:
                # Проверяем, что значение в столбце не является NaN
                if not pd.isna(row[column]):
                    # Проверяем, что столбец не содержит ключевых слов в названии
                    if not any(word in column.lower() for word in ["тематика", "налог", "контакты", "блогер"]):
                        words = column.split()
                        for word in words:
                            if word.lower() == "vk":
                                first_words.append(" ".join(words[:2]))
                                break  # Для случаев, когда "VK" встречается, достаточно первого совпадения
                        else:
                            first_words.append(words[0])

      # Преобразуем список первых слов в уникальный список
      unique_first_words = list(set(first_words))


      markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
      for item in unique_first_words:
        button = types.KeyboardButton(item)
        markup.add(button)
      item555 = types.KeyboardButton("Вернуться в главное меню")
      markup.add(item555)
      # Задаем вопрос о социальных сетях и создаем клавиатуру
      # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
      # item1 = types.KeyboardButton("Telegram")
      # item2 = types.KeyboardButton("Instagram")

      # item3 = types.KeyboardButton("Группы в VK")
      # item4 = types.KeyboardButton("Личные страницы в VK")
      # item5 = types.KeyboardButton("VK Видео")

      # item6 = types.KeyboardButton("YouTube")
      # item7 = types.KeyboardButton("RuTube")

      # item8 = types.KeyboardButton("Дзен")
      # item9 = types.KeyboardButton("Дзен Шоу")

      # item10 = types.KeyboardButton("Одноклассники")
      # item11 = types.KeyboardButton("OK Шоу")

      # item12 = types.KeyboardButton("Twitch")

      # item13 = types.KeyboardButton("TikTok")

      # item14 = types.KeyboardButton("Threads")
      # item15 = types.KeyboardButton("Likee")
      # item16 = types.KeyboardButton("Yappy")

      # item17 = types.KeyboardButton("Подкасты")
      # item18 = types.KeyboardButton("Вернуться в главное меню")

      # markup.add(item1, item2)
      # markup.add(item3, item4, item5)
      # markup.add(item6)
      # markup.add(item7)
      # markup.add(item8, item9)
      # markup.add(item10, item11)
      # markup.add(item12)
      # markup.add(item13)
      # markup.add(item14, item15, item16)
      # markup.add(item17)
      # markup.add(item18)

      bot.send_message(
          message.chat.id,
          "Блогер с именем '{}' найден. Выберите социальные сети, которые вас интересуют:"
          .format(blogger_name),
          reply_markup=markup)

    bot.register_next_step_handler(
        message, partial(filter_data_by_social_network,
                         filtered_df=filtered_df))


# Функция для фильтрации данных по социальной сети
def filter_data_by_social_network(message, filtered_df):
  social_network = message.text

  # Фильтруем данные по выбранной социальной сети
  mask = filtered_df.columns.str.contains(social_network, na=False, case=False)

  filtered_df_socnet = filtered_df.loc[:, mask]

  filtered_df_socnet = filtered_df_socnet.rename(
      columns=lambda x: x.replace(f'{social_network} ', ''))

  filtered_df_socnet = filtered_df_socnet.apply(
      lambda x: x.map(lambda x: np.nan if x is None else x))

  # Добавляем кнопки
  keyboard_data_social_network = types.ReplyKeyboardMarkup(
      one_time_keyboard=True)
  item1 = types.KeyboardButton('Найти другие соц.сети блогера')
  item2 = types.KeyboardButton('Вернуться в главное меню')
  keyboard_data_social_network.add(item1)
  keyboard_data_social_network.add(item2)

  result_message = ""  # Инициализируем result_message

  for index, row in filtered_df_socnet.iterrows():
    # Проверяем, что текущая строка не пуста
    if not row.isnull().all():
      #Инициализируем сообщение для вывода результатов
      result_message = "🖤 Результаты поиска для социальной сети {}:\n\n".format(
          social_network)
      # result_message = "🖤 Результаты поиска для социальной сети :\n\n"

      # Добавляем информацию о блогере в начале каждой строки
      result_message += "<b>Имя блогера</b>: {}\n".format(row['блогер'])
          # row['блогер'].title())

      # Перебираем столбцы и их значения в текущей строке
      for column, value in row.items():
        # Проверяем, что значение не является NaN и не соответствует столбцу 'тематика'
        if not pd.isna(value) and column != 'тематика' and column != 'блогер' and column != 'статистика':
          # Если значение - число, форматируем его с использованием пробела вместо запятой
          if isinstance(value, (int, float)):
              formatted_value = '{:,.0f}'.format(value).replace(',', ' ')
              result_message += "<b>{}</b>: {}\n".format(column.capitalize(), formatted_value)
          else:
              result_message += "<b>{}</b>: {}\n".format(column.capitalize(), value)
          # result_message += "<b>{}</b>: {}\n".format(column.capitalize(),
          #                                            value)

      # Добавляем статистику в конец строки
      if 'статистика' in row:
        if not pd.isna(row['статистика']):
          result_message += "<b>Статистика:</b> {}\n".format(row['статистика'])
      # # Отправляем результат пользователю
      # result_message += "<b>\n\n✂️💵 Налог</b>: {}\n".format(row['налог'])
      # result_message += "<b>☎ Контакты менеджера</b>: {}\n".format(row['контакты менеджера'])

      max_message_length = 4000  # Максимальная длина сообщения в Telegram
      result_message += "\n\n"
      for i in range(0, len(result_message), max_message_length):
        bot.send_message(message.chat.id,
                         result_message[i:i + max_message_length],
                         parse_mode='HTML',
                         reply_markup=keyboard_data_social_network)

  result_message = ""
  tax_value = filtered_df.get('налог')
  # Если серия не равна None и не пустая, то берем первый элемент (значение)
  if tax_value is not None and not tax_value.empty:
    tax_value = tax_value.values[0]
    result_message += "<b>✂️💵 Налог</b>: {}\n".format(tax_value)

  manager_contacts = filtered_df.get('контакты менеджера')
  # Если серия не равна None и не пустая, то берем первый элемент (значение)
  if manager_contacts is not None and not manager_contacts.empty:
    if len(manager_contacts.values) > 1:
      manager_contacts = manager_contacts.values[1]
    else:
      manager_contacts = manager_contacts.values[0]
    result_message += "<b>☎ Контакты менеджера</b>: {}\n".format(
        manager_contacts)

  bot.send_message(
      message.chat.id,
      result_message,
      parse_mode='HTML',
  )

  bot.register_next_step_handler(message, fork_of_functions)


def fork_of_functions(message):
  if message.text.lower() == "вернуться в главное меню":
    return_to_main_menu(message)
  elif message.text.lower() == "найти другие соц.сети блогера":
    try_other_social_networks(message)
  else:
    bot.send_message(message.chat.id, "Ошибка👀. Нажмите /return")


@bot.message_handler(func=lambda message: message.text.lower() ==
                     "Найти другие соц.сети блогера")
def try_other_social_networks(message):
  global current_blogger_name  # Используем глобальную переменную

  if current_blogger_name is not None:
    search_blogger(
        current_blogger_name)  # Вызываем функцию return_to_main_menu
  else:
    bot.send_message(message.chat.id, "Имя блогера не найдено.")


@bot.message_handler(
    func=lambda message: message.text == "Поиск по определённому виду рекламы")
def find_blogger_by_social_media(message):
  if message.text.lower() == "вернуться в главное меню":
    return_to_main_menu(message)
  else:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Telegram")
    item2 = types.KeyboardButton("Instagram")

    item3 = types.KeyboardButton("Группы в VK")
    item4 = types.KeyboardButton("Личные страницы в VK")
    item5 = types.KeyboardButton("VK Видео")

    item6 = types.KeyboardButton("YouTube")
    item7 = types.KeyboardButton("RuTube")

    item8 = types.KeyboardButton("Дзен")
    item9 = types.KeyboardButton("Дзен Шоу")

    item10 = types.KeyboardButton("Одноклассники")
    item11 = types.KeyboardButton("OK Шоу")

    item12 = types.KeyboardButton("Twitch")

    item13 = types.KeyboardButton("TikTok")

    item14 = types.KeyboardButton("Threads")
    item15 = types.KeyboardButton("Likee")
    item16 = types.KeyboardButton("Yappy")

    item17 = types.KeyboardButton("Подкасты")
    item18 = types.KeyboardButton("Вернуться в главное меню")

    markup.add(item1, item2)
    markup.add(item3, item4, item5)
    markup.add(item6)
    markup.add(item7)
    markup.add(item8, item9)
    markup.add(item10, item11)
    markup.add(item12)
    markup.add(item13)
    markup.add(item14, item15, item16)
    markup.add(item17)
    markup.add(item18)

  bot.send_message(
      message.chat.id,
      "Выберите социальную сеть, в которой вам интересна реклама с помощью кнопок ниже",
      reply_markup=markup)

  bot.register_next_step_handler(message, find_blogger_by_social_media_next)


def find_blogger_by_social_media_next(message):
  social_media = message.text
  df_social_media = df.filter(like=social_media, axis=1)
  # Оставляем только столбцы, содержащие "стоимость"
  df_social_media = df_social_media.filter(like='стоимость', axis=1)

  df_social_media = df_social_media.rename(
      columns=lambda x: x.replace(f'{social_media} ', ''))
  df_social_media.columns = df_social_media.columns.str.replace(
      'стоимость за', '')
  df_social_media = df_social_media.loc[:, ~df_social_media.columns.str.
                                        contains('охват', na=False)]
  col_names_social_media = list(df_social_media.columns)

  # Черновик
  # КОД ДЛЯ ДИНАМИЧЕСКИХ КНОПОК
  # col_names_social_media = [re.sub(r'\(.*\)', '', item) for item in col_names_social_media]
  # col_names_social_media = [item.replace('Телеграм', 'Тг') for item in col_names_social_media]
  # col_names_social_media = [item.replace('Инстаграм', 'Инст') for item in col_names_social_media]
  # col_names_social_media = [item[:18] + '...' if len(item) > 21 else item for item in col_names_social_media]

  # invalid_characters = ['@', '#', '$', '%', '&', '*', ' ']
  # cleaned_col_names = [re.sub('|'.join(map(re.escape, invalid_characters)), '', col_name) for col_name in col_names_social_media]

  # bot.send_message(message.chat.id, f"Выберите опцию{col_names_social_media}:")
  # # Создаем инлайн-клавиатуру с кнопками на основе столбцов
  # markup = types.InlineKeyboardMarkup(row_width=1)
  # for col_name in col_names_social_media:
  #     button = types.InlineKeyboardButton(col_name, callback_data=col_name)
  #     markup.add(button)

  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  for item in col_names_social_media:
    button = types.KeyboardButton(item)
    markup.add(button)

  item555 = types.KeyboardButton("Вернуться в главное меню")
  markup.add(item555)

  # Отправляем сообщение с клавиатурой
  bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)


# Обработчик команды /return
@bot.message_handler(
    func=lambda message: message.text.lower() == "вернуться в главное меню")
@bot.message_handler(commands=["return"])
def return_to_main_menu(message):

  markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                     one_time_keyboard=True)
  item1 = types.KeyboardButton("Найти блогера по имени")
  # item2 = types.KeyboardButton("Найти блогера по ссылке")
  # item3 = types.KeyboardButton("Найти блогера по тематике")
  # item4 = types.KeyboardButton("Найти блогеров по определённым соц. сетям")
  item5 = types.KeyboardButton("Поиск по определённому виду рекламы")
  # item6 = types.KeyboardButton("Поиск по определённому бюджету")
  # item7 = types.KeyboardButton("Добавить блогера в бота")
  markup.add(item1)
  # markup.add(item2)
  # markup.add(item3)
  # markup.add(item4)
  markup.add(item5)
  # markup.add(item6)
  # markup.add(item7)

  bot.send_message(message.chat.id,
                   "Продолжите пользоваться нашим ботом с помощью кнопок ниже",
                   reply_markup=markup)


keep_alive()  #запускаем flask-сервер в отдельном потоке.
bot.polling(non_stop=True, interval=0)  #запуск бота
