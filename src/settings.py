import os
from pathlib import Path

from dotenv import load_dotenv


if not os.getenv("MODE"):
    load_dotenv(f"{Path(os.path.dirname(os.path.abspath(__file__))).parent.parent}/.dev.env")


class Settings:

    @classmethod
    def ACCESS_TOKEN_LIFETIME_MINUTES(cls) -> int:
        return 60


    @classmethod
    def REFRESH_TOKEN_LIFETIME_HOURS(cls) -> int:
        return 24


    @classmethod
    def DB_NAME(cls) -> str:
        return os.getenv("AUTH_DATABASE_NAME")
    
    
    @classmethod
    def DB_PASSWORD(cls) -> str:
        return os.getenv("DATABASE_PASSWORD")
    
    
    @classmethod
    def DOMAIN(cls) -> str:
        return os.getenv("DOMAIN")
    
    
    @classmethod
    def API_DOMAIN(cls) -> str:
        return os.getenv("API_DOMAIN")
    

    @classmethod
    def HOST(cls) -> str:
        return os.getenv("HOST")
    

    @classmethod
    def USER(cls) -> str:
        return os.getenv("USER")
    

    @classmethod
    def PORT(cls) -> str:
        return os.getenv("PORT")
    

    @classmethod
    def SECRET_KEY(cls) -> str:
        return os.getenv("SECRET_KEY")
    

    @classmethod
    def BASE_DIR(cls) -> Path:
        return Path(os.path.dirname(os.path.abspath(__file__))).parent
