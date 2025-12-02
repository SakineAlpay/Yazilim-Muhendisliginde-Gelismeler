from flask import Flask, jsonify, request
import time
from datetime import date 
from flask_cors import CORS 
from datetime import date

MOCK_USERS = {
    "user1": {
        "password": "pass1", 
        "level": "B1", 
        "score": 1500, 
        "friends": ["user2", "user3"],
        "stats": {
            "words_learned": 45,
            "grammar_topics_completed": 8,
            "tests_taken": 12,
            "study_streak_days": 7,
            "total_study_time_minutes": 320
        }
    },
    "user2": {
        "password": "pass2", 
        "level": "A2", 
        "score": 950, 
        "friends": ["user1"],
        "stats": {
            "words_learned": 28,
            "grammar_topics_completed": 5,
            "tests_taken": 6,
            "study_streak_days": 3,
            "total_study_time_minutes": 180
        }
    },
    "user3": {
        "password": "pass3", 
        "level": "B1", 
        "score": 2100, 
        "friends": ["user1"],
        "stats": {
            "words_learned": 67,
            "grammar_topics_completed": 12,
            "tests_taken": 18,
            "study_streak_days": 14,
            "total_study_time_minutes": 480
        }
    },
}
MOCK_KELIMELER = [
    {"id": 1, "word": "Ephemeral", "level": "B2", "meaning": "Kısa ömürlü", "example": "Ephemeral beauty.", "pronunciation_url": "/audio/ephemeral.mp3"},
    {"id": 2, "word": "Serene", "level": "A1", "meaning": "Huzurlu", "example": "A serene landscape.", "pronunciation_url": "/audio/serene.mp3"},
    {"id": 3, "word": "Ambiguity", "level": "B1", "meaning": "Belirsizlik", "example": "The ambiguity in his words.", "pronunciation_url": "/audio/ambiguity.mp3"},
]
MOCK_GRAMMAR = [
    {"id": 1, "topic": "Present Simple", "level": "A1", "explanation": "Describes habits and facts."},
    {"id": 2, "topic": "Past Perfect", "level": "B2", "explanation": "Action completed before another past action."},
]
MOCK_TEST_SORULARI = [
    {"id": 1, "question": "The synonym of 'Happy' is...", "options": ["Sad", "Joyful", "Angry"], "answer": "Joyful"},
    {"id": 2, "question": "What is the meaning of 'Serene'?", "options": ["Angry", "Calm", "Fast"], "answer": "Calm"},
]


def create_app():

    app = Flask(__name__)
    CORS(app) 


    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if username in MOCK_USERS and MOCK_USERS[username]['password'] == password:
            user_data = MOCK_USERS[username]
            last_login = date.today().strftime("%Y-%m-%d")
            user_data['last_login'] = last_login 

            return jsonify({
                "success": True,
                "user": username,
                "level": user_data['level'],
                "stats": user_data.get('stats', {}),
                "last_login_date": last_login
            }), 200
        return jsonify({"success": False, "message": "Geçersiz kullanıcı adı veya şifre."}), 401

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"success": False, "message": "Kullanıcı adı ve şifre gereklidir."}), 400
        if username in MOCK_USERS:
            return jsonify({"success": False, "message": "Bu kullanıcı adı zaten alınmış."}), 409

        MOCK_USERS[username] = {
            "password": password, 
            "level": "A1", 
            "score": 0,
            "friends": [],
            "stats": {
                "words_learned": 0,
                "grammar_topics_completed": 0,
                "tests_taken": 0,
                "study_streak_days": 0,
                "total_study_time_minutes": 0
            }
        }

        return jsonify({
            "success": True, 
            "message": "Kayıt başarılı.",
            "level": "A1", 
            "user": username,
        }), 201

    @app.route('/api/words', methods=['GET'])
    def get_words():
        user_level = request.args.get('level', 'A1')
        filtered_words = [w for w in MOCK_KELIMELER if w['level'] == user_level or user_level == 'A1']
        return jsonify(filtered_words), 200

    @app.route('/api/words/repeat', methods=['POST'])
    def submit_word_repetition():
        data = request.get_json()
        word_id = data.get('word_id')
        username = data.get('username', 'user1')
        
        if username in MOCK_USERS:
            if 'stats' not in MOCK_USERS[username]:
                MOCK_USERS[username]['stats'] = {
                    "words_learned": 0,
                    "grammar_topics_completed": 0,
                    "tests_taken": 0,
                    "study_streak_days": 0,
                    "total_study_time_minutes": 0
                }
            MOCK_USERS[username]['stats']['words_learned'] += 1
            MOCK_USERS[username]['stats']['total_study_time_minutes'] += 2
        
        return jsonify({
            "success": True,
            "message": f"Kelime {word_id} ilerlemesi kaydedildi.",
            "stats": MOCK_USERS[username]['stats']
        }), 200

    @app.route('/api/grammar', methods=['GET'])
    def get_grammar_topics():
        user_level = request.args.get('level', 'A1')
        filtered_topics = [t for t in MOCK_GRAMMAR if t['level'] == user_level or t['level'] == 'A1']
        return jsonify(filtered_topics), 200

    @app.route('/api/grammar/quiz', methods=['POST'])
    def submit_grammar_quiz():
        data = request.get_json()
        username = data.get('username', 'user1')
        
        if username in MOCK_USERS:
            if 'stats' not in MOCK_USERS[username]:
                MOCK_USERS[username]['stats'] = {
                    "words_learned": 0,
                    "grammar_topics_completed": 0,
                    "tests_taken": 0,
                    "study_streak_days": 0,
                    "total_study_time_minutes": 0
                }
            MOCK_USERS[username]['stats']['grammar_topics_completed'] += 1
            MOCK_USERS[username]['stats']['total_study_time_minutes'] += 10
        
        return jsonify({
            "success": True,
            "score": "3/5",
            "feedback": "Pratik yapmalısın.",
            "stats": MOCK_USERS[username]['stats']
        }), 200
    
    @app.route('/api/tests/submit', methods=['POST'])
    def submit_test_answers():
        data = request.get_json()
        answers = data.get('answers', [])
        username = data.get('username', 'user1')
        total_count = len(MOCK_TEST_SORULARI)
        
        correct_count = 0
        if answers:
            correct_count = sum(1 for user_answer in answers if user_answer.get('user_answer', '').lower() == next((q['answer'].lower() for q in MOCK_TEST_SORULARI if q['id'] == user_answer.get('id')), None))
        
        if username in MOCK_USERS:
            if 'stats' not in MOCK_USERS[username]:
                MOCK_USERS[username]['stats'] = {
                    "words_learned": 0,
                    "grammar_topics_completed": 0,
                    "tests_taken": 0,
                    "study_streak_days": 0,
                    "total_study_time_minutes": 0
                }
            MOCK_USERS[username]['stats']['tests_taken'] += 1
            MOCK_USERS[username]['stats']['total_study_time_minutes'] += 15
        
        return jsonify({
            "success": True,
            "total_questions": total_count,
            "correct_answers": correct_count,
            "score": f"{correct_count}/{total_count}",
            "feedback": "Başarılı bir test oturumu!",
            "stats": MOCK_USERS[username]['stats']
        }), 200

    @app.route('/api/stats/<username>', methods=['GET'])
    def get_user_stats(username):
        user = MOCK_USERS.get(username)
        if not user:
            return jsonify({"success": False, "message": "Kullanıcı bulunamadı."}), 404
        
        stats = user.get('stats', {
            "words_learned": 0,
            "grammar_topics_completed": 0,
            "tests_taken": 0,
            "study_streak_days": 0,
            "total_study_time_minutes": 0
        })
        
        return jsonify({
            "success": True,
            "username": username,
            "stats": stats,
            "level": user['level'],
            "score": user['score']
        }), 200

    @app.route('/api/speech/analyze', methods=['POST'])
    def analyze_speech():
        return jsonify({
            "success": True,
            "analysis": "Telaffuzunuz %85 doğru.",
            "pronunciation_score": 85
        }), 200

    @app.route('/api/writing/check', methods=['POST'])
    def check_writing():
        data = request.get_json()
        text = data.get('text', '')

        if 'has went' in text.lower():
            corrections = ["Hata: 'has went' yerine 'has gone' kullanmalısın."]
        else:
            corrections = ["Mükemmel, cümlenizde büyük hata yok."]
            
        return jsonify({
            "success": True,
            "corrections": corrections,
            "grade": "B+"
        }), 200

    @app.route('/api/scoreboard', methods=['GET'])
    def get_scoreboard():
        scoreboard = []
        for username, data in MOCK_USERS.items():
            scoreboard.append({
                "username": username,
                "score": data['score'],
                "level": data['level']
            })
        
        scoreboard.sort(key=lambda x: x['score'], reverse=True)
        
        return jsonify(scoreboard), 200

    @app.route('/api/profile/<username>', methods=['GET'])
    def get_user_profile(username):
        user = MOCK_USERS.get(username)
        if not user:
            return jsonify({"success": False, "message": "Kullanıcı bulunamadı."}), 404
        
        return jsonify({
            "username": username,
            "level": user['level'],
            "score": user['score'],
            "friends_count": len(user['friends']),
            "stats": user.get('stats', {})
        }), 200

    @app.route('/api/social/add_friend', methods=['POST'])
    def add_friend():
        data = request.get_json()
        current_user = data.get('current_user', 'user1')
        friend_to_add = data.get('friend_to_add')

        if friend_to_add not in MOCK_USERS:
            return jsonify({"success": False, "message": "Eklenecek kullanıcı bulunamadı."}), 404
        
        if friend_to_add not in MOCK_USERS[current_user]['friends']:
            MOCK_USERS[current_user]['friends'].append(friend_to_add)
        
        if current_user not in MOCK_USERS[friend_to_add]['friends']:
            MOCK_USERS[friend_to_add]['friends'].append(current_user)

        return jsonify({"success": True, "message": f"{friend_to_add} arkadaş olarak eklendi."}), 200

    @app.route('/api/social/friends', methods=['GET'])
    def get_friends_list():
        current_user = request.args.get('current_user', 'user1') 
        user_data = MOCK_USERS.get(current_user)
        
        if not user_data:
            return jsonify({"success": False, "message": "Kullanıcı bulunamadı."}), 404
            
        friends_list = []
        for friend_username in user_data['friends']:
            friend_data = MOCK_USERS.get(friend_username, {})
            friends_list.append({
                "username": friend_username,
                "score": friend_data.get('score', 0),
                "level": friend_data.get('level', 'N/A')
            })
            
        return jsonify(friends_list), 200

    return app


if __name__ == '__main__':
    app = create_app()
app.run(host='0.0.0.0', debug=True, port=5000)