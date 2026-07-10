from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    APP_ENV: str

    META_APP_SECRET: str | None = None

    BASE_GRAPH_URL: str

    WA_PHONE_NUMBER_ID: str
    WA_ACCESS_TOKEN: str
    WA_VERIFY_TOKEN: str
    WA_API_VERSION: str

    # Magento
    MAGENTO_URL: str
    MAGENTO_ADMIN_USERNAME: str
    MAGENTO_ADMIN_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()