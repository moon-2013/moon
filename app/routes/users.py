from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Post, Follow
from werkzeug.security import generate_password_hash, check_password_hash

users_bp = Blueprint('users', __name__)

# مسار للحصول على معلومات المستخدم الحالي
@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user:
        # حساب عدد المنشورات والمتابعين والمتابَعين
        posts_count = Post.query.filter_by(user_id=user.id).count()
        followers_count = Follow.query.filter_by(followed_id=user.id).count()
        following_count = Follow.query.filter_by(follower_id=user.id).count()
        
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "bio": user.bio,
            "profile_image": user.profile_image,
            "created_at": user.created_at.isoformat(),
            "is_private": user.is_private,
            "posts_count": posts_count,
            "followers_count": followers_count,
            "following_count": following_count
        })
    
    return jsonify({"error": "المستخدم غير موجود"}), 404

# مسار للحصول على معلومات مستخدم آخر
@users_bp.route('/<string:username>', methods=['GET'])
@jwt_required()
def get_user_profile(username):
    current_user_id = get_jwt_identity()
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404
    
    # حساب عدد المنشورات والمتابعين والمتابَعين
    posts_count = Post.query.filter_by(user_id=user.id).count()
    followers_count = Follow.query.filter_by(followed_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()
    
    # التحقق مما إذا كان المستخدم الحالي يتابع هذا المستخدم
    is_following = Follow.query.filter_by(follower_id=current_user_id, followed_id=user.id).first() is not None
    
    # التحقق مما إذا كان هذا المستخدم يتابع المستخدم الحالي
    is_followed_by = Follow.query.filter_by(follower_id=user.id, followed_id=current_user_id).first() is not None
    
    # الحصول على منشورات المستخدم إذا كان الحساب عامًا أو إذا كان المستخدم الحالي يتابعه
    posts = []
    if not user.is_private or is_following or user.id == current_user_id:
        user_posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
        for post in user_posts:
            posts.append({
                "id": post.id,
                "image_url": post.image_url,
                "created_at": post.created_at.isoformat()
            })
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "bio": user.bio,
        "profile_image": user.profile_image,
        "is_private": user.is_private,
        "posts_count": posts_count,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "is_followed_by": is_followed_by,
        "posts": posts if not user.is_private or is_following or user.id == current_user_id else []
    }), 200

# مسار لتحديث معلومات المستخدم
@users_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404
    
    data = request.get_json()
    
    # تحديث البيانات المسموح بتحديثها
    if 'bio' in data:
        user.bio = data['bio']
    
    if 'profile_image' in data:
        user.profile_image = data['profile_image']
    
    if 'is_private' in data:
        user.is_private = data['is_private']
    
    # تحديث كلمة المرور إذا تم توفيرها
    if 'new_password' in data and 'current_password' in data:
        if not check_password_hash(user.password, data['current_password']):
            return jsonify({"error": "كلمة المرور الحالية غير صحيحة"}), 400
        
        user.password = generate_password_hash(data['new_password'])
    
    db.session.commit()
    
    return jsonify({"message": "تم تحديث المعلومات بنجاح"}), 200

# مسار لمتابعة مستخدم
@users_bp.route('/<int:user_id>/follow', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    current_user_id = get_jwt_identity()
    
    # لا يمكن متابعة النفس
    if current_user_id == user_id:
        return jsonify({"error": "لا يمكنك متابعة نفسك"}), 400
    
    # التحقق من وجود المستخدم
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404
    
    # التحقق من أن المستخدم لم يتابع هذا المستخدم من قبل
    existing_follow = Follow.query.filter_by(follower_id=current_user_id, followed_id=user_id).first()
    if existing_follow:
        return jsonify({"error": "أنت بالفعل تتابع هذا المستخدم"}), 400
    
    # إضافة متابعة جديدة
    new_follow = Follow(follower_id=current_user_id, followed_id=user_id)
    db.session.add(new_follow)
    db.session.commit()
    
    # الحصول على عدد المتابعين الحالي
    followers_count = Follow.query.filter_by(followed_id=user_id).count()
    
    return jsonify({
        "message": "تمت المتابعة بنجاح",
        "followers_count": followers_count
    }), 201

# مسار لإلغاء متابعة مستخدم
@users_bp.route('/<int:user_id>/unfollow', methods=['POST'])
@jwt_required()
def unfollow_user(user_id):
    current_user_id = get_jwt_identity()
    
    # التحقق من وجود المتابعة
    follow = Follow.query.filter_by(follower_id=current_user_id, followed_id=user_id).first()
    if not follow:
        return jsonify({"error": "أنت لا تتابع هذا المستخدم"}), 400
    
    # حذف المتابعة
    db.session.delete(follow)
    db.session.commit()
    
    # الحصول على عدد المتابعين الحالي
    followers_count = Follow.query.filter_by(followed_id=user_id).count()
    
    return jsonify({
        "message": "تم إلغاء المتابعة بنجاح",
        "followers_count": followers_count
    }), 200