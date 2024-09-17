import os

from dataclasses import dataclass


@dataclass
class RedisEnv:
    host: str = os.getenv("REDIS_HOST")
    port: int = os.getenv("REDIS_PORT")
    db: int = os.getenv("REDIS_DB")

    def __post_init__(self):
        if not self.host:
            raise ValueError("REDIS_HOST is not set")
        if not self.port:
            raise ValueError("REDIS_PORT is not set")
        if not self.db:
            raise ValueError("REDIS_DB is not set")

        self.port = int(self.port)
        self.db = int(self.db)

    @property
    def connect_str(self):
        return f"redis://{self.host}:{self.port}/{self.db}"


@dataclass
class DexScreenerEnv:
    host: str = os.getenv("DEXSCREENER_HOST")
    port: int = os.getenv("DEXSCREENER_PORT")

    def __post_init__(self):
        if not self.host:
            raise ValueError("DEXSCREENER_HOST is not set")
        if not self.port:
            raise ValueError("DEXSCREENER_PORT is not set")

        self.port = int(self.port)

    @property
    def connect_str(self):
        return f"http://{self.host}:{self.port}/dexscreener"


@dataclass
class PostgresEnv:
    host: str = os.getenv("POSTGRES_HOST")
    port: int = os.getenv("POSTGRES_PORT")
    user: str = os.getenv("POSTGRES_USER")
    password: str = os.getenv("POSTGRES_PASSWORD")
    db: str = os.getenv("POSTGRES_DB")

    def __post_init__(self):
        if not self.host:
            raise ValueError("POSTGRES_HOST is not set")
        if not self.port:
            raise ValueError("POSTGRES_PORT is not set")
        if not self.user:
            raise ValueError("POSTGRES_USER is not set")
        if not self.password:
            raise ValueError("POSTGRES_PASSWORD is not set")
        if not self.db:
            raise ValueError("POSTGRES_DB is not set")

        self.port = int(self.port)

    @property
    def connect_str(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
