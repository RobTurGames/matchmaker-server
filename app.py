from flask import Flask, request, jsonify
import time
from threading import Timer

app = Flask(__name__)

# Каждая партия — список из чисел
session_data = {
    "batches": [],            # список списков: [[n1, n2, ...], [n6, n7, ...]]
    "batch_timers": []        # таймеры очистки партий
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

    # Если нет партий или последняя заполнена, создаём новую
    if not session_data["batches"] or len(session_data["batches"][-1]) >= 5:
        session_data["batches"].append([])
        batch_index = len(session_data["batches"]) - 1

        # Запускаем таймер на очистку этой партии через 20 секунд
        timer = Timer(20, lambda: clear_batch(batch_index))
        timer.start()
        session_data["batch_timers"].append(timer)
    else:
        batch_index = len(session_data["batches"]) - 1

    # Добавляем число в текущую партию
    session_data["batches"][batch_index].append(num)

    return jsonify({"status": f"number added to batch {batch_index}"})

def clear_batch(index):
    if index < len(session_data["batches"]):
        print(f"Очищаем партию {index}: {session_data['batches'][index]}")
        session_data["batches"][index] = []

@app.route('/result', methods=['GET'])
def get_result():
    active_batches = [batch for batch in session_data["batches"] if batch]
    if not active_batches:
        return jsonify({"min": None, "message": "Нет активных партий"})

    result = []
    for i, batch in enumerate(active_batches):
        result.append({
            "batch": i,
            "numbers": batch,
            "min": min(batch)
        })

    return jsonify(result)

@app.route('/clear-session', methods=['POST'])
def clear_session_endpoint():
    session_data["batches"].clear()

    # Отменяем все таймеры, если они ещё активны
    for t in session_data["batch_timers"]:
        t.cancel()

    session_data["batch_timers"].clear()
    print("Вся сессия полностью очищена")
    return jsonify({"status": "session cleared"})
