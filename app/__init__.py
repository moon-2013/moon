 
        
    
  
  
import os
from flask import Flask, request
from app.config import Config
from app.extensions import db, jwt
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from flask_cors import CORS
from app.routes.home import home_bp

def create_app():
    app = Flask(__name__)

    # ✅ تحميل الإعدادات من Config
    app.config.from_object(Config)  

    # ✅ تفعيل CORS
    CORS(app, resources={r"/*": {"origins": "*"}})              

    # ✅ تهيئة الإضافات
    db.init_app(app)
    jwt.init_app(app)

    # ✅ تسجيل المسارات
    app.register_blueprint(auth_bp, url_prefix='/sing')
    app.register_blueprint(users_bp, url_prefix='/profile_me')
    app.register_blueprint(home_bp, url_prefix='/')

    # ✅ إضافة Webhook داخل التطبيق
    @app.route("/webhook", methods=["POST"])
    def webhook():
        """يستقبل Webhook من GitHub ويقوم بتحديث المشروع تلقائيًا"""
        data = request.get_json()
        if data and "ref" in data and data["ref"] == "refs/heads/main":  # تأكد أن التحديث للفرع الرئيسي
            os.system("cd /home/moon2013/moon && git pull origin main")      
   
   
   
        
    
            
   
   
    
        # إيقاف السيرفر الحالي
        os.system("pkill -f 'flask run'")

        # إعادة تشغيل السيرفر
        time.sleep(2)  # تأكد من أن السيرفر توقف قبل إعادة تشغيله
        os.system("python3 /home/moon2013/moon/run.py")  # قم بتشغيل السيرفر مجددًا باستخدام python3 run.py
   
   
   
   
   
          
    
    
  
  
  
            return "Repository updated successfully!", 200
        return "Invalid request", 400

    return app  
  
  
  
  
