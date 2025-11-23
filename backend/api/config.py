"""Application configuration using pydantic-settings"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment
    environment: str = "development"
    debug: bool = True

    # Firebase
    google_application_credentials: str = ""
    firebase_project_id: str = "cinefilm-platform"
    firebase_storage_bucket: str = "cinefilm-platform.firebasestorage.app"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1

    # Stripe
    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id_basic: str = ""
    stripe_price_id_pro: str = ""

    # Google Drive
    google_drive_client_id: str = ""
    google_drive_client_secret: str = ""

    # JWT
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 7200

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    cors_origins: str = "http://localhost:3000,https://cinefilm.tech,https://*.cinefilm.tech"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()

