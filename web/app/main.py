#!flask/bin/python
from app.app_factory import create_app
from app.config import BaseConfig

from app.cli import initialize_cli

app = create_app(BaseConfig)
initialize_cli(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=app.config['APP_PORT'], debug=app.config['DEBUG'], ssl_context='adhoc')