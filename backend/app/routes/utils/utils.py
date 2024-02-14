"""
This module contains utility functions for handling tokens and retrieving user IDs from session IDs.
"""

import os

from backend.app.services.sync_calendar.utils.moodle_crawler import \
    MoodleCrawler


def check_token_exist(user_id, token_dir):
    """
    Check if a token file exists for the given user ID.

    Args:
        user_id (str): The ID of the user.
        token_dir (str): The directory where the token file is located.

    Returns:
        bool: True if the token file exists, False otherwise.
    """
    token_fname = f'{user_id}.json'
    token_path = os.path.join(token_dir, token_fname)
    return os.path.exists(token_path)


def get_id_from_session(session_id):
    """
    Get the user ID from the given session id.

    Args:
        session_id (str): The moodle session id.

    Returns:
        str: The user ID from the session.
    """
    crawler = MoodleCrawler(session_id)
    return crawler.get_user_id()
