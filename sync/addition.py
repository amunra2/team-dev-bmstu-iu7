import logging
import os

from codes import ReturnCode

import requests


BRANCHES = ["ИУК", "МК", "K", "ЛТ"]

NUMERATOR = {"name": "(чс)", "value": 0}
DENOMINATOR = {"name": "(зн)", "value": 1}

BUILDINGS = {"": "Главное здание",
             "ю": "Главное здание",
             "л": "Учебно-лабораторный корпус",
             "э": "Корпус 'Энерго'",
             "м": "Корпус 'СМ'"}


def add_data(logger: logging.Logger):
    """
        Функция добавления данных в базу.
    """

    uuids = get_groups_uuids(logger)

    if uuids is None:
        return ReturnCode.fail

    for uuid in uuids:
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
        faculty = get_faculty(group["abbr"])

        if BRANCHES.count(faculty) == 0:
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
        r.raise_for_status()

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

    classroom = get_classroom(schedule_item["aud"])

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

    for symbol in classroom:
        if "0" <= symbol <= "9":
            number += symbol

        if (symbol < "0" or symbol > "9") and number != "":
            number += symbol
            building_abbr += symbol

    if number == "":
        return None

    buildings_abbrs = list(BUILDINGS.keys())

    if building_abbr != "" and buildings_abbrs.count(building_abbr[0]) == 0:
        building_abbr = building_abbr[1:]

    building = get_building_name(building_abbr)

    if building is None:
        return None

    floor = None

    if number[0] == "1" and (number[1] == "0" or number[1] == "1"):
        floor = int(number[:2])
    else:
        floor = int(number[0])

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
        class_id = requests.post(url + + "schedule_classes",
                                 json=schedule_class)

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
