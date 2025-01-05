import json
import logging


def get_data_from_json(logger: logging.Logger, file_path: str):
    """
        Функция парсит JSON файл с данными и переводит это в словарь dict
    """
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
