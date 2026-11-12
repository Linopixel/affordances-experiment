# backend/app.py
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timezone
import os
import database

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')

REQUIRED_FIELDS = [
    'event_id', 'participant_id', 'session_id', 
    'condition', 'condition_order', 'event_type', 'timestamp'
]

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/a')
@app.route('/a.html')
def serve_a():
    return send_from_directory(app.static_folder, 'a.html')

@app.route('/b')
@app.route('/b.html')
def serve_b():
    return send_from_directory(app.static_folder, 'b.html')

@app.route('/event', methods=['POST'])
def receive_event():
    if not request.is_json:
        return jsonify({"error": "Content-Type deve ser application/json"}), 400

    data = request.get_json()

    missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
    if missing_fields:
        return jsonify({"error": f"Campos obrigatórios ausentes: {', '.join(missing_fields)}"}), 400

    data['server_timestamp'] = datetime.now(timezone.utc).isoformat(timespec='milliseconds')

    try:
        database.insert_event(data)
        task_id = data.get('task_id', 'N/A')
        print(f"[SERVER] ✅ Evento persistido: {data['event_type']} | ID: {data['event_id']} | Task: {task_id}")
        return jsonify({"status": "ok", "event_id": data['event_id']}), 200
    
    except Exception as e:
        print(f"[SERVER] ❌ Erro ao persistir evento no banco: {e}")
        return jsonify({"error": "Erro interno ao salvar no banco de dados"}), 500

if __name__ == '__main__':
    database.init_db()
    print(f"[SERVER] Banco de dados inicializado em: {database.DB_PATH}")
    app.run(host='127.0.0.1', port=5000, debug=True)
