    
    
 
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # المسار الأساسي للمشروع
DB_PATH = os.path.join(BASE_DIR, "app", "moon.db")  # وضع قاعدة البيانات في مجلد app

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DB_PATH
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "your_jwt_secret_key"    
  
  
  
    