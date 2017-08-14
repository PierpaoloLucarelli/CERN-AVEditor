from app.auth.cern_auth import load_cern_oauth
from app.extensions import video, images, db
from flask import Flask
from flask_uploads import configure_uploads
from flask_wtf import CSRFProtect
from werkzeug.contrib.fixers import ProxyFix

from app.views.downloads import downloads
from app.views.index_page import index_page
from app.views.video_upload import video_upload


def create_app(config_filename):

    app = Flask(__name__)
    app.config.from_object(config_filename)
    configure_uploads(app, (images, video))

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # enable CSRF for WTF-forms
    CSRFProtect(app)

    app.wsgi_app = ProxyFix(app.wsgi_app)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.register_blueprint(index_page)
    app.register_blueprint(video_upload)
    app.register_blueprint(downloads)

    load_cern_oauth(app)

    return app


