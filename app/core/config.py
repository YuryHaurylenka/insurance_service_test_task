from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application-wide settings.
    """
    api_prefix: str = "/api/v1"
    project_name: str = "Insurance Service"
    version: str = "1.0.0"
    debug: bool = False

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "postgresql"
    postgres_port: int = 5432
    db_echo: bool = False

    kafka_broker: str = "kafka:9092"
    kafka_topic_tariffs: str = "tariff_logs"
    kafka_topic_insurance: str = "insurance_logs"
    batch_size: int = 5
    flush_interval: int = 30

    @property
    def db_url(self) -> str:
        """
        Dynamically generate the database URL.
        """
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
