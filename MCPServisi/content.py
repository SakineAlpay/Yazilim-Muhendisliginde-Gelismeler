from flask import Blueprint, jsonify, request
from models import Word, User, UserStats, Friendship
from db import db
from resources.auth import token_required
content_bp = Blueprint('content', __name__)

@content_bp.route('/words', methods=['GET'])
def get_words(): # Şimdilik testi kolaylaştırmak için token_required'ı kaldırdık
    words = Word.query.all()
    words_list = [{
        'id': w.id,
        'word': w.word,
        'meaning': w.meaning,
        'level': w.level,
        'example': w.example if w.example else "Örnek cümle bulunmuyor."
    } for w in words]
    
    return jsonify({"success": True, "words": words_list}), 200
@content_bp.route('/stats/<username>', methods=['GET'])
@token_required
def get_stats(current_user, username):
    """
    Kullanıcı istatistiklerini getir
    ---
    tags:
      - İstatistikler ve Sosyal
    security:
      - Bearer: []
    parameters:
      - in: path
        name: username
        required: true
        type: string
    responses:
      200:
        description: Kullanıcı istatistikleri
    """
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"success": False, "message": "Kullanıcı bulunamadı"}), 404
    
    stats = user.stats
    
    return jsonify({
        "success": True,
        "level": user.level,
        "stats": {
            "words_learned": stats.words_learned if stats else 0,
            "grammar_topics_completed": stats.grammar_topics_completed if stats else 0,
            "tests_taken": stats.tests_taken if stats else 0,
            "study_streak_days": stats.study_streak_days if stats else 0,
            "total_study_time_minutes": stats.total_study_time_minutes if stats else 0
        }
    }), 200

@content_bp.route('/scoreboard', methods=['GET'])
def get_scoreboard():
    """
    Global skor tahtası (Public - Token gerektirmez)
    ---
    tags:
      - İstatistikler ve Sosyal
    responses:
      200:
        description: Skor tahtası
    """
    users = User.query.order_by(User.score.desc()).limit(10).all()
    
    scoreboard = [{
        'username': u.username,
        'score': u.score,
        'level': u.level
    } for u in users]
    
    return jsonify(scoreboard), 200

@content_bp.route('/profile/<username>', methods=['GET'])
@token_required
def get_profile(current_user, username):
    """
    Kullanıcı profili
    ---
    tags:
      - İstatistikler ve Sosyal
    security:
      - Bearer: []
    """
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"success": False, "message": "Kullanıcı bulunamadı"}), 404
    
    return jsonify({
        "success": True,
        "profile": {
            "username": user.username,
            "level": user.level,
            "score": user.score,
            "created_at": user.created_at.isoformat()
        }
    }), 200

@content_bp.route('/social/friends', methods=['GET'])
@token_required
def get_friends(current_user):
    """
    Arkadaş listesi
    ---
    tags:
      - İstatistikler ve Sosyal
    security:
      - Bearer: []
    """
    friendships = Friendship.query.filter_by(user_id=current_user.id).all()
    
    friends_list = []
    for friendship in friendships:
        friend = User.query.get(friendship.friend_id)
        if friend:
            friends_list.append({
                'username': friend.username,
                'level': friend.level,
                'score': friend.score
            })
    
    return jsonify({"success": True, "friends": friends_list}), 200