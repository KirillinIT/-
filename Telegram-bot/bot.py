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
  item1 = types.KeyboardButton('Найти блогера по имени')
  item2 = types.KeyboardButton('Найти блогера по ссылке')
  # item3 = types.KeyboardButton("Найти блогера по тематике")
  # item4 = types.KeyboardButton("Найти блогеров по определённым соц. сетям")
  item5 = types.KeyboardButton('Поиск по определённому виду рекламы')
  # item6 = types.KeyboardButton("Поиск по определённому бюджету")
  # item7 = types.KeyboardButton("Добавить блогера в бота")
  markup.add(item1)
  markup.add(item2)
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

###############################################################################
#################### Кнопка "Найти блогера по имени" ##########################
###############################################################################

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
def search_blogger(message=None, blogger_name_def=None):
  global current_blogger_name  # Используем глобальную переменную
  if message.text.lower() == "вернуться в главное меню":
    return_to_main_menu(message)
  else:
    # Получаем введенное имя блогера от пользователя
    blogger_name = message.text.lower()
    current_blogger_name = message
    # bot.send_message(message.chat.id, f'{blogger_name}')
    blogger_name = blogger_name.split("\nстоимость:")[0]
    blogger_name = blogger_name.replace('имя блогера: ', '')

    # Ищем блогера в DataFrame
    filtered_df = df[df['блогер'].str.contains(blogger_name, na=False)]

    if not filtered_df.empty:
      first_words = []

      columns_to_exclude = [
          column for column in filtered_df.columns
          if column.startswith("Unnamed:")
      ]
      filtered_df = filtered_df.drop(columns=columns_to_exclude)

      for index, row in filtered_df.iterrows():
        if not pd.isna(row).all(
        ):  # Проверяем, что текущая строка не пуста (не все значения NaN)
          for column in filtered_df.columns:
            # Проверяем, что значение в столбце не является NaN
            if not pd.isna(row[column]):
              # Проверяем, что столбец не содержит ключевых слов в названии
              if not any(
                  word in column.lower()
                  for word in ["тематика", "налог", "контакты", "блогер"]):
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

      bot.send_message(
          message.chat.id,
          "Блогер с именем '{}' найден. Выберите социальные сети, которые вас интересуют:"
          .format(blogger_name),
          reply_markup=markup)

    else:
      # Если блогера не нашли, отправляем сообщение с предложением вернуться в главное меню
      markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
      item555 = types.KeyboardButton("Вернуться в главное меню")
      markup.add(item555)
      bot.send_message(
          message.chat.id,
          f"Блогер с именем '{blogger_name}' не найден. Вернитесь в главное меню.",
          reply_markup=markup)

    bot.register_next_step_handler(
        message, partial(filter_data_by_social_network,
                         filtered_df=filtered_df))


# Функция для фильтрации данных по социальной сети
def filter_data_by_social_network(message, filtered_df):
  if message.text.lower() == "вернуться в главное меню":
    return_to_main_menu(message)
  else:
    social_network = message.text

    # Фильтруем данные по выбранной социальной сети
    mask = filtered_df.columns.str.contains(social_network,
                                            na=False,
                                            case=False)

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
        # Инициализируем сообщение для вывода результатов
        result_message = "🖤 Результаты поиска для социальной сети {}:\n\n".format(
            social_network)

        # Добавляем информацию о блогере в начале каждой строки
        result_message += "<b>Имя блогера</b>: {}\n".format(str(row['блогер']).title())
        # result_message += "<b>Имя блогера</b>: {}\n".format(
        #   row['блогер'])
        # Перебираем столбцы и их значения в текущей строке
        result_message += "\n<b>Общая информация и статистика:</b>\n"
        for column, value in row.items():
          # Проверяем, что значение не является NaN и не соответствует столбцу 'тематика' или 'статистика'
          # if not pd.isna(value) and column != 'тематика' and column != 'блогер' and column != 'статистика' and column != 'стоимость':
          if not pd.isna(
              value
          ) and column != 'тематика' and column != 'блогер' and column != 'статистика' and 'стоимость' not in column:
            # Если значение - число, форматируем его с использованием пробела вместо запятой
            if isinstance(value, (int, float)):
              formatted_value = '{:,.0f}'.format(value).replace(',', ' ')
              result_message += "  ▶ <b>{}</b>: {}\n".format(
                  column.capitalize(), formatted_value)
            else:
              result_message += "  ▶ <b>{}</b>: {}\n".format(
                  column.capitalize(), value)

        #   # Добавляем столбцы с словом "стоимость"
        # result_message += "\n<b>Стоимость рекламных размещений:</b>\n"
        # for column, value in row.items():
        #   if 'стоимость' in column and not pd.isna(value):
        #     column_without_first_word = ' '.join(column.split()[1:])
        #     if isinstance(value, (int, float)):
        #       formatted_cost = '{:,.0f}'.format(value).replace(',', ' ')
        #       result_message += "  ▶ <b>{}</b>: {} рублей\n".format(
        #           column_without_first_word.capitalize(), formatted_cost)
        not_found_cost_column = True  # Инициализация флага перед циклом

        result_message += "\n<b>Стоимость рекламных размещений:</b>\n"
        column_without_first_word = ""  # Инициализация переменной
        for column, value in row.items():
          if 'стоимость' in column:
            if not pd.isna(value):
              column_without_first_word = ' '.join(column.split()[1:])
              if isinstance(value, (int, float)):
                formatted_cost = '{:,.0f}'.format(value).replace(',', ' ')
                result_message += "  ▶ <b>{}</b>: {} рублей\n".format(
                    column_without_first_word.capitalize(), formatted_cost)
              not_found_cost_column = False  # Нашли столбец с "стоимость"

        if not_found_cost_column:
          result_message += "  ▶ Размещение не постоянное. Обращайтесь с запросом к менеджерам блогера👇\n"



        # Добавляем статистику в конец строки
        for column, value in row.items():
          if 'статистика' in column and not pd.isna(row['статистика']):
            result_message += "\n<b>Статистика:</b> {}\n".format(
                row['статистика'])

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


###############################################################################
############# Кнопка "Поиск по определённому виду рекламы" ####################
###############################################################################

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

    item17 = types.KeyboardButton("Подкаст")
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
      "Выберите социальную сеть, в которой вам интересна реклама, с помощью кнопок ниже",
      reply_markup=markup)

  bot.register_next_step_handler(message, find_blogger_by_social_media_next)



def find_blogger_by_social_media_next(message):
  if message.text.lower() == "вернуться в главное меню":
    return_to_main_menu(message)
  else:
    social_media = message.text
    if social_media == 'Группы в VK':
      social_media = 'VK группа'
    elif social_media == 'Личные страницы в VK':
      social_media = 'VK личная страница'

    df_social_media = df.filter(like=social_media, axis=1)

    # Оставляем только столбцы, содержащие "стоимость"
    # df_social_media = df_social_media.filter(like='стоимость', axis=1)
    # df_social_media = df_social_media.loc[:, df_social_media.columns.str.contains('стоимость|блогер', case=False, na=False)]
    df_social_media = df_social_media.loc[:, df_social_media.columns.str.contains('стоимость|блогер', case=False, na=False) & ~df_social_media.columns.str.contains('охват', case=False, na=False)]


    df_social_media = df_social_media.rename(
        columns=lambda x: x.replace(f'{social_media} ', ''))
    df_social_media.columns = df_social_media.columns.str.replace(
        'стоимость ', '')

    df_social_media.columns = df_social_media.columns.str.capitalize()
    df_social_media = df_social_media.loc[:, ~df_social_media.columns.str.
                                          contains('охват', na=False)]
    col_names_social_media = list(df_social_media.columns)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for item in col_names_social_media:
      if item.lower() != 'блогер':
        button = types.KeyboardButton(item)
        markup.add(button)

    item555 = types.KeyboardButton("Вернуться в главное меню")
    markup.add(item555)

    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)

    bot.register_next_step_handler(
        message,
        partial(find_blogger_by_social_media_2_next,
                df_social_media=df_social_media))

def find_blogger_by_social_media_2_next(message, df_social_media):
  if message.text.lower() == "вернуться в главное меню":
    return_to_main_menu(message)
  else:
    position_social_media = message.text

    filtered_df_socnet_position = df_social_media[['Блогер', position_social_media]]

    row_counts = filtered_df_socnet_position[position_social_media].count()
    total_rows = row_counts.sum()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Да")
    item2 = types.KeyboardButton("Нет, вывести всех")
    item555 = types.KeyboardButton("Вернуться в главное меню")
    markup.add(item1, item2)
    markup.add(item555)
    bot.send_message(
        message.chat.id,
        f"Найдено <b>{total_rows}</b> варинтов.\n\nХотите ограничить по цене?",
        parse_mode='HTML',
        reply_markup=markup)

    # bot.register_next_step_handler(message, fork_of_functions_position)

    bot.register_next_step_handler(
      message,
      partial(fork_of_functions_position,
              filtered_df_socnet_position=filtered_df_socnet_position,
             position_social_media=position_social_media))


def fork_of_functions_position(message, filtered_df_socnet_position, position_social_media):
  if message.text.lower() == "да":
    find_blogger_by_social_media_price(message, filtered_df_socnet_position, position_social_media)
  elif message.text.lower() == "нет, вывести всех":
    find_blogger_by_social_media_all(message, filtered_df_socnet_position, position_social_media)
  elif message.text.lower() == "вернуться в главное меню":
    return_to_main_menu(message)
  else:
    bot.send_message(message.chat.id, "Ошибка👀. Нажмите /return")


def find_blogger_by_social_media_price(message, filtered_df_socnet_position, position_social_media):

  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  item555 = types.KeyboardButton("Вернуться в главное меню")
  markup.add(item555)
  bot.send_message(
      message.chat.id,
      "Введите максимальную стоимость рекламы без нулей и лишних символов.\n\nПример: 1000000",
      reply_markup=markup)

  bot.register_next_step_handler(
    message,
    partial(find_blogger_by_social_media_price_2,
            filtered_df_socnet_position=filtered_df_socnet_position,
            position_social_media=position_social_media))



def find_blogger_by_social_media_price_2(message, filtered_df_socnet_position, position_social_media):
  if message.text.lower() == "вернуться в главное меню":
    return_to_main_menu(message)
  else:
    price = float(message.text)
    # Создаем маску для столбцов, чьи значения меньше или равны 'price'
    mask = (filtered_df_socnet_position['Блогер'].notna()) & (filtered_df_socnet_position[position_social_media] <= price)
    filtered_df_socnet_position_price = filtered_df_socnet_position[mask].copy()



    # 'filtered_df' содержит только столбцы, удовлетворяющие условию

    # row_counts = filtered_df_socnet_position_price.count()
    # total_rows = row_counts.sum()
    total_rows = mask.sum()
    bot.send_message(message.chat.id,
                     f"Найдено варинтов: <b>{total_rows}</b>.",
                     parse_mode='HTML')


    for _, row in filtered_df_socnet_position_price.iterrows():
        result_message = ""
#        blogger = row['Блогер'].title()
        blogger = row['Блогер']

        price = row[position_social_media]

        if not pd.isna(price):
          # Создаем инлайн-клавиатуру для каждого вывода
            keyboard = types.InlineKeyboardMarkup()
            result_message += "<b>Имя блогера</b>: {}\n".format(str(blogger).title())
            price = '{:,.0f}'.format(price).replace(',', ' ')
            result_message += "<b>Стоимость</b>: {} рублей\n\n".format(price)

            blogger_name_def = blogger
            blogger_name_def = re.sub('<.*?>', '', blogger_name_def)
            button1_callback_data = f"more_{blogger_name_def}"
            # button2_callback_data = "more_info_"  # Значение для второй кнопки

            button1 = types.InlineKeyboardButton(text="Больше о блогере", callback_data=button1_callback_data)
            # button2 = types.InlineKeyboardButton(text="Контакты", callback_data=button2_callback_data)
            # keyboard.add(button1, button2)
            keyboard.add(button1)


            # Отправляем сообщение с инлайн-клавиатурой
            bot.send_message(message.chat.id, result_message, parse_mode='HTML', reply_markup=keyboard)

    # Создаем клавиатуру с одной кнопкой снизу
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item555 = types.KeyboardButton("Вернуться в главное меню")
    markup.add(item555)

    # Отправляем клавиатуру снизу
    bot.send_message(message.chat.id, '\nПо каждому блогеру вы можете загрузить отдельную информацию с помощью кнопок под сообщением или вернутесь в главное меню с помощью кнопки ниже\n', reply_markup=markup)
    bot.send_message(message.chat.id,f'{blogger}', reply_markup=markup)


def find_blogger_by_social_media_all(message, filtered_df_socnet_position, position_social_media):
  for _, row in filtered_df_socnet_position.iterrows():
      blogger = row['Блогер']
      price = row[position_social_media]

      if not pd.isna(price):
          keyboard = types.InlineKeyboardMarkup()
          result_message = "<b>Имя блогера</b>: {}\n".format(str(blogger).title())
          price = '{:,.0f}'.format(price).replace(',', ' ')
          result_message += "<b>Стоимость</b>: {} рублей\n\n".format(price)

          # Создаем инлайн-клавиатуру для этого результата
          # keyboard.add(types.InlineKeyboardButton(text="Дополнительная информация", callback_data="more_info_{}".format(blogger)))
          # Создаем инлайн-клавиатуру для этого результата

          blogger_name_def = blogger
          blogger_name_def = re.sub('<.*?>', '', blogger_name_def)
          button1_callback_data = f"more_{blogger_name_def}"
          # button2_callback_data = "more_info_{}"
        # Значение для второй кнопки
          button1 = types.InlineKeyboardButton(text="Больше о блогере", callback_data=button1_callback_data)
          # button2 = types.InlineKeyboardButton(text="Контакты", callback_data=button2_callback_data)
          # keyboard.add(button1, button2)

          keyboard.add(button1)

          # Отправляем сообщение с инлайн-клавиатурой
          bot.send_message(message.chat.id, result_message, parse_mode='HTML', reply_markup=keyboard)

  # Создаем клавиатуру с одной кнопкой снизу
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  item555 = types.KeyboardButton("Вернуться в главное меню")
  markup.add(item555)

  # Отправляем клавиатуру снизу
  bot.send_message(message.chat.id, '\nПо каждому блогеру вы можете загрузить отдельную информацию с помощью кнопок под сообщением или вернутесь в главное меню с помощью кнопки ниже\n', reply_markup=markup)


###############################################################################
################### Кнопка "Найти блогера по ссылке" ##########################
###############################################################################

@bot.message_handler(func=lambda message: message.text == 'Найти блогера по ссылке')
def find_blogger_by_href(message):

  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  item = types.KeyboardButton("Вернуться в главное меню")
  markup.add(item)

  bot.send_message(
      message.chat.id,
      "{0.first_name}, отправьте мне ссылку на блогера.\n\nНе рекомендуем искать Youtube-блогеров, так как у данной площадки может быть несколько ссылок на одного и того же блогера.\n\nЧтобы вернуться в главное меню, нажмите кнопку ниже.".format(message.from_user), reply_markup=markup)

  bot.register_next_step_handler(message, find_blogger_by_href_with_href)


def find_blogger_by_href_with_href(message):
  if message.text.lower() == "вернуться в главное меню":
      return_to_main_menu(message)
  else:
      # Получаем введенную ссылку на блогера от пользователя
      blogger_href = message.text.lower()

      # Отладочное сообщение для проверки ввода пользователя
      print("Полученный blogger_href:", blogger_href)

      # Ищем blogger_href во всех столбцах, содержащих слово "ссылка"
      keyword = 'ссылка'
      columns_with_link = [col for col in df.columns if keyword in col.lower()]

      filtered_df_href_sample = df[df[columns_with_link].apply(lambda col: col.astype(str).str.contains(blogger_href, case=False, na=False)).any(axis=1)]

      filtered_df_href = df[df.apply(lambda col: col.astype(str).str.contains(blogger_href, case=False, na=False)).any(axis=1)]

      social_network = ['Telegram', 'Instagram', 'VK группа', 'VK личная страница', 'VK Видео', 'YouTube', 'RuTube', 'Дзен', 'Дзен Шоу', 'Одноклассники', 'OK Шоу', 'Twitch', 'TikTok', 'Threads', 'Likee', 'Yappy', 'Подкаст']
  
      found_networks = []  # Создаем список для найденных социальных сетей

      for network in social_network:
        if network.lower() in blogger_href:
            found_networks.append(network)

      relevant_columns = [col for col in filtered_df_href.columns if any(network in col for network in found_networks) or col.strip().lower() == 'блогер' or col.strip().lower() == 'налог' or col.strip().lower() == 'контакты менеджера']
 

      if relevant_columns:
        filtered_df_href = filtered_df_href[relevant_columns]

      for network in found_networks:
        filtered_df_href = filtered_df_href.rename(columns=lambda x: x.replace(f'{network} ', ''))

      filtered_df_href.columns = [col.lower() for col in filtered_df_href.columns]


    
      if not filtered_df_href_sample.empty:
          markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
          item = types.KeyboardButton("Вернуться в главное меню")
          markup.add(item)

          bot.send_message(message.chat.id,
              "Мы нашли данного блогера в нашей базе. Информация ниже👇",
              reply_markup=markup)

          keyboard_data_social_network = types.ReplyKeyboardMarkup(
              one_time_keyboard=True)
          # item1 = types.KeyboardButton('Найти другие соц.сети блогера')
          item2 = types.KeyboardButton('Вернуться в главное меню')
          # keyboard_data_social_network.add(item1)
          keyboard_data_social_network.add(item2)

          result_message = ""  # Инициализируем result_message

          for index, row in filtered_df_href.iterrows():
            # Проверяем, что текущая строка не пуста
            if not row.isnull().all():              
              # Добавляем информацию о блогере в начале каждой строки
              result_message += "<b>Имя блогера</b>: {}\n".format(str(row['блогер']).title())
              # result_message += "<b>Имя блогера</b>: {}\n".format(
              #   row['блогер'])
              # Перебираем столбцы и их значения в текущей строке
              result_message += "\n<b>Общая информация и статистика:</b>\n"

              excluded_keywords = ['блогер', 'статистика', 'стоимость', 'налог', 'контакты менеджера']
              for column, value in row.items():
                # Проверяем, что значение не является NaN и не соответствует столбцу 'тематика' или 'статистика'
                if not pd.isna(value) and not all(keyword in column for keyword in excluded_keywords):

                # if not pd.isna(value) and column not in ['тематика', 'блогер', 'статистика', 'стоимость', 'налог'] and 'контакты менеджера' not in column:
                  # Если значение - число, форматируем его с использованием пробела вместо запятой
                  if isinstance(value, (int, float)):
                    formatted_value = '{:,.0f}'.format(value).replace(',', ' ')
                    result_message += "  ▶ <b>{}</b>: {}\n".format(
                        column.capitalize(), formatted_value)
                  else:
                    result_message += "  ▶ <b>{}</b>: {}\n".format(
                        column.capitalize(), value)

              not_found_cost_column = True  # Инициализация флага перед циклом

              result_message += "\n<b>Стоимость рекламных размещений:</b>\n"
              column_without_first_word = ""  # Инициализация переменной
              for column, value in row.items():
                if 'стоимость' in column:
                  if not pd.isna(value):
                    column_without_first_word = ' '.join(column.split()[1:])
                    if isinstance(value, (int, float)):
                      formatted_cost = '{:,.0f}'.format(value).replace(',', ' ')
                      result_message += "  ▶ <b>{}</b>: {} рублей\n".format(
                          column_without_first_word.capitalize(), formatted_cost)
                    not_found_cost_column = False  # Нашли столбец с "стоимость"

              if not_found_cost_column:
                result_message += "  ▶ Размещение не постоянное. Обращайтесь с запросом к менеджерам блогера👇\n"

              # Добавляем статистику в конец строки
              # for column, value in row.items():
              #   if 'статистика' in column and not pd.isna(row['статистика']):
              #     result_message += "\n<b>Статистика:</b> {}\n".format(
              #         row['статистика'])
              #   else:
              #     result_message += "\n<b>Статистика:</b> не найдена"


              max_message_length = 4000  # Максимальная длина сообщения в Telegram
              result_message += "\n\n"
              for i in range(0, len(result_message), max_message_length):
                bot.send_message(message.chat.id,
                                 result_message[i:i + max_message_length],
                                 parse_mode='HTML',
                                 reply_markup=keyboard_data_social_network)

          result_message = ""
          tax_value = filtered_df_href.get('налог')
          # Если серия не равна None и не пустая, то берем первый элемент (значение)
          if tax_value is not None and not tax_value.empty:
            tax_value = tax_value.values[0]
            result_message += "<b>✂️💵 Налог</b>: {}\n".format(tax_value)

          manager_contacts = filtered_df_href.get('контакты менеджера')
          # Если серия не равна None и не пустая, то берем первый элемент (значение)
          if manager_contacts is not None and not manager_contacts.empty:
            if len(manager_contacts.values) > 1:
              manager_contacts = manager_contacts.values[1]
            else:
              manager_contacts = manager_contacts.values[0]
            result_message += "<b>📞 Контакты менеджера</b>: {}\n".format(
                manager_contacts)

          bot.send_message(
              message.chat.id,
              result_message,
              parse_mode='HTML',
          )

      else:
          markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
          # item1 = types.KeyboardButton("Попробовать другую ссылку")
          item2 = types.KeyboardButton("Вернуться в главное меню")
          # markup.add(item1)
          markup.add(item2)
          bot.send_message(
              message.chat.id,
              "{0.first_name}, мы не нашли данного блогера в нашей базе.\n\nВы можете попробовать ввести другую ссылку с помощью кнопки 'Попробовать другую ссылку'. \n\nЧтобы вернуться в главное меню, нажмите кнопку ниже.".format(message.from_user), reply_markup=markup)






###############################################################################
####################### Функция для инлайн-кнопки #############################
###############################################################################

@bot.callback_query_handler(func=lambda call: call.data.startswith('more_'))
def handle_more_button(call):
    message = call.message
    search_blogger(message)



###############################################################################
###################### Обработчик команды /return #############################
###############################################################################

@bot.message_handler(
    func=lambda message: message.text.lower() == "вернуться в главное меню")
@bot.message_handler(commands=["return"])
def return_to_main_menu(message):

  markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                     one_time_keyboard=True)
  item1 = types.KeyboardButton('Найти блогера по имени')
  item2 = types.KeyboardButton('Найти блогера по ссылке')
  # item3 = types.KeyboardButton("Найти блогера по тематике")
  # item4 = types.KeyboardButton("Найти блогеров по определённым соц. сетям")
  item5 = types.KeyboardButton('Поиск по определённому виду рекламы')
  # item6 = types.KeyboardButton("Поиск по определённому бюджету")
  # item7 = types.KeyboardButton("Добавить блогера в бота")
  markup.add(item1)
  markup.add(item2)
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
