""" Blueprint for the authentication routes. """
import os.path

from flask import Blueprint, current_app, make_response, request
from google_auth_oauthlib.flow import Flow

from backend.app.routes.utils.session import Session
from backend.app.routes.utils.utils import get_id_from_session

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('', methods=['POST'])
def auth():
    """
    Authenticates the user and generates the authorization URL for accessing Google Calendar API.

    Returns:
        str: The authorization URL for the user to grant access to their Google Calendar.
    """
    session = Session(current_app.config, request=request)
    if session.get('moodle_session') is None:
        resp = make_response('User not logged in', 401)
        return session.make_response(resp)

    token = session.create_token()
    flow = Flow.from_client_secrets_file(
        current_app.config['API_CREDS_PATH'],
        scopes=[
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/calendar',
        ],
        state=token,
        redirect_uri=f'{current_app.config["BASE_URL"]}/auth/callback'
    )
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true'
    )

    resp = make_response(authorization_url, 200)
    return session.make_response(resp)


@auth_blueprint.route('/callback')
def oauth2callback():
    """
    Callback function for OAuth2 authentication.

    This function handles the callback from the OAuth2 authentication process. It retrieves the state parameter from the request,
    verifies the state, and then fetches the access token using the authorization code. The access token is then
    stored in a JSON file for future use.

    Returns:
        A response indicating the success or failure of the authentication process.
    """
    state = request.args.get('state')

    session = Session(current_app.config, request=request)
    session.from_token(state)
    if session.payload is None:
        resp = make_response('Invalid state', 400)
        return session.make_response(resp)

    flow = Flow.from_client_secrets_file(
        current_app.config['API_CREDS_PATH'],
        scopes=[
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/calendar',
        ],
        redirect_uri=f'{current_app.config["BASE_URL"]}/auth/callback'
    )

    auth_code = request.args.get('code')
    flow.fetch_token(code=auth_code)

    credentials = flow.credentials

    # try:
    user_id = get_id_from_session(session.get('moodle_session'))
    token_fname = f'{user_id}.json'
    token_path = os.path.join(current_app.config['TOKEN_DIR'], token_fname)
    with open(token_path, 'w', encoding='utf-8') as token:
        token.write(credentials.to_json())

    resp = make_response('綁定成功，請關閉此分頁', 200)
    return session.make_response(resp)
    # except TypeError:
    #     # Can't get user ID from session
    #     resp = make_response('Session Expired', 401)
    #     return session.make_response(resp)
