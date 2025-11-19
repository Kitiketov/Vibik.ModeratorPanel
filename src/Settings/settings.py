from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    bot_token: str = ""
    API_BASE: AnyUrl = AnyUrl("http://localhost:5000")
    API_BASE_LOCAL: AnyUrl | None = None
    API_ENV: str = "prod"  # prod | local
    API_TOKEN: str | None = None
    VERIFY_SSL: bool = False
    CA_CERT_PATH: str | None = None
    bot_secret: str = ""

    @property
    def api_base(self) -> AnyUrl:
        """Возвращает адрес API в зависимости от окружения."""
        if self.API_ENV.lower() == "local" and self.API_BASE_LOCAL is not None:
            return self.API_BASE_LOCAL
        return self.API_BASE

    class Config:
        env_file = ".env"
