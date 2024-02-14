""" This file is the entry point for the Flask app. """
from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    # Run the Flask app
    app.run(host='localhost', port=8080, debug=False)
