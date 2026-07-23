import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # Build DB URI directly from .env variables
    _user = os.getenv("DB_USER", "root")
    _pass = os.getenv("DB_PASSWORD", "yamuna")
    _host = os.getenv("DB_HOST", "127.0.0.1")
    _port = os.getenv("DB_PORT", "3306")
    _name = os.getenv("DB_NAME", "tradeiq")

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{_user}:{_pass}@{_host}:{_port}/{_name}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "connect_args": {"connect_timeout": 10},
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}

def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)