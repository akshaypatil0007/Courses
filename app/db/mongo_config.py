from pydantic import BaseSettings


class DatabaseSettings(BaseSettings):
    DB_URL = "mongodb://127.0.0.1:27017/coursesdb"
    DB_NAME = "coursesdb"


_db_settings = DatabaseSettings()
