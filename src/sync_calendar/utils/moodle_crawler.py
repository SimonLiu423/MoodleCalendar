import bs4
import requests
import re
import json
import datetime


class MoodleCrawlerError(Exception):
    pass


class SubmissionNotFoundError(MoodleCrawlerError):
    pass


class SubmissionStatusError(MoodleCrawlerError):
    pass


class DueDateError(MoodleCrawlerError):
    pass


class MoodleCrawler:
    def __init__(self, session_id=None):
        self.parser = 'html.parser'
        self.login_token = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/53.0.2785.143 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        if session_id:
            self.session.cookies.set('MoodleSession', session_id)

    def get_login_token(self):
        soup = bs4.BeautifulSoup(self.session.get('https://moodle.ncku.edu.tw/').text, self.parser)
        token = soup.find('input', {'name': 'logintoken'})['value']
        return token

    def login(self, creds_path):
        with open(creds_path, 'r') as f:
            credentials = json.load(f)
            username = credentials['username']
            password = credentials['password']

        self.login_token = self.get_login_token()
        login_url = 'https://moodle.ncku.edu.tw/login/index.php'
        payload = {
            'Mime Type': 'application/x-www-form-urlencoded',
            'anchor': '',
            'username': username,
            'password': password,
            'logintoken': self.login_token,
        }
        self.session.post(login_url, data=payload)

    def get_month_assign_urls(self, timestamps):
        calendar_url = 'https://moodle.ncku.edu.tw/calendar/view.php?view=month&time={}'
        assign_urls = []

        for timestamp in timestamps:
            soup = bs4.BeautifulSoup(self.session.get(calendar_url.format(timestamp)).text, self.parser)
            for event in soup.find_all('a', {'data-action': 'view-event'}):
                href = event['href']
                if 'assign' in href:
                    assign_urls.append(href)

        return assign_urls

    def get_assign_info(self, assign_url):
        soup = bs4.BeautifulSoup(self.session.get(assign_url).text, self.parser)
        assign_info = {
            'title': soup.find('div', {'role': 'main'}).find('h2').text.strip(),
            'can_submit': False,
            'deadline': None,
            'submission_status': None,
            'description': str(soup.find('div', {'id': 'intro'})),
        }

        # get submission allowed date
        submission_allowed_date_th = soup.find('div',
                                               {'class': 'box py-3 generalbox boxaligncenter submissionsalloweddates'})
        if submission_allowed_date_th:
            assign_info['can_submit'] = False
        else:
            assign_info['can_submit'] = True

        # get submission status
        submission_status_th = soup.find('th', string='繳交狀態')
        if submission_status_th:
            submission_status_td = submission_status_th.find_next_sibling('td')
            submission_status = submission_status_td.text.strip() if submission_status_td else None
        else:
            raise SubmissionStatusError('submission status element not found')

        if submission_status in ['沒有繳交作業', '這個作業還沒人繳交']:
            assign_info['submission_status'] = 'not_submitted'
        elif submission_status.startswith('已繳交'):
            assign_info['submission_status'] = 'submitted'
        else:
            assign_info['submission_status'] = 'unknown'

        # Find the `<th>` tag by text and then the following `<td>` for the due date
        due_date_th = soup.find('th', string='規定繳交時間')
        if due_date_th:
            due_date_td = due_date_th.find_next_sibling('td')
            due_date = due_date_td.text.strip() if due_date_td else None
        else:
            raise DueDateError('due date element not found')

        # parse date
        assign_info['deadline'] = parse_date(due_date)

        return assign_info

    def get_next_k_month_assign_info(self, k):
        timestamps = get_next_k_month_timestamp(k=k)
        urls = self.get_month_assign_urls(timestamps)
        assign_info = []
        for url in urls:
            assign_info.append(self.get_assign_info(url))
        return assign_info


def get_next_k_month_timestamp(k):
    """
    Get timestamps that is within the next k months (include this month)
    """
    timestamps = []
    now = datetime.datetime.now()
    for i in range(k):
        year = now.year
        month = now.month + i
        if month > 12:
            month -= 12
            year += 1

        timestamps.append(int(datetime.datetime(year, month, 5).timestamp()))
    return timestamps


def parse_date(date_str):
    return re.sub(r'(\d+)年\s*(\d{1,2})月\s*(\d{1,2})日.*\)\s*(\d{1,2}:\d{1,2}).*', r'\1-\2-\3T\4', date_str) + ":00"
