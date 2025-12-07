Migration: add `pg_scale_1_10` to `joint_assessment_summaries`

Run this only if you have existing databases that need the new column.

SQL (SQLite):

```sql
ALTER TABLE joint_assessment_summaries ADD COLUMN pg_scale_1_10 INTEGER;
```

Notes:
- This is safe for SQLite (adds NULLable column).
- After running the ALTER, new code will start inserting `pg_scale_1_10` values.
- Consider backfilling from any existing patient-global values if you stored them elsewhere.

How to run (from project root, with Python available):

```powershell
# Open a Python REPL that executes the SQL against your DB file (example assumes sqlite file at backend/database/app.db)
python - <<'PY'
import sqlite3
conn = sqlite3.connect('backend/database/app.db')
cur = conn.cursor()
cur.execute("ALTER TABLE joint_assessment_summaries ADD COLUMN pg_scale_1_10 INTEGER;")
conn.commit()
conn.close()
print('Migration applied')
PY
```

If you use a different DB engine (Postgres/MySQL), adapt the SQL to the engine's ALTER TABLE syntax and ensure you have backups before running migrations.
