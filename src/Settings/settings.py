from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    bot_token: str = ""
    API_BASE: AnyUrl = AnyUrl("http://89.169.162.5/:5000")
    #API_BASE: AnyUrl = AnyUrl("http://localhost:5248")
    API_TOKEN: str | None = None
    VERIFY_SSL: bool = False
    CA_CERT_PATH: str | None = None
    bot_secret: str

    class Config:
        env_file = ".env"
