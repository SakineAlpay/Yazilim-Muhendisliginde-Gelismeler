from flask import Flask, jsonify, request
import time
from datetime import date, datetime, timedelta
from flask_cors import CORS 
import jwt
from functools import wraps

# JWT için gizli anahtar
SECRET_KEY = "super-secret-key-2024"

# --- SAHTE VERİTABANI ---
MOCK_USERS = {
    "user1": {
        "password": "pass1", "level": "B1", "score": 1500, "friends": ["user2", "user3"],
        "stats": { "words_learned": 45, "grammar_topics_completed": 8, "tests_taken": 12, "study_streak_days": 7, "total_study_time_minutes": 320 }
    },
    "user2": {
        "password": "pass2", "level": "A2", "score": 950, "friends": ["user1"],
        "stats": { "words_learned": 28, "grammar_topics_completed": 5, "tests_taken": 6, "study_streak_days": 3, "total_study_time_minutes": 180 }
    },
    "user3": {
        "password": "pass3", "level": "B1", "score": 2100, "friends": ["user1"],
        "stats": { "words_learned": 67, "grammar_topics_completed": 12, "tests_taken": 18, "study_streak_days": 14, "total_study_time_minutes": 480 }
    },
}

MOCK_KELIMELER = [
    {"id": 1, "word": "Ephemeral", "level": "B2", "meaning": "Kısa ömürlü", "example": "Ephemeral beauty."},
    {"id": 2, "word": "Serene", "level": "A1", "meaning": "Huzurlu", "example": "A serene landscape."},
    {"id": 3, "word": "Ambiguity", "level": "B1", "meaning": "Belirsizlik", "example": "The ambiguity in his words."},
    {"id": 4, "word": "Resilient", "level": "B1", "meaning": "Dirençli", "example": "She is very resilient."},
    {"id": 5, "word": "Eloquent", "level": "C1", "meaning": "Güzel konuşan", "example": "An eloquent speech."},
]

MOCK_GRAMMAR = [
    {"id": 1, "topic": "Present Simple", "level": "A1", "explanation": "Geniş zaman: Alışkanlıklar ve genel doğrular için kullanılır."},
    {"id": 2, "topic": "Past Perfect", "level": "B2", "explanation": "Miş'li Geçmiş Zaman: Geçmişte yapılan bir eylemden daha önce yapılanı anlatır."},
    {"id": 3, "topic": "Conditionals", "level": "B1", "explanation": "Koşul cümleleri (If clauses): Eğer şöyle olursa, böyle olur."},
]

MOCK_TEST_SORULARI = [
    {"id": 1, "question": "'Happy' kelimesinin eş anlamlısı nedir?", "options": ["Sad", "Joyful", "Angry"], "answer": "Joyful"},
    {"id": 2, "question": "'Serene' kelimesi ne anlama gelir?", "options": ["Sinirli", "Huzurlu", "Hızlı"], "answer": "Huzurlu"},
    {"id": 3, "question": "Hangi cümle 'Present Simple' (Geniş Zaman) yapısındadır?", "options": ["I am going.", "I went.", "I go."], "answer": "I go."},
]

# --- YARDIMCI FONKSİYONLAR ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except:
                return jsonify({"message": "Token geçersiz!"}), 401
        if not token:
            return jsonify({"message": "Token yok!"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['username']
            if current_user not in MOCK_USERS:
                raise Exception("User not found")
        except:
            return jsonify({"message": "Token geçersiz veya süresi dolmuş!"}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS"])

    # --- AUTH ENDPOINTS ---
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if username in MOCK_USERS and MOCK_USERS[username]['password'] == password:
            token = jwt.encode({'username': username, 'exp': datetime.utcnow() + timedelta(hours=24)}, SECRET_KEY, algorithm="HS256")
            return jsonify({"success": True, "token": token, "user": username, "stats": MOCK_USERS[username]['stats']})
        return jsonify({"message": "Hatalı giriş"}), 401

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data.get('username')
        if username in MOCK_USERS: return jsonify({"message": "Kullanıcı zaten var"}), 409
        MOCK_USERS[username] = {
            "password": data.get('password'), "level": "A1", "score": 0, "friends": [],
            "stats": { "words_learned": 0, "grammar_topics_completed": 0, "tests_taken": 0, "study_streak_days": 1, "total_study_time_minutes": 0 }
        }
        return jsonify({"success": True, "message": "Kayıt başarılı"}), 201

    # --- WORDS ENDPOINT ---
    @app.route('/api/words', methods=['GET'])
    @token_required
    def get_words(current_user):
        return jsonify({"success": True, "words": MOCK_KELIMELER})

    # --- GRAMMAR ENDPOINTS ---
    @app.route('/api/grammar', methods=['GET'])
    @token_required
    def get_grammar(current_user):
        return jsonify({"success": True, "topics": MOCK_GRAMMAR, "user": current_user})

    @app.route('/api/grammar/quiz', methods=['POST'])
    @token_required
    def complete_grammar(current_user):
        MOCK_USERS[current_user]['stats']['grammar_topics_completed'] += 1
        MOCK_USERS[current_user]['score'] += 50
        return jsonify({"success": True})

    # --- TESTS ENDPOINTS ---
    @app.route('/api/tests', methods=['GET'])
    @token_required
    def get_tests(current_user):
        # Cevapları gizleyerek gönderiyoruz
        safe_questions = [{"id": q['id'], "question": q['question'], "options": q['options']} for q in MOCK_TEST_SORULARI]
        return jsonify({"success": True, "tests": safe_questions})

    @app.route('/api/tests/submit', methods=['POST'])
    @token_required
    def submit_test(current_user):
        answers = request.get_json().get('answers', [])
        correct = 0
        for ans in answers:
            question = next((q for q in MOCK_TEST_SORULARI if q['id'] == ans['id']), None)
            if question and question['answer'] == ans['user_answer']:
                correct += 1
        
        score_earned = correct * 10
        MOCK_USERS[current_user]['score'] += score_earned
        MOCK_USERS[current_user]['stats']['tests_taken'] += 1
        
        return jsonify({
            "success": True, 
            "correct_answers": correct, 
            "total_questions": len(MOCK_TEST_SORULARI),
            "score": score_earned,
            "feedback": "Harika iş!",
            "stats": MOCK_USERS[current_user]['stats']
        })

    # --- SCOREBOARD (PUBLIC) ---
    @app.route('/api/scoreboard', methods=['GET'])
    def get_scoreboard():
        board = []
        for u, data in MOCK_USERS.items():
            board.append({"username": u, "score": data['score'], "level": data['level']})
        board.sort(key=lambda x: x['score'], reverse=True)
        return jsonify(board)

    # --- FRIENDS ENDPOINT ---
    @app.route('/api/social/friends', methods=['GET'])
    @token_required
    def get_friends(current_user):
        friends = []
        for friend_name in MOCK_USERS[current_user]['friends']:
            if friend_name in MOCK_USERS:
                f_data = MOCK_USERS[friend_name]
                friends.append({"username": friend_name, "score": f_data['score'], "level": f_data['level']})
        return jsonify(friends)

    # --- STATS ENDPOINT ---
    @app.route('/api/stats/<username>', methods=['GET'])
    @token_required
    def get_stats(current_user, username):
        if username not in MOCK_USERS: return jsonify({"message": "User not found"}), 404
        return jsonify({"success": True, "stats": MOCK_USERS[username]['stats']})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', debug=True, port=5000)
