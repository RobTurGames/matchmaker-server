from flask import Flask, request, jsonify
import time
from threading import Timer

app = Flask(__name__)

session_data = {
    "batches": [],
    "batch_timers": [],
    "batch_expiration": []
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
    print(f"Получено число: {num}")

    if not session_data["batches"] or len(session_data["batches"][-1]) >= 5:
        session_data["batches"].append([])
        session_data["batch_expiration"].append(False)

    batch_index = len(session_data["batches"]) - 1
    session_data["batches"][batch_index].append(num)

    if not session_data["batch_expiration"][batch_index]:
        timer = Timer(20, lambda: clear_batch(batch_index))
        timer.start()

        session_data["batch_timers"].append(timer)
        session_data["batch_expiration"][batch_index] = True
        print(f"Таймер очистки запущен для партии #{batch_index}")

    return jsonify({"status": f"number added to batch {batch_index}"})

def clear_batch(index):
    if index < len(session_data["batches"]):
        print(f"Очищаем партию {index}: {session_data['batches'][index]}")
        session_data["batches"][index] = []

@app.route('/result', methods=['GET'])
def get_result():
    batch_param = request.args.get('batch')
    if batch_param is None:
        return jsonify({"error": "Missing batch index"}), 400

    try:
        batch_index = int(batch_param)
    except ValueError:
        return jsonify({"error": "Invalid batch index"}), 400

    if batch_index < 0 or batch_index >= len(session_data["batches"]):
        return jsonify({"min": None, "message": "Batch not found"})

    batch = session_data["batches"][batch_index]
    if not batch:
        return jsonify({"min": None, "message": "Batch is empty"})

    return jsonify({
        "batch": batch_index,
        "min": min(batch),
        "numbers": batch
    })

@app.route('/clear-session', methods=['POST'])
def clear_session_endpoint():
    session_data["batches"].clear()

    for t in session_data["batch_timers"]:
        t.cancel()

    session_data["batch_timers"].clear()
    print("Вся сессия полностью очищена")
    return jsonify({"status": "session cleared"})
    
@app.route('/clear-by-number', methods=['POST'])
def clear_by_number():
    data = request.get_json()
    if not data or 'number' not in data:
        return jsonify({"error": "Invalid input"}), 400

    num = int(data['number'])

    for i, batch in enumerate(session_data["batches"]):
        if num in batch:
            session_data["batches"][i] = []

            if i < len(session_data["batch_timers"]):
                session_data["batch_timers"][i].cancel()

            if "batch_expiration" in session_data and i < len(session_data["batch_expiration"]):
                session_data["batch_expiration"][i] = False

            print(f"Число {num} найдено — партия #{i} очищена.")
            return jsonify({"status": f"batch {i} cleared", "number": num})

    print(f"Число {num} не найдено ни в одной партии.")
    return jsonify({"status": "not found", "number": num})
