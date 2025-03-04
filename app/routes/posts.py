from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Post, User, Like, Comment, Follow
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import uuid
from datetime import datetime

posts_bp = Blueprint('posts', __name__)

# مسار للحصول على منشورات الصفحة الرئيسية (الخلاصة)
@posts_bp.route('/feed', methods=['GET'])
@jwt_required()
def get_feed():
    current_user_id = get_jwt_identity()
    
    # الحصول على قائمة المستخدمين الذين يتبعهم المستخدم الحالي
    following_ids = [follow.followed_id for follow in Follow.query.filter_by(follower_id=current_user_id).all()]
    
    # إضافة معرّف المستخدم الحالي للحصول على منشوراته أيضًا
    following_ids.append(current_user_id)
    
    # الحصول على المنشورات من المستخدمين المتابعين، مرتبة حسب التاريخ
    posts = Post.query.filter(Post.user_id.in_(following_ids)).order_by(Post.created_at.desc()).limit(20).all()
    
    result = []
    for post in posts:
        # الحصول على معلومات الكاتب
        author = User.query.get(post.user_id)
        
        # التحقق مما إذا كان المستخدم الحالي قد أعجب بالمنشور
        is_liked = Like.query.filter_by(user_id=current_user_id, post_id=post.id).first() is not None
        
        # عدد الإعجابات والتعليقات
        likes_count = Like.query.filter_by(post_id=post.id).count()
        comments_count = Comment.query.filter_by(post_id=post.id).count()
        
        # الحصول على أحدث 3 تعليقات
        recent_comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).limit(3).all()
        comments_list = []
        for comment in recent_comments:
            comment_user = User.query.get(comment.user_id)
            comments_list.append({
                "id": comment.id,
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
                "user": {
                    "id": comment_user.id,
                    "username": comment_user.username,
                    "profile_image": comment_user.profile_image
                }
            })
        
        result.append({
            "id": post.id,
            "image_url": post.image_url,
            "caption": post.caption,
            "created_at": post.created_at.isoformat(),
            "author": {
                "id": author.id,
                "username": author.username,
                "profile_image": author.profile_image
            },
            "is_liked": is_liked,
            "likes_count": likes_count,
            "comments_count": comments_count,
            "recent_comments": comments_list
        })
    
    return jsonify(result), 200

# مسار لإنشاء منشور جديد
@posts_bp.route('/', methods=['POST'])
@jwt_required()
def create_post():
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    if not data or 'image_url' not in data:
        return jsonify({"error": "يجب توفير صورة للمنشور"}), 400
    
    new_post = Post(
        image_url=data['image_url'],
        caption=data.get('caption', ''),
        user_id=current_user_id
    )
    
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({
        "message": "تم إنشاء المنشور بنجاح",
        "post": {
            "id": new_post.id,
            "image_url": new_post.image_url,
            "caption": new_post.caption,
            "created_at": new_post.created_at.isoformat()
        }
    }), 201

# مسار للإعجاب بمنشور
@posts_bp.route('/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    current_user_id = get_jwt_identity()
    
    # التحقق من وجود المنشور
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "المنشور غير موجود"}), 404
    
    # التحقق من أن المستخدم لم يعجب بالمنشور من قبل
    existing_like = Like.query.filter_by(user_id=current_user_id, post_id=post_id).first()
    if existing_like:
        return jsonify({"error": "لقد أعجبت بهذا المنشور من قبل"}), 400
    
    # إضافة إعجاب جديد
    new_like = Like(user_id=current_user_id, post_id=post_id)
    db.session.add(new_like)
    db.session.commit()
    
    # الحصول على عدد الإعجابات الحالي
    likes_count = Like.query.filter_by(post_id=post_id).count()
    
    return jsonify({
        "message": "تم الإعجاب بالمنشور بنجاح",
        "likes_count": likes_count
    }), 201

# مسار لإلغاء الإعجاب بمنشور
@posts_bp.route('/<int:post_id>/unlike', methods=['POST'])
@jwt_required()
def unlike_post(post_id):
    current_user_id = get_jwt_identity()
    
    # التحقق من وجود الإعجاب
    like = Like.query.filter_by(user_id=current_user_id, post_id=post_id).first()
    if not like:
        return jsonify({"error": "لم تعجب بهذا المنشور من قبل"}), 400
    
    # حذف الإعجاب
    db.session.delete(like)
    db.session.commit()
    
    # الحصول على عدد الإعجابات الحالي
    likes_count = Like.query.filter_by(post_id=post_id).count()
    
    return jsonify({
        "message": "تم إلغاء الإعجاب بالمنشور بنجاح",
        "likes_count": likes_count
    }), 200

# مسار لإضافة تعليق
@posts_bp.route('/<int:post_id>/comment', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    current_user_id = get_jwt_identity()
    
    # التحقق من وجود المنشور
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "المنشور غير موجود"}), 404
    
    data = request.get_json()
    if not data or 'content' not in data or not data['content'].strip():
        return jsonify({"error": "محتوى التعليق مطلوب"}), 400
    
    # إضافة تعليق جديد
    new_comment = Comment(
        content=data['content'],
        user_id=current_user_id,
        post_id=post_id
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    # الحصول على معلومات المستخدم
    user = User.query.get(current_user_id)
    
    return jsonify({
        "message": "تم إضافة التعليق بنجاح",
        "comment": {
            "id": new_comment.id,
            "content": new_comment.content,
            "created_at": new_comment.created_at.isoformat(),
            "user": {
                "id": user.id,
                "username": user.username,
                "profile_image": user.profile_image
            }
        }
    }), 201

# مسار للحصول على تعليقات منشور
@posts_bp.route('/<int:post_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(post_id):
    # التحقق من وجود المنشور
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "المنشور غير موجود"}), 404
    
    # الحصول على التعليقات
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    
    result = []
    for comment in comments:
        user = User.query.get(comment.user_id)
        result.append({
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at.isoformat(),
            "user": {
                "id": user.id,
                "username": user.username,
                "profile_image": user.profile_image
            }
        })
    
    return jsonify(result), 200