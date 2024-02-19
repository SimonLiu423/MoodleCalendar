""" This module contains the main blueprint for the Flask app. """
import os

from flask import (Blueprint, current_app, make_response, render_template,
                   request)

from backend.app.routes.utils.session import Session
from backend.app.routes.utils.utils import (check_token_exist,
                                            get_id_from_session)
from backend.app.services.calendar_syncer import __main__
from backend.app.services.user_info.__main__ import UserInfo

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route("/privacy-policy", methods=['GET'])
def privacy_policy():
    """
    Render the privacy policy page.

    Returns:
        The rendered privacy policy page.
    """
    return render_template('privacy_policy.html')


@main_blueprint.route("/login", methods=['POST'])
def login():
    """
    Handles the login functionality.

    Retrieves the Moodle session from the request headers and adds it to the session cookies.
    If the Moodle session is not found, returns a 404 response.

    Returns:
        A response indicating the success of the login process.
    """
    session = Session(current_app.config)
    moodle_session = request.headers.get('Moodle-Session')

    if moodle_session is None:
        resp = make_response('Moodle session not found', 404)
        return session.make_response(resp)

    session.add_cookie('moodle_session', moodle_session)

    resp = make_response('OK', 200)
    return session.make_response(resp)


@main_blueprint.route("/sync", methods=['POST'])
def trigger_sync():
    """
    Triggers the synchronization process between the Moodle calendar and the local system.

    Returns:
        Response: The response indicating the status of the synchronization process.
    """
    session = Session(current_app.config, request=request)
    moodle_session_id = session.get('moodle_session')

    resp = None

    if moodle_session_id is None:
        resp = make_response('Moodle session not found', 404)

    try:
        user_id = get_id_from_session(moodle_session_id)
    except TypeError:
        # Can't get user ID from session
        resp = make_response('Session Expired', 401)
        return session.make_response(resp)

    if not check_token_exist(user_id, current_app.config['TOKEN_DIR']):
        resp = make_response('Token not found', 404)
    else:
        token_fname = f'{user_id}.json'
        token_path = os.path.join(current_app.config['TOKEN_DIR'], token_fname)

        try:
            __main__.main(moodle_session_id=moodle_session_id, token_path=token_path)
            resp = make_response('OK', 200)
        except Exception as e:
            # Error occurred during sync
            resp = make_response('Error occurred during sync', 500)
            raise e

    return session.make_response(resp)


@main_blueprint.route("/binded-email", methods=['GET'])
def get_binded_email():
    session = Session(current_app.config, request=request)
    moodle_session_id = session.get('moodle_session')

    resp = None

    if moodle_session_id is None:
        resp = make_response('Moodle session not found', 404)

    try:
        user_id = get_id_from_session(moodle_session_id)
    except TypeError:
        # Can't get user ID from session
        resp = make_response('Session Expired', 401)
        return session.make_response(resp)

    if not check_token_exist(user_id, current_app.config['TOKEN_DIR']):
        resp = make_response('Token not found', 404)
    else:
        token_fname = f'{user_id}.json'
        token_path = os.path.join(current_app.config['TOKEN_DIR'], token_fname)

        try:
            api_creds_path = os.path.join('.', 'secrets', 'api_credentials.json')
            user_info = UserInfo(api_creds_path, token_path=token_path)
            email = user_info.get_email()

            resp = make_response(email, 200)
        except Exception:
            # Error occurred during sync
            resp = make_response('Error occurred while obtaining email', 500)

    return session.make_response(resp)


@main_blueprint.route("/google9dff49afa7ecbee1.html", methods=['GET'])
def site_verification():
    """
    Handles the site verification request from Google Search Console.

    Returns:
        The site verification page.
    """
    return render_template('google9dff49afa7ecbee1.html')
