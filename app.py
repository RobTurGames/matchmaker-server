from flask import Flask, request, jsonify
import time
from threading import Timer

app = Flask(__name__)
session_data = {
    "numbers": [],
    "start_time": None
}

@app.route('/')
def home():
    return "Server is running"

@app.route('/submit', methods=['POST'])
def submit_number():
    data = request.get_json()
    if not data or 'number' not in data:
        return jsonify({"error": "Invalid input"}), 400

    num = int(data['number'])

    if session_data["start_time"] is None:
        session_data["start_time"] = time.time()

    if len(session_data["numbers"]) < 5:
        session_data["numbers"].append(num)

    print(f"Получено число: {num}")
    return jsonify({"status": "submitted"})

@app.route('/result', methods=['GET'])
def get_result():
    now = time.time()

    if not session_data["numbers"]:
        print("Список пуст")
        return jsonify({"min": None})

    elapsed = now - session_data["start_time"] if session_data["start_time"] else 0

    if len(session_data["numbers"]) >= 5 or elapsed >= 5:
        min_val = min(session_data["numbers"])
        print(f"Отправляем минимум: {min_val}")
        Timer(15, clear_session_endpoint).start()
        return jsonify({"min": min_val})
    else:
        print(f"Ждём игроков... ({elapsed:.1f} сек)")
        return jsonify({"min": None})

@app.route('/clear-session', methods=['POST'])
def clear_session_endpoint():
    session_data["numbers"].clear()
    session_data["start_time"] = None
    print("Сессия очищена")
    return jsonify({"status": "cleared"})
