
import json
from datetime import date, datetime
from decimal import Decimal

from app.core.db import get_db, engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker


# Make get_db() work when running this file directly
def get_session():
    Session = sessionmaker(bind=engine)
    return Session()


def safe_print(obj):
    """Pretty-print with support for dates, decimals, etc."""
    print(json.dumps(obj, indent=2, default=lambda x: str(x)))


print("🌿 Sacred Valley — Temp DB Explorer")
print("=" * 50)

# Option 1: Use your existing get_db() generator (preferred)
try:
    db = next(get_db())
    print("✅ Connected via get_db()")
except:
    print("⚠️ get_db() failed, falling back to direct session")
    db = get_session()

print("\n1. Current Users:")
users = db.execute(
    text("SELECT id, username, email, current_realm, progress_to_next, created_at FROM users")).fetchall()
for u in users:
    print(u._mapping)

print("\n2. Total Habits:")
count = db.execute(text("SELECT COUNT(*) FROM habits")).scalar()
print(f"   → {count} habits total")

print("\n3. Sample Habits (latest 5):")
habits = db.execute(text("""
                         SELECT h.id, h.name, h.frequency, u.username
                         FROM habits h
                                  JOIN users u ON h.user_id = u.id
                         ORDER BY h.created_at DESC LIMIT 5
                         """)).fetchall()
for h in habits:
    print(h._mapping)

print("\n" + "=" * 50)
print("🧙 Interactive SQL Mode (type 'quit' to exit)")

while True:
    try:
        query = input("\n🪄 SQL > ").strip()
        if query.lower() in ["quit", "exit", "q"]:
            break
        if not query:
            continue

        result = db.execute(text(query))

        # Handle SELECTs
        if query.strip().lower().startswith("select"):
            rows = result.fetchall()
            if rows:
                print("\nResults:")
                for row in rows:
                    safe_print(dict(row._mapping))
            else:
                print("No rows returned.")
        else:
            db.commit()
            print(f"✅ Query executed. Rows affected: {result.rowcount}")

    except Exception as e:
        print(f"❌ Error: {e}")

print("\n👋 Goodbye, sacred artist.")
db.close()