from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://tcgtool:tcgtool_dev@localhost:5432/tcgtool"
    REDIS_URL: str = "redis://localhost:6379/0"
    TCGDEX_BASE_URL: str = "https://api.tcgdex.net/v2"
    POKEMONTCG_BASE_URL: str = "https://api.pokemontcg.io/v2"
    POKEMONTCG_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    FRONTEND_URL: str = "http://localhost:3000"
    DEFAULT_LANGUAGE: str = "pt"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
