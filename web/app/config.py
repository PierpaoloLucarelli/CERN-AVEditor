import os

from app.utils.utils import str2bool


class DatabaseConfig:
    """
    Application database configuration
    """

    DB_NAME = os.environ['DB_NAME']
    DB_PASS = os.environ['DB_PASS']
    DB_PORT = os.environ['DB_PORT']
    DB_SERVICE = os.environ['DB_SERVICE']
    DB_USER = os.environ['DB_USER']

    """
    Database URI will be generated with the already gotten database parameters
    """
    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
        DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
    )


class BaseConfig(DatabaseConfig):
    """
    Main config
    """

    #################### flask-uplaods ##########################

    UPLOADS_DEFAULT_DEST = os.environ['UPLOADS_DEFAULT_DEST']
    UPLOADED_IMAGES_DEST = os.environ['UPLOADED_IMAGES_DEST']
    UPLOADED_VIDEO_DEST = os.environ['UPLOADED_VIDEO_DEST']
    UPLOADED_VIDEO_URL = os.environ['UPLOADED_VIDEO_URL']

    #################### flask-wtf ##########################

    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']

    #################### app configs ##########################

    APP_PORT = int(os.environ['APP_PORT'])
    DEBUG = str2bool(os.environ['DEBUG'])
    TESTING = str2bool(os.environ['TESTING'])

    #################### auth ##########################
    CERN_OAUTH_CLIENT_ID = os.environ['CERN_OAUTH_CLIENT_ID']
    CERN_OAUTH_CLIENT_SECRET = os.environ['CERN_OAUTH_CLIENT_SECRET']
