""" 
This module contains the Session class that handles the creation, retrieval, 
and manipulation of session data. Google has announced that third-party cookies 
will be phased out soon. 'Session' from Flask currently does not support 
CHIPS(Cookies Having Independent Partitioned State). Therefore I implemented 
session myself, adding 'Partitioned' attribute to the cookie.
"""
import jwt


class Session:
    """
    Represents a session object that handles session management and token generation.

    Attributes:
        config (dict): The configuration dictionary containing the secret key and other session settings.
        secret_key (str): The secret key used for token generation.
        payload (dict): The payload dictionary containing session data.

    Methods:
        __init__(self, config, request=None): Initializes the Session object with the given request.
        get(self, key): Returns the value of the given key from the payload.
        add_cookie(self, key, value): Adds a cookie to the payload dictionary.
        create_token(self): Creates a JSON Web Token (JWT) using the payload and secret key.
        from_token(self, token): Decodes the given JWT token and sets the payload to the decoded payload.
        from_request(self, request): Extracts and decodes the JWT token from the request cookies.
        make_response(self, response): Adds the session cookie to the given response.
    """

    def __init__(self, config, request=None):
        """
        Initializes the Session object with the given request.

        Args:
            config (dict): The configuration dictionary containing the secret key and other session settings.
            request (flask.Request, optional): The Flask request object. Defaults to None.
        """
        self.config = config
        self.secret_key = config['SECRET_KEY']
        self.payload = {}
        if request:
            self.from_request(request)

    def get(self, key):
        """
        Returns the value of the given key from the payload.

        Args:
            key (str): The key to retrieve from the payload.

        Returns:
            str: The value of the given key if it exists, None otherwise.
        """
        return self.payload.get(key, None)

    def add_cookie(self, key, value):
        """
        Adds a cookie to the payload dictionary.

        Args:
            key (str): The key of the cookie.
            value (str): The value of the cookie.
        """
        self.payload[key] = value

    def create_token(self):
        """
        Creates a JSON Web Token (JWT) using the payload and secret key.

        Returns:
            str: The generated JWT.
        """
        token = jwt.encode(self.payload, self.secret_key, algorithm='HS256')
        return token

    def from_token(self, token):
        """
        Decodes the given JWT token and sets the payload to the decoded payload.

        Args:
            token (str): The JWT token to decode.
        """
        try:
            self.payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return self.payload
        except jwt.ExpiredSignatureError:
            # Handle expired token
            print('Token is expired')
            return None
        except jwt.InvalidTokenError:
            # Handle invalid token
            print('Invalid token')
            return None

    def from_request(self, request):
        """
        Extracts and decodes the JWT token from the request cookies.

        Args:
            request (flask.Request): The Flask request object.

        Returns:
            dict: The decoded payload of the JWT token if it exists and is valid, None otherwise.
        """
        token = request.cookies.get('session')
        if token is None:
            return None

        return self.from_token(token)

    def make_response(self, response):
        """
        Adds the session cookie to the given response.

        Args:
            response (Response): The response to add the cookie to.

        Returns:
            Response: The response with the added cookie.
        """
        path = self.config['SESSION_COOKIE_PATH']
        same_site = self.config['SESSION_COOKIE_SAMESITE']
        http_only_str = 'HttpOnly' if self.config['SESSION_COOKIE_HTTPONLY'] else ''
        secure_str = 'Secure' if self.config['SESSION_COOKIE_SECURE'] else ''
        lifetime = self.config['PERMANENT_SESSION_LIFETIME'].total_seconds()
        partitioned_str = 'Partitioned' if self.config['SESSION_COOKIE_PARTITIONED'] else ''

        if self.payload != {}:
            response.headers['Set-Cookie'] = (
                f"session={self.create_token()}; "
                f"Path={path}; "
                f"SameSite={same_site}; "
                f"Max-Age={lifetime}; "
                f"{http_only_str}; "
                f"{secure_str}; "
                f"{partitioned_str}; "
            )
        return response
