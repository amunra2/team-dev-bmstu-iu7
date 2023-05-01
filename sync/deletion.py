import logging
import os

from codes import ReturnCode

import requests


def delete_data(logger: logging.Logger):
    """
        Функция удаления данных из базы.
    """

    url = os.getenv("DATA_URL")

    try:
        r = requests.delete(url + "classrooms")
        r.raise_for_status()

        r = requests.delete(url + "classes")
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logging.critical("Неудачный запрос:", errh)
        return ReturnCode.fail
    except requests.exceptions.ConnectionError as errc:
        logging.critical("Ошибка соединения:", errc)
        return ReturnCode.fail
    except requests.exceptions.Timeout as errt:
        logging.critical("Время ожидания ответа истекло:", errt)
        return ReturnCode.fail
    except requests.exceptions.RequestException as err:
        logging.critical("Что-то пошло не так:", err)
        return ReturnCode.fail

    return ReturnCode.ok
