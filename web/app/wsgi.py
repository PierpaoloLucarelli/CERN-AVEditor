from app.config import BaseConfig
from app.app_factory import create_app

app = create_app(BaseConfig)