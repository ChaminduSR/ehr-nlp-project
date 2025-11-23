import sqlite3
import os

# Get absolute path to database
db_path = os.path.join(os.path.dirname(__file__), 'clinical_ehr.db')
schema_path = os.path.join(os.path.dirname(__file__), 'init_schema.sql')

print(f"Initializing database at: {db_path}")

# Connect and execute schema
conn = sqlite3.connect(db_path)
with open(schema_path, 'r') as f:
    conn.executescript(f.read())
conn.commit()

# Verify tables
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"✅ Successfully created {len(tables)} tables:")
for table in tables:
    print(f"   - {table}")
conn.close()
