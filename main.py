import logging
import os

from dotenv import load_dotenv

import telebot as tb


class TelegramBotEmptyAudienceBMSTU:
    def __init__(self):
        self.bot = tb.TeleBot(os.getenv("TOKEN"))

        @self.bot.message_handler(commands=['start'])
        def init_command_handler(message: tb.types.Message):
            self.init_command_process(message)

    def init_command_process(self, message: tb.types.Message):
        self.bot.send_message(message.from_user.id,
                              "Привет! Я бот поиска свободных аудиторий в Бауманке")

    def run(self):
        self.bot.infinity_polling()


def get_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()

    format_log_message = '%(asctime)s: (%(name)s) - %(levelname)s:\t%(message)s'
    formatter = logging.Formatter(format_log_message)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger


if __name__ == "__main__":
    logger = get_logger()
    load_dotenv()  # должен быть файл .env, а в нем токен
    bot = TelegramBotEmptyAudienceBMSTU()
    bot.run()
