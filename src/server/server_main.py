import os.path
import src.sync_calendar.sync_main as sync_main

from flask import Flask, request, make_response, redirect
from google_auth_oauthlib.flow import Flow
from src.server.utils.storage import CloudStorage

app = Flask(__name__)

# Configure the OAuth2 flow
flow = Flow.from_client_secrets_file(
    'secrets/api_credentials.json',
    scopes=['https://www.googleapis.com/auth/calendar'],
    redirect_uri='https://sync-calendar-app-xt6u7vzbeq-de.a.run.app/callback'
)
storage = CloudStorage('moodle-405408', 'user_tokens')
token_dir = os.path.join(os.path.dirname(__file__), '../../secrets')


def check_token_exist(user_id):
    token_fname = f'{user_id}.json'
    token_path = os.path.join(os.path.dirname(__file__), '../../secrets', token_fname)
    if storage.check_blob_exist(token_fname):
        storage.download_blob(token_fname, token_path)


@app.route("/", methods=['GET'])
def trigger_sync():
    moodle_session_id = request.headers.get('Moodle-Session')
    user_id = request.headers.get('Moodle-ID')

    if not check_token_exist(user_id):
        return make_response('Unauthorized', 401)

    token_fname = f'{user_id}.json'
    token_path = os.path.join(token_dir, token_fname)
    storage.download_blob(token_fname, token_path)

    sync_main.main(moodle_session_id=moodle_session_id, token_path=token_path)
    return make_response('OK', 200)


@app.route('/auth', methods=['GET'])
def auth():
    print(request)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    os.environ['OAUTH2_STATE'] = state

    return redirect(authorization_url)


@app.route('/callback')
def oauth2callback():
    user_id = request.headers['Moodle-ID']

    state = os.environ.get('OAUTH2_STATE')
    flow.fetch_token(authorization_response=request.url)

    if not state or state != request.args['state']:
        return 'State error', 400

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
