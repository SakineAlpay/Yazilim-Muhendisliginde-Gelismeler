from flask import Blueprint, request, jsonify
from models import User, UserStats
from db import db
import jwt
import os
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key-2024')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Yeni kullanıcı kaydı
    ---
    tags:
      - Kimlik Doğrulama
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: yeni_kullanici
            password:
              type: string
              example: sifre123
    responses:
      201:
        description: Kayıt başarılı
      400:
        description: Kullanıcı zaten mevcut
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Kullanıcı adı ve şifre gerekli"}), 400
    
    # Kullanıcı var mı kontrol et
    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "message": "Bu kullanıcı adı zaten mevcut"}), 400
    
    # Yeni kullanıcı oluştur
    new_user = User(username=username, level='A1', score=0)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    # Kullanıcı istatistikleri oluştur
    user_stats = UserStats(user_id=new_user.id)
    db.session.add(user_stats)
    db.session.commit()
    
    return jsonify({
        "success": True, 
        "message": "Kayıt başarılı",
        "user": {"username": username, "level": "A1"}
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Kullanıcı girişi
    ---
    tags:
      - Kimlik Doğrulama
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: user1
            password:
              type: string
              example: pass1
    responses:
      200:
        description: Giriş başarılı, JWT token döner
      401:
        description: Kullanıcı adı veya şifre hatalı
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({"success": False, "message": "Kullanıcı adı veya şifre hatalı"}), 401
    
    # JWT Token oluştur
    token = jwt.encode({
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        "success": True,
        "message": "Giriş başarılı",
        "token": token,
        "username": username,
        "level": user.level,
        "score": user.score
    }), 200

def token_required(f):
    """JWT token doğrulama decorator'ı"""
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({"success": False, "message": "Token eksik"}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.filter_by(username=data['username']).first()
            
            if not current_user:
                return jsonify({"success": False, "message": "Kullanıcı bulunamadı"}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token süresi dolmuş"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Geçersiz token"}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated