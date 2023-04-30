from datetime import datetime

FEBRUARY = 2
MAY = 5
SEPTEMBER = 9
DECEMBER = 12
SEMESTER_1_START_DAY = 1
SEMESTER_2_START_DAY = 6
CHISLITEL = 0
ZNAMENATEL = 1
NO_SEMESTER = -1
DAYS_IN_WEEK = 7


def get_study_week():
    today = datetime.now()

    if (FEBRUARY <= today.month <= MAY):
        semester_start_date = datetime(today.year, FEBRUARY, SEMESTER_2_START_DAY)
    elif (SEPTEMBER <= today.month <= DECEMBER):
        semester_start_date = datetime(today.year, SEPTEMBER, SEMESTER_1_START_DAY)
    else:
        return NO_SEMESTER
    
    today_day_of_year = today.timetuple().tm_yday
    semester_start_date_day_of_year = semester_start_date.timetuple().tm_yday
    
    week = int(((today_day_of_year - semester_start_date_day_of_year) / DAYS_IN_WEEK) + 1)
    
    if (week % 2 == 1):
        return CHISLITEL
    else:
        return ZNAMENATEL


# return: STUDY_WEEK,DAY,LESSON
def get_full_lesson_data(lesson: int):
    study_week = get_study_week()

    if (study_week == NO_SEMESTER):
        study_week = -1
    
    day = datetime.now().weekday()

    return f"{study_week},{day},{lesson}"
