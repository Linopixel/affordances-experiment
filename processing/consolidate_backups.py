# processing/consolidate_backups.py
import sqlite3
import os
import glob

def consolidate_backups():
    backup_dir = os.path.join('data', 'raw', 'backups')
    consolidated_db_path = os.path.join('data', 'raw', 'consolidated.db')
    
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_files = glob.glob(os.path.join(backup_dir, 'experiment_*.db'))
    
    if not backup_files:
        print("[CONSOLIDATE] ⚠️ Nenhum arquivo de backup encontrado em data/raw/backups/.")
        return

    print(f"[CONSOLIDATE] Encontrados {len(backup_files)} arquivo(s) de backup.")
    print(f"[CONSOLIDATE] Iniciando consolidação em: {consolidated_db_path}\n")

    conn_consolidated = sqlite3.connect(consolidated_db_path)
    cursor_consolidated = conn_consolidated.cursor()
    
    cursor_consolidated.execute('''
        CREATE TABLE IF NOT EXISTS events (
            event_id          TEXT PRIMARY KEY,
            participant_id    TEXT NOT NULL,
            session_id        TEXT NOT NULL,
            condition         TEXT NOT NULL,
            condition_order   TEXT NOT NULL,
            task_id           TEXT,
            event_type        TEXT NOT NULL,
            element_id        TEXT,
            timestamp         TEXT NOT NULL,
            server_timestamp  TEXT NOT NULL,
            elapsed_ms        REAL,
            x                 REAL,
            y                 REAL,
            metadata          TEXT
        )
    ''')
    conn_consolidated.commit()

    total_events_imported = 0

    for backup_file in sorted(backup_files):
        filename = os.path.basename(backup_file)
        try:
            conn_backup = sqlite3.connect(backup_file)
            cursor_backup = conn_backup.cursor()
            
            cursor_backup.execute("SELECT * FROM events")
            rows = cursor_backup.fetchall()
            
            if not rows:
                print(f"  - {filename}: 0 eventos (vazio)")
                conn_backup.close()
                continue
            
            cursor_consolidated.executemany('''
                INSERT OR IGNORE INTO events (
                    event_id, participant_id, session_id, condition, condition_order,
                    task_id, event_type, element_id, timestamp, server_timestamp,
                    elapsed_ms, x, y, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', rows)
            
            conn_consolidated.commit()
            
            print(f"  - {filename}: {len(rows)} eventos processados.")
            total_events_imported += len(rows)
            
            conn_backup.close()
            
        except Exception as e:
            print(f"  - {filename}: ERRO ao processar ({e})")

    conn_consolidated.close()
    
    conn_final_check = sqlite3.connect(consolidated_db_path)
    cursor_final = conn_final_check.cursor()
    cursor_final.execute("SELECT COUNT(*) FROM events")
    final_count = cursor_final.fetchone()[0]
    conn_final_check.close()

    print("\n" + "="*60)
    print("[CONSOLIDATE] ✅ Concluído com sucesso.")
    print(f"  - Total de eventos processados dos backups: {total_events_imported}")
    print(f"  - Total de eventos únicos no banco consolidado: {final_count}")
    print(f"  - Arquivo salvo em: {consolidated_db_path}")
    print("="*60)
    print("\nPRÓXIMO PASSO:")
    print("1. Renomeie 'consolidated.db' para 'experiment.db' (ou ajuste o pipeline).")
    print("2. Execute: python processing/run_all.py")

if __name__ == '__main__':
    consolidate_backups()
