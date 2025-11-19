from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    bot_token: str = ""
    API_BASE: AnyUrl | None = None
    API_BASE_LOCAL: AnyUrl | None = None
    API_ENV: str = "prod"  # prod | local
    API_TOKEN: str | None = None
    VERIFY_SSL: bool = False
    CA_CERT_PATH: str | None = None
    bot_secret: str = ""

    @property
    def api_base(self) -> AnyUrl:
        """Возвращает адрес API в зависимости от окружения."""
        base: AnyUrl | None = None
        if self.API_ENV.lower() == "local" and self.API_BASE_LOCAL is not None:
            base = self.API_BASE_LOCAL
        else:
            base = self.API_BASE

        if base is None:
            raise ValueError("API base URL is not configured")

        return base

    class Config:
        env_file = ".env"
