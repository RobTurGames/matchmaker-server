from flask import Flask, request, jsonify
import time

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

    print(f"🔥 Получено число: {num}")
    return jsonify({"status": "submitted"})

@app.route('/result', methods=['GET'])
def get_result():
    if not session_data["numbers"]:
        return jsonify({"min": None})

    if len(session_data["numbers"]) >= 5 or time.time() - session_data["start_time"] >= 10:
        min_val = min(session_data["numbers"])
        print(f"📤 Отправляем минимум: {min_val}")
        return jsonify({"min": min_val})
    else:
        return jsonify({"min": None})
