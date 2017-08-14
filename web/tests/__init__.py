import os

from app.app_factory import create_app
from flask_testing import TestCase

from web.app.extensions import db

_basedir = os.path.abspath(os.path.dirname(__file__))


class TestConfig(object):
    UPLOADS_DEFAULT_DEST = "/opt/app-root/test-uploads"
    UPLOADED_IMAGES_DEST = "/opt/app-root/test-uploads"

    SECRET_KEY = "a random key that will be replaced in production"
    TESTING = True
    WTF_CSRF_ENABLED = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'test_app.db')

    CERN_OAUTH_CLIENT_ID = "test"
    CERN_OAUTH_CLIENT_SECRET = "test"
    CERN_OAUTH_TOKEN_URL = ""
    CERN_OAUTH_AUTHORIZE_URL = ""


class BaseTestCase(TestCase):

    def create_app(self):

        application = create_app(TestConfig)
        return application

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
