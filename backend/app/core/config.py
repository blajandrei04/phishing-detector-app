from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "Phishing Detector API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: list[str] = ["http://localhost:4200"]
    database_url: str = "sqlite:///./phishing_detector.db"
    model_path: str = "./artifacts/xgb_opt.pkl"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings=Settings()
