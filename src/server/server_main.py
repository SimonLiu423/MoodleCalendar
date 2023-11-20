import os.path
import src.sync_calendar.sync_main as sync_main

from flask import Flask, request, make_response
from src.sync_calendar.sync_main import main
from src.server.utils.storage import CloudStorage

app = Flask(__name__)


@app.route("/", methods=['GET'])
def trigger_sync():
    print(request.headers)
    moodle_session_id = request.headers.get('Moodle-Session')
    username = request.headers.get('Username')

    # check if there's user's token file in google cloud SQL, create one if not
    storage = CloudStorage('moodle-405408', 'user_tokens')

    upload_creds = False
    token_fname = f'{username}.json'
    token_path = os.path.join(os.path.dirname(__file__), '../../secrets', token_fname)
    if storage.check_blob_exist(token_fname):
        storage.download_blob(token_fname, token_path)

    sync_main.main(moodle_session_id=moodle_session_id, token_path=token_path)

    if upload_creds is True:
        if os.path.exists(token_path):
            storage.upload_blob(token_path, token_fname)
        else:
            return make_response('Unauthorized', 401)

    return make_response('OK', 200)


# start the server
if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True)
