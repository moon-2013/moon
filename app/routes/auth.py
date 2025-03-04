from flask import Blueprint, request, jsonify
from app.extensions import db
from flask_jwt_extended import create_access_token
from app.models import User, COUNTRY_CODES
from werkzeug.security import generate_password_hash, check_password_hash
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/up', methods=['POST'])
def register():
    data = request.get_json()
    
    # التحقق من وجود البيانات المطلوبة
    if not all(k in data for k in ["username", "password"]):
        return jsonify({"error": "يجب توفير اسم المستخدم وكلمة المرور"}), 400
    
    # التحقق من أن اسم المستخدم غير موجود مسبقاً
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "اسم المستخدم موجود بالفعل"}), 400
    
    # التحقق من رقم الهاتف إذا تم تقديمه
    if "phone_number" in data and data["phone_number"]:
        # فحص رقم الهاتف حسب البلد
        country_code = data.get("country_code", "IQ")  # افتراضي العراق
        
        if country_code not in COUNTRY_CODES:
            return jsonify({"error": "رمز البلد غير صالح"}), 400
        
        phone_rules = COUNTRY_CODES[country_code]
        phone_number = data["phone_number"]
        
        # إزالة أي رموز زائدة من الرقم
        phone_number = re.sub(r'[^0-9]', '', phone_number)
        
        # التحقق من صحة طول الرقم
        if len(phone_number) != phone_rules['length']:
            return jsonify({"error": f"يجب أن يكون طول رقم الهاتف {phone_rules['length']} أرقام"}), 400
        
        # التحقق من بداية الرقم إذا كان هناك بداية محددة
        if phone_rules['start'] and not phone_number.startswith(phone_rules['start']):
            return jsonify({"error": f"يجب أن يبدأ رقم الهاتف بـ {phone_rules['start']}"}), 400
        
        # التحقق من عدم وجود رقم هاتف مسجل مسبقاً
        if User.query.filter_by(phone_number=phone_number).first():
            return jsonify({"error": "رقم الهاتف مسجل بالفعل"}), 400
            
        # تنسيق الرقم بشكل صحيح
        formatted_phone = f"+{phone_rules['code']}{phone_number[len(phone_rules['start']):]}"
        data["phone_number"] = formatted_phone
    
    # التحقق من البريد الإلكتروني إذا تم تقديمه
    if "email" in data and data["email"]:
        # التحقق من عدم وجود بريد إلكتروني مسجل مسبقاً
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "البريد الإلكتروني مسجل بالفعل"}), 400
    
    # تشفير كلمة المرور
    hashed_password = generate_password_hash(data["password"])
    
    # إنشاء مستخدم جديد
    new_user = User(
        username=data["username"],
        password=hashed_password,
        email=data.get("email"),
        phone_number=data.get("phone_number"),
        country_code=data.get("country_code", "IQ"),
        bio=data.get("bio", "")
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # إنشاء توكن للمستخدم الجديد
    token = create_access_token(identity=new_user.id)
    
    return jsonify({
        "message": "تم تسجيل المستخدم بنجاح",
        "access_token": token,
        "user": {
            "id": new_user.id,
            "username": new_user.username
        }
    }), 201

@auth_bp.route('/in', methods=['POST'])
def login():
    data = request.get_json()
    
    # التحقق من البيانات المطلوبة
    if not all(k in data for k in ["username", "password"]):
        return jsonify({"error": "يجب توفير اسم المستخدم وكلمة المرور"}), 400
    
    # البحث عن المستخدم باسم المستخدم
    user = User.query.filter_by(username=data["username"]).first()
    
    # إذا لم يتم العثور على المستخدم، تحقق ما إذا كان تم استخدام البريد الإلكتروني
    if not user and "@" in data["username"]:
        user = User.query.filter_by(email=data["username"]).first()
    
    # إذا لم يتم العثور على المستخدم، تحقق ما إذا كان تم استخدام رقم الهاتف
    if not user and re.match(r'^\+?\d+$', data["username"]):
        user = User.query.filter_by(phone_number=data["username"]).first()
    
    # التحقق من وجود المستخدم وصحة كلمة المرور
    if user and check_password_hash(user.password, data["password"]):
        token = create_access_token(identity=user.id)
        return jsonify({
            "access_token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "profile_image": user.profile_image
            }
        }), 200
    
    return jsonify({"error": "بيانات الدخول غير صحيحة"}), 401