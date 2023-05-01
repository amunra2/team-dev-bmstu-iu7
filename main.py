import logging
import os
from threading import Thread

from dotenv import load_dotenv

import requests

import schedule

from sync.sync import sync_data

import telebot as tb
import telebot.types as tbt

from utils.get_full_lesson_data import get_full_lesson_data
from utils.get_json_data import get_data_from_json
from utils.get_logger import get_logger

PARSE_MODE = 'MarkdownV2'
KEY = 0
VALUE = 1


class TelegramBotEmptyAudienceBMSTU:
    def __init__(self, bot_messages_json: dict, buildings_json: dict,
                 lessons_json: dict, levels_json: dict):
        self.bot = tb.TeleBot(os.getenv("TOKEN"))

        self.bot_messages = bot_messages_json
        self.buildings = buildings_json
        self.lessons = lessons_json
        self.levels = levels_json

        # key - USER_ID, data - user data
        self.data_users: dict = {}

        @self.bot.message_handler(commands=['start', 'help'])
        def init_command_handler(message: tbt.Message):
            """
                Перехватывает команды /start и /help.
                Отправляет общую информацию по работе с ботом.
            """
            self.init_command_process(message)

        @self.bot.message_handler(commands=['find_empty'])
        def find_empty_audience_handler(message: tbt.Message):
            """
                Перехватывает команду поиска свободной аудитории /find_empty.
                Инициализирует запись о пользователе в массиве data_users.
                Вызывает функцию выбора корпуса.
            """
            user_id = message.from_user.id
            self.data_users.update({user_id: {"MODE": "FIND_EMPTY_AUDIENCE"}})

            self.select_building(self.data_users[user_id]["MODE"], user_id)

        @self.bot.message_handler(commands=['is_empty'])
        def is_empty_audience_handler(message: tbt.Message):
            """
                Перехватывает команду проверки "свободности" аудитории /is_empty.
                Инициализирует запись о пользователе в массиве data_users.
                Вызывает функцию выбора корпуса.
            """
            user_id = message.from_user.id
            self.data_users.update({user_id: {"MODE": "IS_EMPTY_AUDIENCE"}})

            self.select_building(self.data_users[user_id]["MODE"], user_id)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("BUILDING"))
        def save_building_handler(call: tbt.CallbackQuery):
            """
                Перехватывает нажатие inline-клавиатуры выбора корпуса по значению,
                начинающееся с ключевого слова "BUILDING".

                Сохраняет данные о выбранном корпусе.
                Вызывает функцию выбора пары.
            """
            user_id = call.message.chat.id
            self.delete_stage_messages(user_id, [call.message.message_id])

            if (self.is_user_comebacked(user_id, "BUILDING")):
                return

            data_string = call.data.split(":")
            self.data_users[user_id].update({data_string[KEY]: data_string[VALUE]})

            self.select_lesson(self.data_users[user_id]["MODE"], user_id)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("LESSON"))
        def save_lesson_handler(call: tbt.CallbackQuery):
            """
                Перехватывает нажатие inline-клавиатуры выбора пары по значению,
                начинающееся с ключевого слова "LESSON".

                Сохраняет данные о выбранной паре.
                Вызывает функцию выбора этажа (для поиска свободной аудитории) или
                функцию ввода аудитории (для определения "свободности" аудитории).
            """
            user_id = call.message.chat.id
            self.delete_stage_messages(user_id, [call.message.message_id])

            if (self.is_user_comebacked(user_id, "LESSON")):
                return

            data_string = call.data.split(":")
            lesson = get_full_lesson_data(data_string[VALUE])
            self.data_users[user_id].update({data_string[KEY]: lesson})

            if (self.data_users[user_id]["MODE"] == "FIND_EMPTY_AUDIENCE"):
                self.select_level(self.data_users[user_id]["MODE"], user_id)
            else:
                self.select_audience(call.message, self.data_users[user_id]["MODE"])

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("LEVEL"))
        def save_level_handler(call: tbt.CallbackQuery):
            """
                Перехватывает нажатие inline-клавиатуры выбора пары по значению,
                начинающееся с ключевого слова "LESSON".

                Сохраняет данные о выбранной паре.
                Вызывает функцию выбора этажа (для поиска свободной аудитории) или
                функцию ввода аудитории (для определения "свободности" аудитории).
            """
            user_id = call.message.chat.id
            self.delete_stage_messages(user_id, [call.message.message_id])

            if (self.is_user_comebacked(user_id, "LEVEL")):
                return

            data_string = call.data.split(":")
            self.data_users[user_id].update({data_string[KEY]: data_string[VALUE]})

            if (logger.level <= logging.INFO):
                items = self.data_users[user_id].items()
                string = "{\n" + \
                         "".join([f'  {key}: {value},\n' for key, value in items]) + \
                         "}"
                logger.info(string.replace("\n", "").replace("  ", " "))

                mode = self.data_users[user_id]['MODE']
                self.bot.send_message(user_id,
                                      f"{self.bot_messages[mode]} `{string}`",
                                      parse_mode=PARSE_MODE)

            self.show_empty_audiences(self.data_users[user_id], user_id)
            self.data_users.pop(user_id)

        @self.bot.message_handler(func=lambda message: True,
                                  content_types=['audio', 'photo', 'voice', 'video',
                                                 'document', 'text', 'location',
                                                 'contact', 'sticker'])
        def default_command_handler(message):
            """
                Перехватывает все необрабатываемое.
                Выводит общую информацию по боту.
            """
            self.init_command_process(message)

        logger.info("Бот запущен")

    def show_empty_audiences(self, user_data: dict, user_id: int):
        """
            Функция выводит результат поиска свободных аудиторий.
            Информация получается через запрос в БД.
        """
        try:
            request_params = {"building": user_data["BUILDING"],
                              "floor": user_data["LEVEL"],
                              "class": user_data["LESSON"]}

            url = os.getenv("DATA_URL") + "classrooms"
            response = requests.get(url, params=request_params)

            if (response.status_code != 200):
                raise Exception(f"Request status code {response.status_code}: {response.reason}")

            free_audiences = response.json()
            free_audiences_str = ""

            if (not free_audiences):
                message = bot_messages_json[user_data['MODE']] + \
                          bot_messages_json['EMPTY_AUDIENCES_NOT_FOUND']
            else:
                for audience in free_audiences:
                    free_audiences_str += f"\n \\- `{audience['number']}`"

                message = bot_messages_json[user_data['MODE']] + \
                    bot_messages_json['EMPTY_AUDIENCES_FOUND'] + \
                    free_audiences_str

            self.bot.send_message(user_id, message, parse_mode=PARSE_MODE)
        except Exception as exception:
            logger.warning(exception)
            self.bot.send_message(user_id,
                                  self.bot_messages[user_data['MODE']] +
                                  self.bot_messages["FIND_EMPTY_FAILED"],
                                  parse_mode=PARSE_MODE)

    def show_is_empty_audience(self, user_data: dict, user_id: int):
        """
            Функция выводит результат проверки "свободности" аудитории.
            Информация получается через запрос в БД.
        """
        try:
            request_params = {"is_free": "true",
                              "building": user_data["BUILDING"],
                              "class": user_data["LESSON"],
                              "number": user_data["AUDIENCE"]}

            url = os.getenv("DATA_URL") + "classrooms"
            response = requests.get(url, params=request_params)

            if (response.status_code != 200):
                raise Exception(f"Request status code {response.status_code}: {response.reason}")

            result: dict = response.json()

            if (result['is_free']):
                message = bot_messages_json[user_data['MODE']] + \
                          bot_messages_json['IS_EMPTY_YES']
            else:
                message = bot_messages_json[user_data['MODE']] + \
                          bot_messages_json['IS_EMPTY_NO']

            self.bot.send_message(user_id, message, parse_mode=PARSE_MODE)
        except Exception as exception:
            logger.warning(exception)
            self.bot.send_message(user_id,
                                  self.bot_messages[user_data['MODE']] +
                                  self.bot_messages["FIND_EMPTY_FAILED"],
                                  parse_mode=PARSE_MODE)

    def is_user_comebacked(self, user_id: int, stage: str):
        """
            Функция проверяет:
            1) Есть ли запись о пользователе (запрещено работать не с первого этапа команды)
            2) Ввел ли уже пользователь данные по этапу stage (запрещается вводить заново)
        """
        error = False
        if (self.data_users.get(user_id) is None):
            error = True
        elif (self.data_users[user_id].get(stage) is not None):
            error = True

        if (error):
            self.bot.send_message(user_id,
                                  self.bot_messages["CHOOSE_FAIL"],
                                  parse_mode=PARSE_MODE)

        return error

    def select_building(self, command_text: str, user_id: int):
        """
            Функция выводит inline-клавиатуру для выбора корпуса
        """
        keyboard = tbt.InlineKeyboardMarkup()

        for key, value in self.buildings.items():
            button = tbt.InlineKeyboardButton(text=value,
                                              callback_data=f"BUILDING:{key}")
            keyboard.add(button)

        self.bot.send_message(user_id,
                              self.bot_messages[command_text] +
                              self.bot_messages["CHOOSE_BUILDING"],
                              parse_mode=PARSE_MODE,
                              reply_markup=keyboard)

    def select_lesson(self, command_text: str, user_id: int):
        """
            Функция выводит inline-клавиатуру для выбора пары
        """
        keyboard = tbt.InlineKeyboardMarkup()

        for key, value in self.lessons.items():
            button = tbt.InlineKeyboardButton(text=value,
                                              callback_data=f"LESSON:{key}")
            keyboard.add(button)

        self.bot.send_message(user_id,
                              self.bot_messages[command_text] +
                              self.bot_messages["CHOOSE_LESSON"],
                              parse_mode=PARSE_MODE,
                              reply_markup=keyboard)

    def select_level(self, command_text: str, user_id: int):
        """
            Функция выводит inline-клавиатуру для выбора этажа
        """
        keyboard = tbt.InlineKeyboardMarkup()
        levels_num = self.levels[self.data_users[user_id]["BUILDING"]]

        for level_num in range(levels_num):
            button = tbt.InlineKeyboardButton(text=f"Этаж {level_num + 1}",
                                              callback_data=f"LEVEL:{level_num + 1}")
            keyboard.add(button)

        self.bot.send_message(user_id,
                              self.bot_messages[command_text] +
                              self.bot_messages["CHOOSE_LEVEL"],
                              parse_mode=PARSE_MODE,
                              reply_markup=keyboard)

    def select_audience(self, message: tbt.Message, command_text: str, error: str = ""):
        """
            Функция просит пользователя ввести номер аудитории в определенном формате
        """
        message = self.bot.send_message(message.chat.id,
                                        self.bot_messages[command_text] +
                                        error +
                                        self.bot_messages['CHOOSE_AUDIENCE'],
                                        parse_mode=PARSE_MODE)

        self.bot.register_next_step_handler(message,
                                            self.save_audience,
                                            message_id_to_delete=message.message_id,
                                            command_text=command_text)

    def save_audience(self, message: tbt.Message, message_id_to_delete: int, command_text: str):
        """
            Функция сохраняет информацию о введеном номере аудитории
        """
        user_id = message.chat.id
        self.delete_stage_messages(user_id, [message_id_to_delete, message.message_id])

        if (self.is_user_comebacked(user_id, "AUDIENCE")):
            return

        self.data_users[user_id].update({"AUDIENCE": message.text})

        if (logger.level <= logging.INFO):
            items = self.data_users[user_id].items()
            string = "{\n" + \
                     "".join([f'  {key}: {value},\n' for key, value in items]) + \
                     "}"
            logger.info(string.replace("\n", "").replace("  ", " "))

            mode = self.data_users[user_id]['MODE']
            self.bot.send_message(user_id,
                                  f"{self.bot_messages[mode]} `{string}`",
                                  parse_mode=PARSE_MODE)

        self.show_is_empty_audience(self.data_users[user_id], user_id)
        self.data_users.pop(user_id)

    def delete_stage_messages(self, chat_id: int, message_ids: list[int]):
        """
            Удаляет сообщения стадии ввода
        """
        for message_id in message_ids:
            self.bot.delete_message(chat_id, message_id)

    def init_command_process(self, message: tbt.Message):
        """
            Функция выводит общую информацию по боту
        """
        self.bot.send_message(message.from_user.id,
                              self.bot_messages["HI"] +
                              self.bot_messages["COMMAND_FIND_EMPTY"] +
                              self.bot_messages["COMMAND_IS_EMPTY"],
                              parse_mode=PARSE_MODE)

    def run(self):
        """
            Запускает цикл работы бота и синхронизацию данных БД
        """
        Thread(target=schedule_checker).start()
        schedule.every().monday.do(sync_data)
        self.bot.infinity_polling()


def schedule_checker():
    while True:
        schedule.run_pending()


if __name__ == "__main__":
    """
        Запуск
    """
    load_dotenv()  # должен быть файл .env, смотреть .env.example
    logger = get_logger(os.getenv("LOG_LEVEL"))

    bot_messages_json = get_data_from_json(logger, os.getenv("MESSAGES_FILE_PATH"))
    buildings_json = get_data_from_json(logger, os.getenv("BUILDINGS_FILE_PATH"))
    lessons_json = get_data_from_json(logger, os.getenv("LESSONS_FILE_PATH"))
    levels_json = get_data_from_json(logger, os.getenv("LEVELS_FILE_PATH"))

    if ((bot_messages_json is not None) and
            (buildings_json is not None) and
            (lessons_json is not None) and
            (levels_json is not None)):
        bot = TelegramBotEmptyAudienceBMSTU(bot_messages_json,
                                            buildings_json,
                                            lessons_json,
                                            levels_json)
        bot.run()
