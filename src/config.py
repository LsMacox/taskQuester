from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


base_dir = Path(__file__).parent.resolve()


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    BASE_DIR: Path = base_dir
    GOOGLE_MAIL: str
    GOOGLE_CLIENT_CREDS: dict = {}
    GOOGLE_USER_CREDS: dict = {}
    GOOGLE_CALENDAR_ID: str = 'primary'
    TIMEZONE: str = 'Europe/Moscow'
    GOOGLE_TASK_LIST: str = ''
    DEBUG: bool

    @property
    def DATABASE_URL_asyncmy(self):
        # mysql+asyncpg://mysql:mysql@localhost:3306/habitica
        return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_pymysql(self):
        # mysql+psycopg://mysql:mysql@localhost:3306/habitica
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')


settings = Settings()