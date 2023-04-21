import os
import logging

import telebot as tb
from dotenv import load_dotenv


def main():
    bot = tb.TeleBot(os.getenv("TOKEN"))

    @bot.message_handler(commands=['start'])
    def sayHi(message: tb.types.Message):
        logger.info(f'username: {message.from_user.username}')
        bot.send_message(message.from_user.id, "Привет! Я бот расписания поиска свободных аудиторий")

    bot.infinity_polling()


def getLogger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()

    formatLogMessage = '%(asctime)s: (%(name)s) - %(levelname)s:\t%(message)s'
    formatter = logging.Formatter(formatLogMessage)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    return logger


if __name__ == "__main__":
    logger = getLogger()
    load_dotenv() # должен быть файл .env, а в нем токен
    main()
