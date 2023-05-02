import os
import sqlite3 as sl


DB_NAME = "test.db"
CLASSES = "classes"
CLASSROOMS = "classrooms"
STATES = "states"


def select_count_sql(table):
    return f"select count(*) from sqlite_master where type='table' and name='{table}'"


def create_classes_table(cursor):
    count_sql = select_count_sql(CLASSES)
    count_table = cursor.execute(count_sql)

    for row in count_table:
        if row[0] == 0:
            cursor.execute("""
                   CREATE TABLE classes (
                       class_id INTEGER PRIMARY KEY,
                       week INTEGER,
                       day INTEGER,
                       time INTEGER
                    );
             """)

    insert_sql = f"INSERT INTO {CLASSES} (class_id, week, day, time) values(?, ?, ?, ?)"
    data = [
        (1, 0, 0, 0),
        (2, 0, 0, 1),
        (3, 0, 0, 2),
    ]

    cursor.executemany(insert_sql, data)

    select_sql = f"SELECT * FROM {CLASSES}"
    data = cursor.execute(select_sql)

    for row in data:
        print(row)


def create_classrooms_table(cursor):
    count_sql = select_count_sql(CLASSROOMS)
    count_table = cursor.execute(count_sql)

    for row in count_table:
        if row[0] == 0:
            cursor.execute("""
                   CREATE TABLE classrooms (
                       classroom_id INTEGER PRIMARY KEY,
                       building TEXT,
                       floor INTEGER,
                       number TEXT
                    );
             """)

    insert_sql = \
        f"INSERT INTO {CLASSROOMS} (classroom_id, building, floor, number) values(?, ?, ?, ?)"
    data = [
        (1, "GZ", 3, "305ю"),
        (2, "ULK", 5, "511л"),
        (3, "SM", 4, "405м"),
    ]

    cursor.executemany(insert_sql, data)

    select_sql = f"SELECT * FROM {CLASSROOMS}"
    data = cursor.execute(select_sql)

    for row in data:
        print(row)


def create_states_table(cursor):
    count_sql = select_count_sql(STATES)
    count_table = cursor.execute(count_sql)

    for row in count_table:
        if row[0] == 0:
            cursor.execute("""
                   CREATE TABLE states (
                       state_id INTEGER PRIMARY KEY,
                       classroom_id INTEGER,
                       class_id INTEGER,
                       state BOOLEAN
                    );
             """)

    insert_sql = \
        f"INSERT INTO {STATES} (state_id, classroom_id, class_id, state) values(?, ?, ?, ?)"
    data = [
        (1, 1, 1, False),
        (2, 2, 2, False),
        (3, 3, 3, False),
    ]

    cursor.executemany(insert_sql, data)

    select_sql = f"SELECT * FROM {STATES}"
    data = cursor.execute(select_sql)

    for row in data:
        print(row)


def create_test_db(db):
    con = sl.connect(db)
    cursor = con.cursor()

    create_classes_table(cursor)
    con.commit()

    create_classrooms_table(cursor)
    con.commit()

    create_states_table(cursor)
    con.commit()


if __name__ == "__main__":
    os.remove(DB_NAME)
    create_test_db(DB_NAME)
