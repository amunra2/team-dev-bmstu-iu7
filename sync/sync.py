import logging

from sync.addition import add_data
from sync.codes import ReturnCode
from sync.deletion import delete_data


def sync_data(logger: logging.Logger):
    """
        Функция синхронизации данных.
    """

    logger.info("Удаление данных...")

    if delete_data(logger) != ReturnCode.ok:
        return
    logger.info("Данные удалены.")

    logger.info("Добавление данных...")

    if add_data(logger) != ReturnCode.ok:
        return
    logger.info("Данные добавлены.")
