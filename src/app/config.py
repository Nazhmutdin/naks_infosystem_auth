import os
from pathlib import Path

from dotenv import load_dotenv


if not os.getenv("MODE"):
    load_dotenv(f"{Path(os.path.dirname(os.path.abspath(__file__))).parent.parent}/.dev.env", override=True)


class DBConfig:

    @classmethod
    def USER(cls) -> str:
        return os.getenv("USER")


    @classmethod
    def DB_NAME(cls) -> str:
        return os.getenv("DATABASE_NAME")
    
    
    @classmethod
    def DB_PASSWORD(cls) -> str:
        return os.getenv("DATABASE_PASSWORD")
    

    @classmethod
    def DB_HOST(cls) -> str:
        return os.getenv("DB_HOST")
    

    @classmethod
    def DB_PORT(cls) -> str:
        return os.getenv("DB_PORT")
    

    @classmethod
    def DB_URL(cls) -> str:
        return "postgresql+asyncpg://{0}:{1}@{2}:{3}/{4}".format(
            cls.USER(), 
            cls.DB_PASSWORD(), 
            cls.DB_HOST(), 
            cls.DB_PORT(), 
            cls.DB_NAME()
        )


class RedisConfig:

    @classmethod
    def REDIS_HOST(cls) -> str:
        return os.getenv("REDIS_HOST")


    @classmethod
    def REDIS_PORT(cls) -> str:
        return os.getenv("REDIS_PORT")
    
    
    @classmethod
    def REDIS_PASSWORD(cls) -> str:
        return os.getenv("REDIS_PASSWORD")
    

    @classmethod
    def USER(cls) -> str:
        return "default"
    

    @classmethod
    def DB_NAME(cls) -> str:
        return 1
    

    @classmethod
    def CACHE_EXP(cls) -> int:
        return os.getenv("CACHE_EXP", 900)
    

    @classmethod
    def REDIS_URL(cls) -> str:
        return "redis://{0}:{1}@{2}:{3}/{4}".format(
            cls.USER(), 
            cls.REDIS_PASSWORD(), 
            cls.REDIS_HOST(), 
            cls.REDIS_PORT(), 
            cls.DB_NAME()
        )


class ApplicationConfig:

    @classmethod
    def ACCESS_TOKEN_LIFETIME_MINUTES(cls) -> int:
        return 60


    @classmethod
    def REFRESH_TOKEN_LIFETIME_HOURS(cls) -> int:
        return 24
    
    
    @classmethod
    def DOMAIN(cls) -> str:
        return os.getenv("DOMAIN")
    

    @classmethod
    def SECRET_KEY(cls) -> str:
        return os.getenv("SECRET_KEY")
    

    @classmethod
    def ALGORITHM(cls) -> str:
        return "HS256"
    

    @classmethod
    def BASE_DIR(cls) -> Path:
        return Path(os.path.dirname(os.path.abspath(__file__))).parent
