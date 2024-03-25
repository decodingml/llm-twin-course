from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # MongoDB
    DATABASE_HOST: str = "mongodb://decodingml:decodingml@decodingml_mongo:27017"
    DATABASE_NAME: str = "twin"

    # Selenium
    SELENIUM_BROWSER_BINARY_PATH: str | None = "/opt/chrome/chrome"
    SELENIUM_DRIVER_BINARY_PATH: str = "/opt/chromedriver"

    # LinkedIn Credentials
    LINKEDIN_USERNAME: str | None = None
    LINKEDIN_PASSWORD: str | None = None


settings = Settings()
print(settings.SELENIUM_DRIVER_BINARY_PATH)
