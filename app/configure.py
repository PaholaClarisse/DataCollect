from dotenv import load_dotenv
import os


load_dotenv()

class Settings:
    PORT = os.getenv("PORT", 27017)
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    MONGO_URI = f"mongodb://{DB_USER}:{DB_PASSWORD}@localhost:{PORT}/{DB_NAME}?authSource=admin"
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

settings = Settings()