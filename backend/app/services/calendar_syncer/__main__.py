import datetime
import logging
import os

from dateutil.relativedelta import relativedelta

from backend.app.services.calendar_syncer.utils.google_calendar import \
    GoogleCalendar
from backend.app.services.calendar_syncer.utils.moodle_crawler import (
    MoodleCrawler, SubmissionStatusError)


def get_cal_id(calendars, summary):
    for cal in calendars:
        if cal['summary'] == summary:
            return cal['id']
    return None


def get_iso_format_date(date, delta_year=0, delta_month=0, delta_day=0):
    date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    date += relativedelta(years=delta_year, months=delta_month, days=delta_day)

    return date.isoformat() + '+08:00'


def get_color_id(can_submit, submission_status):
    if not can_submit or not submission_status or submission_status == 'unknown':
        return 8    # gray
    elif submission_status == 'not_submitted':
        return 11   # red
    elif submission_status == 'submitted':
        return 2    # green
    else:
        raise SubmissionStatusError('Unexpected submission status: {}'.format(submission_status))


def event_identical(event, assign):
    if event['summary'] != assign['title']:
        return False
    if event['description'] != assign['description']:
        return False
    if event['start']['dateTime'] != assign['deadline']:
        return False
    if event['end']['dateTime'] != assign['deadline']:
        return False
    if event['colorId'] != str(get_color_id(assign['can_submit'], assign['submission_status'])):
        return False
    return True


def main(moodle_session_id=None, token_path=None):
    logging.basicConfig(level=logging.INFO)
    secrets_path = os.path.join('.', 'secrets')

    # login to moodle
    moodle_creds_path = os.path.join(secrets_path, 'moodle_credentials.json')
    web_crawler = MoodleCrawler(session_id=moodle_session_id)
    if moodle_session_id is None:
        web_crawler.login(moodle_creds_path)

    # authenticate google calendar api
    api_creds_path = os.path.join(secrets_path, 'api_credentials.json')
    cal_api = GoogleCalendar(api_creds_path, token_path)
    # get calendar id
    calendars = cal_api.list_calendars()
    cal_id = get_cal_id(calendars, 'Moodle Deadline')
    if cal_id is None:
        cal_id = cal_api.create_calendar('Moodle Deadline', 'Deadline from Moodle')

    # get next k months assignment info
    k = 6
    assign_info = web_crawler.get_next_k_month_assign_info(k)
    cal_events = cal_api.list_events(cal_id, time_min=get_iso_format_date(
        datetime.datetime.now()),
        time_max=get_iso_format_date(
        datetime.datetime.now(),
        delta_month=k))

    logging.info('Found %d assignments.', len(assign_info))

    for assign in assign_info:
        logging.info('Processing assignment %s.', assign)

        color_id = get_color_id(assign['can_submit'], assign['submission_status'])

        # check if the assignment is already in the calendar
        exist = False
        for event in cal_events:
            # if the assignment is already in the calendar
            if event['summary'] == assign['title']:
                exist = True
                # update the event if the event is not identical
                if not event_identical(event, assign):
                    cal_api.update_event(
                        cal_id, event['id'],
                        assign['title'],
                        assign['deadline'],
                        assign['deadline'],
                        assign['description'],
                        color_id=color_id)
                break

        # create the event if the assignment is not in the calendar
        if not exist:
            cal_api.create_event(
                cal_id, assign['title'],
                assign['deadline'],
                assign['deadline'],
                assign['description'],
                color_id=color_id)


if __name__ == '__main__':
    token_path = os.path.join('.', 'secrets', 'token.json')
    main(token_path=token_path)
