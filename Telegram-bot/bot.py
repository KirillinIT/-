#bot
import telebot
from telebot import types
from string import Template
from background import keep_alive  #импорт функции для поддержки работоспособности

#basic
import pandas as pd
from functools import partial

#data
df = pd.read_csv('bufer.csv')
token = 'TOKEN'  # Токен бота  # Замените на свой токен
bot = telebot.TeleBot(token)


# Команда /start
@bot.message_handler(commands=["start"])
def start(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  item1 = types.KeyboardButton("Найти блогера по имени")
  item2 = types.KeyboardButton("Найти блогера по ссылке")
  item3 = types.KeyboardButton("Найти блогера по тематике")
  item4 = types.KeyboardButton("Найти блогеров по определённым соц. сетям")
  item5 = types.KeyboardButton("Поиск по определённому виду рекламы")
  item6 = types.KeyboardButton("Поиск по бюджету")
  item7 = types.KeyboardButton("Добавить блогера в бота")
  markup.add(item1)
  markup.add(item2)
  markup.add(item3)
  markup.add(item4)
  markup.add(item5)
  markup.add(item6)
  markup.add(item7)
  img = open('blog-articles.png', 'rb')  # Подтягиваем фотку для приветствия
  bot.send_photo(
      message.chat.id,
      img,
      "Добрый день, {0.first_name}! \n\nЯ - бот для поиска блогеров. На данный момент я в режиме Бета-тестирования. Ожидаемое время запуска - 30.10.2023. Выберите один из вариантов поиска:"
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
    filtered_df = df[df['блогер'].str.contains(blogger_name)]
  
    if not filtered_df.empty:
      # Задаем вопрос о социальных сетях и создаем клавиатуру
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
          "Блогер с именем '{}' найден. Выберите социальные сети, которые вас интересуют:"
          .format(blogger_name),
          reply_markup=markup)
  
    bot.register_next_step_handler(
        message,
        partial(filter_data_by_social_network, filtered_df=filtered_df))
  

# Функция для фильтрации данных по социальной сети
def filter_data_by_social_network(message, filtered_df):
  social_network = message.text

  # Фильтруем данные по выбранной социальной сети
  mask = filtered_df.columns.str.contains(social_network, case=False)
  filtered_df_socnet = filtered_df.loc[:, mask]

  filtered_df_socnet = filtered_df_socnet.rename(
      columns=lambda x: x.replace(f'{social_network} ', ''))

  filtered_df_socnet = filtered_df_socnet.apply(
      lambda x: x.map(lambda x: np.nan if x is None else x))

  # Добавьте кнопки

  keyboard_data_social_network = types.ReplyKeyboardMarkup(
      one_time_keyboard=True)
  item1 = types.KeyboardButton('Вернуться в главное меню')
  item2 = types.KeyboardButton('Найти другие соц.сети блогера')
  keyboard_data_social_network.add(item1)
  keyboard_data_social_network.add(item2)

  for index, row in filtered_df_socnet.iterrows():
    # Проверяем, что текущая строка не пуста
    if not row.isnull().all():
      # Инициализируем сообщение для вывода результатов
      result_message = "🖤 Результаты поиска для социальной сети {}:\n\n".format(
          social_network)

      # Добавляем информацию о блогере в начале каждой строки
      result_message += "<b>Имя блогера</b>: {}\n".format(
          row['блогер'].title())

      # Перебираем столбцы и их значения в текущей строке
      for column, value in row.items():
        # Проверяем, что значение не является NaN и не соответствует столбцу 'тематика'
        if not pd.isna(
            value
        ) and column != 'тематика' and column != 'блогер' and column != 'статистика':
          result_message += "<b>{}</b>: {}\n".format(column.capitalize(),
                                                     value)

      # Добавляем статистику в конец строки
      result_message += "<b>Статистика:</b> {}\n\n".format(row['статистика'])

      # Отправляем результат пользователю
      max_message_length = 4000  # Максимальная длина сообщения в Telegram
      result_message += "\n\n"
      for i in range(0, len(result_message), max_message_length):
        bot.send_message(message.chat.id,
                         result_message[i:i + max_message_length],
                         parse_mode='HTML',
                         reply_markup=keyboard_data_social_network)

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


# Обработчик команды /return
@bot.message_handler(
    func=lambda message: message.text.lower() == "вернуться в главное меню")
@bot.message_handler(commands=["return"])
def return_to_main_menu(message):

  markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                     one_time_keyboard=True)
  item1 = types.KeyboardButton("Найти блогера по имени")
  item2 = types.KeyboardButton("Найти блогера по ссылке")
  item3 = types.KeyboardButton("Найти блогера по тематике")
  item4 = types.KeyboardButton("Поиск блогеров по определённым соц. сетям")
  item5 = types.KeyboardButton("Добавить блогера в бота")
  markup.add(item1)
  markup.add(item2)
  markup.add(item3)
  markup.add(item4)
  markup.add(item5)

  bot.send_message(message.chat.id,
                   "Продолжите пользоваться нашим ботом с помощью кнопок ниже",
                   reply_markup=markup)



keep_alive()  #запускаем flask-сервер в отдельном потоке. Подробнее ниже...
bot.polling(non_stop=True, interval=0)  #запуск бота
