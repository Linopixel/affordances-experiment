# processing/export_raw.py
import sqlite3
import pandas as pd
import os

def export_raw_data():
    db_path = os.path.join('data', 'raw', 'experiment.db')
    csv_path = os.path.join('data', 'raw', 'raw_events.csv')
    
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM events ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    
    column_names = [description[0] for description in cursor.description]
    
    conn.close()
    
    df = pd.DataFrame(rows, columns=column_names)
    
    # Filtro para desconsiderar sessões piloto / testes (P00)
    df = df[df['participant_id'] != 'P00']
    
    df.to_csv(csv_path, index=False, encoding='utf-8')
    
    n_events = len(df)
    n_participants = df['participant_id'].nunique()
    n_sessions = df['session_id'].nunique()
    
    print(f"[EXPORT] ✅ Concluído.")
    print(f"  - Eventos exportados: {n_events}")
    print(f"  - Participantes únicos: {n_participants}")
    print(f"  - Sessões únicas: {n_sessions}")
    print(f"  - Arquivo salvo em: {csv_path}")

if __name__ == '__main__':
    export_raw_data()
