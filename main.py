import json
import logging
import os

from dotenv import load_dotenv

import telebot as tb


class TelegramBotEmptyAudienceBMSTU:
    def __init__(self, bot_messages_json: dict):
        self.bot = tb.TeleBot(os.getenv("TOKEN"))
        self.bot_messages = bot_messages_json

        @self.bot.message_handler(commands=['start'])
        def init_command_handler(message: tb.types.Message):
            self.init_command_process(message)

        # @self.bot.message_handler(content_types=['text'])
        # def work(message: tb.types.Message):

    def init_command_process(self, message: tb.types.Message):
        self.bot.send_message(message.from_user.id, self.bot_messages["HI"])

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


def get_messages_from_json():
    try:
        with open(os.getenv("MESSAGES_FILE_PATH"), 'r') as messages_file:
            bot_messages_json: dict = json.load(messages_file)
    except FileNotFoundError:
        logger.critical('Неверно указан путь до файла' +
                        f'с сообщениями бота: {os.getenv("MESSAGES_FILE_PATH")}')
        return None
    except json.decoder.JSONDecodeError:
        logger.critical('Файл с сообщениями бота поврежден')
        return None
    except Exception as exception:
        logger.critical(str(exception))
        return None

    return bot_messages_json


if __name__ == "__main__":
    load_dotenv()  # должен быть файл .env, смотреть .env.example
    logger = get_logger(os.getenv("LOG_LEVEL"))
    bot_messages_json = get_messages_from_json()

    if (bot_messages_json is not None):
        bot = TelegramBotEmptyAudienceBMSTU(bot_messages_json)
        bot.run()
