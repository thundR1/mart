from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "k1q35ijGCCe6fSB8dzkHk0/IMTT/P/02yIHg0ZrPwqQ="
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "sqlite:///./meridian.db"
    embedding_backend: str = "transformer"
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
