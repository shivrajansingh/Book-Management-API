import os 
from dotenv import load_dotenv


load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_CONN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('SECRET_JWT_KEY')
    print(JWT_SECRET_KEY)
