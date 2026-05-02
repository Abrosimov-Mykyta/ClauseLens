from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ClauseLens API"
    app_env: str = "development"
    database_url_override: str = ""
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "clauselens"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1/responses"
    worker_poll_interval_seconds: float = 2.0
    upload_dir: str = "./uploads"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override

        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def local_database_url(self) -> str:
        return "sqlite:///./apps/api/clauselens.db"


settings = Settings()
