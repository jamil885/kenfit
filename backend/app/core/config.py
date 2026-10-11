from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: Literal["HS256"] = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    cors_origins: list[str] = []
    app_env: Literal["development", "production"] = "development"
    mail_mode: Literal["disabled", "file", "smtp"] = "disabled"
    mail_outbox: str = ".local-mail"
    smtp_host: str | None = None
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "KenFit <no-reply@localhost>"

    @model_validator(mode="after")
    def mail_config(self):
        if self.app_env == "production" and self.mail_mode == "file":
            raise ValueError("File mailbox is for local development only")
        if self.mail_mode == "smtp" and not self.smtp_host:
            raise ValueError("SMTP_HOST is required")
        return self

    model_config = SettingsConfigDict(
        env_file=(ROOT.parent / ".env", ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
