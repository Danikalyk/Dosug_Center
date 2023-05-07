import psycopg2
import telebot
from telebot import types

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(database="dosug_center", user="postgres", password="*********", host="127.0.0.1", port="5433")
cursor = conn.cursor()

# Создание таблицы расписания курсов
cursor.execute('''CREATE TABLE IF NOT EXISTS courses 
                (id SERIAL PRIMARY KEY,
                course_name TEXT,
                day_of_week TEXT,
                time TEXT)''')

# Создание таблицы расписания секций
cursor.execute('''CREATE TABLE IF NOT EXISTS sections 
                (id SERIAL PRIMARY KEY,
                section_name TEXT,
                day_of_week TEXT,
                time TEXT)''')

# Создание таблицы мероприятий
cursor.execute('''CREATE TABLE IF NOT EXISTS events 
                (id SERIAL PRIMARY KEY,
                event_name TEXT,
                date TEXT,
                time TEXT)''')

# Инициализация телеграм бота
bot = telebot.TeleBot('*****************************')

# Обработчик команды start
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()
    course_button = types.InlineKeyboardButton(text='Расписание курсов', callback_data='course')
    section_button = types.InlineKeyboardButton(text='Расписание секций', callback_data='section')
    events_button = types.InlineKeyboardButton(text='Мероприятия', callback_data='events')
    keyboard.row(course_button, section_button)
    keyboard.row(events_button)
    bot.send_message(chat_id=message.chat.id, text='Выберите:', reply_markup=keyboard)

# Обработчик inline кнопок
@bot.callback_query_handler(func=lambda call: True)
def button(call):
    if call.data == 'section':
        cursor.execute('select sections.section_name, section_schedule.week_day, section_schedule.section_time from sections, section_schedule where section_schedule.section_code = sections.section_number')
        data = cursor.fetchall()
        message = '\n'.join([f"{item[0]}\n{item[1]}/{item[2]}\n" for item in data])
        bot.send_message(chat_id=call.message.chat.id, text=message)
        bot.answer_callback_query(callback_query_id=call.id)

    elif call.data == 'course':
        cursor.execute('select courses.course_name, course_schedule.week_day, course_schedule.course_time from courses, course_schedule where course_schedule.course = courses.course_number')
        data = cursor.fetchall()
        message = '\n'.join([f"{item[0]}\n{item[1]}/{item[2]}\n" for item in data])
        bot.send_message(chat_id=call.message.chat.id, text=message)
        bot.answer_callback_query(callback_query_id=call.id)

    elif call.data == 'events':
        cursor.execute('select events.event_name, event_schedule.event_date_time from events, event_schedule where event_schedule.event_code = events.event_number')
        data = cursor.fetchall()
        message = '\n'.join([f"{item[0]}/{item[1]}\n" for item in data])
        bot.send_message(chat_id=call.message.chat.id, text=message)
        bot.answer_callback_query(callback_query_id=call.id)

# Запуск телеграм бота
bot.polling()
