import os.path
import src.sync_calendar.sync_main as sync_main

from flask import Flask, request, make_response, redirect, session, url_for
from flask_cors import CORS
from datetime import timedelta
from google_auth_oauthlib.flow import Flow

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=2)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

# Enable CORS for all routes
CORS(app, supports_credentials=True,
     origins=['https://moodle.ncku.edu.tw', 'https://sync-calendar-app-xt6u7vzbeq-de.a.run.app'])

flow = Flow.from_client_secrets_file(
    '/secrets/api_credentials.json',
    scopes=['https://www.googleapis.com/auth/calendar'],
    redirect_uri='https://sync-calendar-app-xt6u7vzbeq-de.a.run.app/callback'
)

token_dir = os.path.join('/', 'tokens')


def check_token_exist(user_id):
    token_fname = f'{user_id}.json'
    token_path = os.path.join(token_dir, token_fname)
    return os.path.exists(token_path)


@app.route("/login", methods=['POST'])
def login():
    user_id = request.headers.get('Moodle-ID')
    moodle_session = request.headers.get('Moodle-Session')
    if 'user_id' in session:
        session.clear()

    session.permanent = True
    session['user_id'] = user_id
    session['moodle_session'] = moodle_session
    return make_response('OK', 200)


@app.route("/", methods=['POST'])
def trigger_sync():
    user_id = session.get('user_id', None)
    moodle_session_id = session.get('moodle_session', None)

    if user_id is None:
        return make_response('User not logged in', 401)
    if moodle_session_id is None:
        return make_response('Moodle session not found', 404)

    if not check_token_exist(user_id):
        return make_response('Token not found', 404)

    token_fname = f'{user_id}.json'
    token_path = os.path.join(token_dir, token_fname)

    sync_main.main(moodle_session_id=moodle_session_id, token_path=token_path)
    return make_response('OK', 200)


@app.route('/auth', methods=['POST'])
def auth():
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['OAUTH2_STATE'] = state
    
    return make_response(authorization_url, 200)


@app.route('/callback')
def oauth2callback():
    user_id = session.get('user_id', None)
    if user_id is None:
        return make_response('User not logged in', 401)

    state = session.get('OAUTH2_STATE')
    
    auth_code = request.args.get('code')
    flow.fetch_token(code=auth_code)

    if not state:
        return make_response('State not found', 400)

    if not state or state != request.args['state']:
        return make_response('State not match', 400)

    # Now you have the tokens, you can use them to make API calls
    credentials = flow.credentials
    # Use credentials here...
    token_fname = f'{user_id}.json'
    token_path = os.path.join(token_dir, token_fname)
    with open(token_path, 'w') as token:
        token.write(credentials)

    return make_response('OK', 200)


# start the server
if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=False)
