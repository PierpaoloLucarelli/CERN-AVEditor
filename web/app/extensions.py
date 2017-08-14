import logging
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES
from wtforms.validators import Regexp

# upload sets for flask-uploads allowed files (mp4 only)
video = UploadSet('video', '.mp4')
images = UploadSet('images', IMAGES)

# regular expression used by wtfforms to check if time is in HH:MM:SS format
time_regex = Regexp('([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]')

db = SQLAlchemy()


# application logger
def setup_custom_logger(name):
    """
    Creates a logger to be used by the whole appliction
    :param name: the name of the logger
    :return: The application logger
    """
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.FileHandler('aveditor.log')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
