import logging


def get_logger(log_level: str) -> logging.Logger:
    """
        Функция настройки логгера
    """
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()

    format_log_message = '%(asctime)s: (%(name)s) - %(levelname)s:\t%(message)s'
    formatter = logging.Formatter(format_log_message)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(log_level)

    return logger
