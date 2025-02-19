                                   
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
                    
users_bp = Blueprint('users', __name__)
                     
@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return jsonify({"id": user.id, "username": user.username, "email": user.email})
    return jsonify({"error": "User not found"}), 404
             