from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    bot_token: str = ""
    api_base: AnyUrl
    api_base_local: AnyUrl | None = None
    api_env: str = "prod"  # prod | local
    API_TOKEN: str | None = None
    VERIFY_SSL: bool = False
    CA_CERT_PATH: str | None = None
    bot_secret: str

    @property
    def api_base(self) -> AnyUrl:
        """Возвращает адрес API в зависимости от окружения."""
        if self.api_env.lower() == "local" and self.api_base_local is not None:
            return self.api_base_local
        return self.api_base

    class Config:
        env_file = ".env"
