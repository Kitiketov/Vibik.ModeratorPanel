from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    bot_token: str = ""
    api_base_host: AnyUrl | None = None
    api_base_local: AnyUrl | None = None
    api_env: str = "prod"  # prod | local
    api_token: str | None = None
    verify_ssl: bool = False
    ca_cert_path: str | None = None
    bot_secret: str = ""

    @property
    def api_base(self) -> AnyUrl:
        """Возвращает адрес API в зависимости от окружения."""
        base: AnyUrl | None = None
        if self.api_env.lower() == "local" and self.api_base_local is not None:
            base = self.api_base_local
        else:
            base = self.api_base_host

        if base is None:
            raise ValueError("API base URL is not configured")

        return base

    class Config:
        env_file = ".env"
