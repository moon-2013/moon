
        


import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # المسار الأساسي للمشروع
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "instance", "moon.db")  # موقع قاعدة البيانات

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DB_PATH
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "your_jwt_secret_key"
  
