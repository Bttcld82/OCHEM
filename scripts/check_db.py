import sqlite3
import os

db_path = 'instance/ochem.sqlite3'

if os.path.exists(db_path):
    print(f"✅ Database trovato: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ottieni lista tabelle
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\n📊 Database creato con {len(tables)} tabelle:")
    for table in tables:
        table_name = table[0]
        print(f"  - {table_name}")
    
    conn.close()
else:
    print(f"❌ Database non trovato: {db_path}")