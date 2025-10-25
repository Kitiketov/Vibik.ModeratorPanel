from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    bot_token: str = ""
    API_BASE: AnyUrl = AnyUrl("http://localhost:5248")
    API_TOKEN: str | None = None
    VERIFY_SSL: bool = False
    CA_CERT_PATH: str | None = None

    class Config:
        env_file = ".env"
