                               
from flask import Blueprint, request, jsonify
from app.extensions import db
from flask_jwt_extended import create_access_token
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
           
auth_bp = Blueprint('auth', __name__)          
                    
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data["password"])
    new_user = User(username=data["username"], email=data["email"], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201
                
@auth_bp.route('/login', methods=['POST'])
def login     (     )        :                     
    data = request       .      get_json    (        )        
    user = User.query.filter_by(email=data["email"]).first()
    if user and check_password_hash(user.password, data["password"]):
        token = create_access_token(identity=user.id)
        return jsonify({"access_token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401
                      