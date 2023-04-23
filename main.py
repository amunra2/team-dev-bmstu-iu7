import json
import logging
import os

from dotenv import load_dotenv

import telebot as tb
import telebot.types as tbt

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
            self.init_command_process(message)

        @self.bot.message_handler(commands=['find_empty'])
        def find_empty_audience_handler(message: tbt.Message):
            user_id = message.from_user.id
            self.data_users.update({user_id: {"MODE": "FIND_EMPTY_AUDIENCE"}})

            self.select_building(self.data_users[user_id]["MODE"], user_id)

        @self.bot.message_handler(commands=['is_empty'])
        def is_empty_audience_handler(message: tbt.Message):
            user_id = message.from_user.id
            self.data_users.update({user_id: {"MODE": "IS_EMPTY_AUDIENCE"}})

            self.select_building(self.data_users[user_id]["MODE"], user_id)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("BUILDING"))
        def save_building_handler(call: tbt.CallbackQuery):
            user_id = call.message.chat.id

            if (self.is_user_comebacked(user_id, "BUILDING")):
                return

            data_string = call.data.split(":")
            self.data_users[user_id].update({data_string[KEY]: data_string[VALUE]})

            self.select_lesson(self.data_users[user_id]["MODE"], user_id)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("LESSON"))
        def save_lesson_handler(call: tbt.CallbackQuery):
            user_id = call.message.chat.id

            if (self.is_user_comebacked(user_id, "LESSON")):
                return

            data_string = call.data.split(":")
            self.data_users[user_id].update({data_string[KEY]: data_string[VALUE]})

            if (self.data_users[user_id]["MODE"] == "FIND_EMPTY_AUDIENCE"):
                self.select_level(self.data_users[user_id]["MODE"], user_id)
            else:
                self.select_audience(call, self.data_users[user_id]["MODE"])

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("LEVEL"))
        def save_level_handler(call: tbt.CallbackQuery):
            user_id = call.message.chat.id

            if (self.is_user_comebacked(user_id, "LEVEL")):
                return

            data_string = call.data.split(":")
            self.data_users[user_id].update({data_string[KEY]: data_string[VALUE]})

            string = "{\n" + \
                     "".join([f'  {key}: {value},\n' for key,value in self.data_users[user_id].items()]) + \
                     "}"
            logger.info(string.replace("\n", "").replace("  ", " "))

            print(self.data_users)

            self.bot.send_message(user_id,
                              f"{self.bot_messages[self.data_users[user_id]['MODE']]} `{string}`",
                              parse_mode=PARSE_MODE)
            self.data_users.pop(user_id)
            print(self.data_users)
            
        logger.info("Бот запущен!")


    def is_user_comebacked(self, user_id: int, stage: str):
        if (self.data_users.get(user_id) is None):
            self.bot.send_message(user_id,
                                  self.bot_messages["CHOOSE_FAIL"],
                                  parse_mode=PARSE_MODE)
            return True
        elif (self.data_users[user_id].get(stage) is not None):
            self.bot.send_message(user_id,
                                    self.bot_messages["CHOOSE_FAIL"],
                                    parse_mode=PARSE_MODE)
            return True
        return False


    def select_building(self, command_text: str, user_id: int):
        keyboard = tbt.InlineKeyboardMarkup();
    
        for key,value in self.buildings.items():
            button = tbt.InlineKeyboardButton(text=value,
                                              callback_data=f"BUILDING:{key}")
            keyboard.add(button)

        self.bot.send_message(user_id,
                              self.bot_messages[command_text] +
                              self.bot_messages["CHOOSE_BUILDING"],
                              parse_mode=PARSE_MODE,
                              reply_markup=keyboard)

        
    def select_lesson(self, command_text: str, user_id: int):
        keyboard = tbt.InlineKeyboardMarkup();
    
        for key,value in self.lessons.items():
            button = tbt.InlineKeyboardButton(text=value,
                                              callback_data=f"LESSON:{key}")
            keyboard.add(button)

        self.bot.send_message(user_id,
                              self.bot_messages[command_text] +
                              self.bot_messages["CHOOSE_LESSON"],
                              parse_mode=PARSE_MODE,
                              reply_markup=keyboard)
        
    
    def select_level(self, command_text: str, user_id: int):
        keyboard = tbt.InlineKeyboardMarkup();
        levelsNum = self.levels[self.data_users[user_id]["BUILDING"]]
    
        for levelNum in range(levelsNum):
            button = tbt.InlineKeyboardButton(text=f"Этаж {levelNum + 1}",
                                              callback_data=f"LEVEL:{levelNum + 1}")
            keyboard.add(button)

        self.bot.send_message(user_id,
                              self.bot_messages[command_text] +
                              self.bot_messages["CHOOSE_LEVEL"],
                              parse_mode=PARSE_MODE,
                              reply_markup=keyboard)
        

    def select_audience(self, call: tbt.CallbackQuery, command_text: str):
        self.bot.send_message(call.message.chat.id,
                              self.bot_messages[command_text] +
                              self.bot_messages["CHOOSE_AUDIENCE"],
                              parse_mode=PARSE_MODE)
        
        self.bot.register_next_step_handler(call.message, self.save_audience)


    def save_audience(self, message: tbt.Message):
        user_id = message.chat.id
        if (self.is_user_comebacked(user_id, "AUDIENCE")): return
        
        self.data_users[user_id].update({"AUDIENCE": message.text})

        string = "{\n" + \
                 "".join([f'  {key}: {value},\n' for key,value in self.data_users[user_id].items()]) + \
                 "}"
        logger.info(string.replace("\n", "").replace("  ", " "))

        print(self.data_users)
        
        self.bot.send_message(user_id,
                              f"{self.bot_messages[self.data_users[user_id]['MODE']]} `{string}`",
                              parse_mode=PARSE_MODE)


    def init_command_process(self, message: tbt.Message):
        self.bot.send_message(message.from_user.id,
                              self.bot_messages["HI"] +
                              self.bot_messages["COMMAND_FIND_EMPTY"] +
                              self.bot_messages["COMMAND_IS_EMPTY"],
                              parse_mode=PARSE_MODE)

    def run(self):
        self.bot.infinity_polling()


def get_logger(log_level: str) -> logging.Logger:
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()

    format_log_message = '%(asctime)s: (%(name)s) - %(levelname)s:\t%(message)s'
    formatter = logging.Formatter(format_log_message)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(log_level)

    return logger


def get_data_from_json(file_path: str):
    try:
        with open(file_path, 'r') as file:
            data_json: dict = json.load(file)
    except FileNotFoundError:
        logger.critical(f'Неверно указан путь до файла {file_path}')
        return None
    except json.decoder.JSONDecodeError:
        logger.critical('Файл поврежден')
        return None
    except Exception as exception:
        logger.critical(str(exception))
        return None

    return data_json


if __name__ == "__main__":
    load_dotenv()  # должен быть файл .env, смотреть .env.example
    logger = get_logger(os.getenv("LOG_LEVEL"))
    bot_messages_json = get_data_from_json(os.getenv("MESSAGES_FILE_PATH"))
    buildings_json = get_data_from_json(os.getenv("BUILDINGS_FILE_PATH"))
    lessons_json = get_data_from_json(os.getenv("LESSONS_FILE_PATH"))
    levels_json = get_data_from_json(os.getenv("LEVELS_FILE_PATH"))

    if ((bot_messages_json is not None) and
        (buildings_json is not None) and
        (lessons_json is not None) and
        (levels_json is not None)):
        bot = TelegramBotEmptyAudienceBMSTU(bot_messages_json,
                                            buildings_json,
                                            lessons_json,
                                            levels_json)
        bot.run()
