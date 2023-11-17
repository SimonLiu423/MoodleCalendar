from utils.google_calendar import GoogleCalendar
from utils.moodle_crawler import *
from dateutil.relativedelta import relativedelta


def get_cal_id(calendars, summary):
    for cal in calendars:
        if cal['summary'] == summary:
            return cal['id']
    return None


def get_iso_format_date(date, delta_year=0, delta_month=0, delta_day=0):
    date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    date += relativedelta(years=delta_year, months=delta_month, days=delta_day)

    return date.isoformat() + '+08:00'


def get_color_id(submission_status):
    if not submission_status or submission_status == 'unknown':
        return 8
    elif submission_status == 'not_submitted':
        return 11
    elif submission_status == 'submitted':
        return 2
    else:
        raise Exception('Unknown submission status')


def event_identical(event, assign):
    if event['summary'] != assign['title']:
        return False
    if event['description'] != assign['description']:
        return False
    if event['start']['dateTime'] != assign['deadline']:
        return False
    if event['end']['dateTime'] != assign['deadline']:
        return False
    if event['colorId'] != str(get_color_id(assign['submission_status'])):
        return False
    return True


def main():
    # load username, password from credentials.json
    with open('secrets/moodle_credentials.json', 'r') as f:
        credentials = json.load(f)
        username = credentials['username']
        password = credentials['password']

    # login to moodle
    web_crawler = MoodleCrawler()
    web_crawler.login(username, password)

    cal_api = GoogleCalendar('secrets/api_credentials.json', 'secrets/token.json')
    # get calendar id
    calendars = cal_api.list_calendars()
    cal_id = get_cal_id(calendars, 'Moodle Deadline')
    if cal_id is None:
        cal_id = cal_api.create_calendar('Moodle Deadline', 'Deadline from Moodle')

    # get next k months assignment info
    k = 6
    assign_info = web_crawler.get_next_k_month_assign_info(k)
    cal_events = cal_api.list_events(cal_id, time_min=get_iso_format_date(datetime.datetime.now()),
                                     time_max=get_iso_format_date(datetime.datetime.now(), delta_month=k))

    for assign in assign_info:
        color_id = get_color_id(assign['submission_status'])

        # check if the assignment is already in the calendar
        exist = False
        for event in cal_events:
            # if the assignment is already in the calendar
            if event['summary'] == assign['title']:
                exist = True
                # update the event if the event is not identical
                if not event_identical(event, assign):
                    cal_api.update_event(cal_id, event['id'], assign['title'], assign['deadline'], assign['deadline'],
                                         assign['description'], color_id=color_id)
                break

        # create the event if the assignment is not in the calendar
        if not exist:
            cal_api.create_event(cal_id, assign['title'], assign['deadline'], assign['deadline'], assign['description'],
                                 color_id=color_id)


if __name__ == '__main__':
    main()
