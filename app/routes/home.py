from flask import Blueprint, jsonify, request

home_bp = Blueprint("home", __name__)

@home_bp.route("/", methods=["GET"])
def home():
    """API الصفحة الرئيسية التي تعرض بيانات مختلفة حسب الموقع الذي يطلبها"""
                    
    return jsonify({"message": "00000001111111111111"})
