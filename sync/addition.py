import logging
import os

import requests

from sync.codes import ReturnCode


NOT_HANDLED = ["МТ6-81"]
BRANCHES = ["ИУК", "МК", "K", "ЛТ"]

NUMERATOR = {"name": "(чс)", "value": 0}
DENOMINATOR = {"name": "(зн)", "value": 1}

MIN_FLOOR_LEN = 3
MAX_FLOOR_LEN = 4
BUILDINGS = {"": "GZ",
             "ю": "GZ",
             "л": "ULK",
             "э": "ENERGO",
             "м": "SM"}


def add_data(logger: logging.Logger):
    """
        Функция добавления данных в базу.
    """

    uuids = get_groups_uuids(logger)

    if uuids is None:
        return ReturnCode.fail

    uuids_len = len(uuids)

    for i, uuid in enumerate(uuids):
        if (logger.level <= logging.INFO):
            print(f"{uuid} ({i+1}/{uuids_len})")

        schedule = get_group_schedule(logger, uuid)

        if schedule is None:
            return ReturnCode.fail

        for schedule_item in schedule:
            parse_schedule_item(logger, schedule_item)

    return ReturnCode.ok


def get_groups_uuids(logger: logging.Logger):
    """
        Функция получения uuid групп.
    """

    url = os.getenv("BASE_URL") + os.getenv("GROUPS")
    auth = {"Authorization": "Bearer " + os.getenv("BEARER_TOKEN")}

    try:
        r = requests.get(url, headers=auth)
        r.raise_for_status()

        groups = r.json()
    except requests.exceptions.HTTPError as errh:
        logging.critical("Неудачный запрос:", errh)
        return None
    except requests.exceptions.ConnectionError as errc:
        logging.critical("Ошибка соединения:", errc)
        return None
    except requests.exceptions.Timeout as errt:
        logging.critical("Время ожидания ответа истекло:", errt)
        return None
    except requests.exceptions.JSONDecodeError as errd:
        logging.critical("Ошибка декодирования:", errd)
        return None
    except requests.exceptions.RequestException as err:
        logging.critical("Что-то пошло не так:", err)
        return None

    uuids = []

    for group in groups:
        if group["abbr"] not in NOT_HANDLED:
            faculty = get_faculty(group["abbr"])

            if faculty not in BRANCHES:
                uuids.append(group["uuid"])

    return uuids


def get_faculty(group_abbr):
    """
        Функция получения факультета группы.
    """

    department = group_abbr.split("-")[0]

    i = 0

    while i < len(department) and (department[i] < "0" or department[i] > "9"):
        i += 1

    return department[:i]


def get_group_schedule(logger: logging.Logger, group_uuid):
    """
        Функция получения расписания группы.
    """

    url = os.getenv("BASE_URL") + group_uuid
    auth = {"Authorization": "Bearer " + os.getenv("BEARER_TOKEN")}

    try:
        r = requests.get(url, headers=auth)
        schedule = r.json()
    except requests.exceptions.HTTPError as errh:
        logging.critical("Неудачный запрос:", errh)
        return None
    except requests.exceptions.ConnectionError as errc:
        logging.critical("Ошибка соединения:", errc)
        return None
    except requests.exceptions.Timeout as errt:
        logging.critical("Время ожидания ответа истекло:", errt)
        return None
    except requests.exceptions.JSONDecodeError as errd:
        logging.critical("Ошибка декодирования:", errd)
        return None
    except requests.exceptions.RequestException as err:
        logging.critical("Что-то пошло не так:", err)
        return None

    return schedule


def parse_schedule_item(logger: logging.Logger, schedule_item):
    """
        Функция парсинга пары.
    """

    if len(schedule_item["aud"]) == 0:
        return ReturnCode.ok

    for room in schedule_item["aud"]:
        classroom = get_classroom(room)

        if classroom is None:
            return ReturnCode.ok

        if schedule_item["term"] == NUMERATOR["name"] or \
           schedule_item["term"] == "":
            schedule_class = {"week": NUMERATOR["value"],
                              "day": schedule_item["wday"],
                              "time": schedule_item["time"][0]}

            if add_entities(logger, classroom, schedule_class) != ReturnCode.ok:
                return ReturnCode.fail

        if schedule_item["term"] == DENOMINATOR["name"] or \
           schedule_item["term"] == "":
            schedule_class = {"week": DENOMINATOR["value"],
                              "day": schedule_item["wday"],
                              "time": schedule_item["time"][0]}

            if add_entities(logger, classroom, schedule_class) != ReturnCode.ok:
                return ReturnCode.fail


def get_classroom(classroom):
    """
        Функция получения сущности аудитории.
    """

    building_abbr = ""
    number = ""
    length = 0

    for symbol in classroom:
        if "0" <= symbol <= "9":
            number += symbol
            length += 1

        if (symbol < "0" or symbol > "9") and number != "":
            number += symbol
            building_abbr += symbol

    if number == "" or ("." in number):
        return None

    buildings_abbrs = list(BUILDINGS.keys())

    if building_abbr != "" and (building_abbr[0] not in buildings_abbrs):
        building_abbr = building_abbr[1:]

    building = get_building_name(building_abbr)

    if building is None:
        return None

    floor = None

    if length == MAX_FLOOR_LEN:
        floor = int(number[:2])
    elif length == MIN_FLOOR_LEN:
        floor = int(number[0])
    else:
        return None

    return {"building": building,
            "floor": floor,
            "number": number}


def get_building_name(building_abbr):
    """
        Функция получения названия корпуса.
    """

    for key in BUILDINGS.keys():
        if building_abbr == key:
            return BUILDINGS[key]

    return None


def add_entities(logger: logging.Logger, classroom, schedule_class):
    """
        Функция добавления сущностей в базу.
    """

    url = os.getenv("DATA_URL")

    try:
        classroom_id = requests.post(url + "classrooms", json=classroom)
        class_id = requests.post(url + "classes", json=schedule_class)

        state = {"classroom_id": classroom_id,
                 "class_id": class_id}
        requests.post(url + "states", state)
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
