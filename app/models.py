from app.extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(20), unique=True)
    country_code = db.Column(db.String(5))
    profile_image = db.Column(db.String(255), default='default.jpg')
    bio = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_private = db.Column(db.Boolean, default=False)
    
    # ط§ظ„ط¹ظ„ط§ظ‚ط§طھ
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id', backref='followed', lazy=True, cascade='all, delete-orphan')
    following = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy=True, cascade='all, delete-orphan')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # ط§ظ„ط¹ظ„ط§ظ‚ط§طھ
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ط§ظ„ط¹ظ„ط§ظ‚ط© ظ…ط¹ ط§ظ„ظ…ط³طھط®ط¯ظ…
    user = db.relationship('User', backref='comments')

# ظ‚ط§ظ…ظˆط³ ظ„ط£ظƒظˆط§ط¯ ط§ظ„ط¯ظˆظ„ (ظ…ط®طھطµط± ظ„ظ„ط£ظ…ط«ظ„ط© ظپظ‚ط·)
COUNTRY_CODES = {
    'IQ': {'code': '964', 'start': '07', 'length': 11},
    'EG': {'code': '20', 'start': '01', 'length': 11},
    'SA': {'code': '966', 'start': '05', 'length': 10},
    'AE': {'code': '971', 'start': '05', 'length': 9},
    'US': {'code': '1', 'start': '', 'length': 10}
}