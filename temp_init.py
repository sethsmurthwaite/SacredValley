# check_db.py
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://sacred:valley123@localhost:5432/sacredvalley")
with engine.connect() as conn:
    users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
    realms = conn.execute(text("SELECT COUNT(*) FROM realms")).scalar()
    paths = conn.execute(text("SELECT COUNT(*) FROM paths")).scalar()
    print(f"✅ Database healthy!")
    print(f"   Users: {users} | Realms: {realms} | Paths: {paths}")
    print(f"   Ready for sacred artists to begin cultivation!")


















# # temp_init.py — STAND-ALONE VERSION (no imports needed)
# from sqlalchemy import create_engine, text
#
# # Connect to your running Docker Postgres
# engine = create_engine("postgresql://sacred:valley123@localhost:5432/sacredvalley")
#
# # FULL SCHEMA — paste exactly as-is (this is the complete Cradle schema)
# schema_sql = """
#              -- Users
#              CREATE TABLE IF NOT EXISTS users \
#              ( \
#                  id \
#                  SERIAL \
#                  PRIMARY \
#                  KEY, \
#                  username \
#                  VARCHAR \
#              ( \
#                  50 \
#              ) UNIQUE NOT NULL,
#                  email VARCHAR \
#              ( \
#                  100 \
#              ) UNIQUE NOT NULL,
#                  password_hash VARCHAR \
#              ( \
#                  255 \
#              ) NOT NULL,
#                  path_id INTEGER,
#                  current_realm VARCHAR \
#              ( \
#                  20 \
#              ) NOT NULL DEFAULT 'Mortal',
#                  progress_to_next DECIMAL \
#              ( \
#                  5, \
#                  2 \
#              ) DEFAULT 0.00 CHECK \
#              ( \
#                  progress_to_next \
#                  >= \
#                  0 \
#                  AND \
#                  progress_to_next \
#                  <= \
#                  100 \
#              ),
#                  madra_type VARCHAR \
#              ( \
#                  50 \
#              ) DEFAULT 'Pure',
#                  clan_id INTEGER,
#                  total_habits_completed INTEGER DEFAULT 0,
#                  created_at TIMESTAMP DEFAULT NOW \
#              ( \
#              ),
#                  updated_at TIMESTAMP DEFAULT NOW \
#              ( \
#              )
#                  );
#
# -- Paths (Blackflame, Pure Madra, etc.)
#              CREATE TABLE IF NOT EXISTS paths \
#              ( \
#                  id \
#                  SERIAL \
#                  PRIMARY \
#                  KEY, \
#                  name \
#                  VARCHAR \
#              ( \
#                  100 \
#              ) NOT NULL,
#                  madra_type VARCHAR \
#              ( \
#                  50 \
#              ) NOT NULL,
#                  description TEXT
#                  );
#
# -- Realms (Copper → Monarch)
#              CREATE TABLE IF NOT EXISTS realms \
#              ( \
#                  id \
#                  SERIAL \
#                  PRIMARY \
#                  KEY, \
#                  name \
#                  VARCHAR \
#              ( \
#                  20 \
#              ) UNIQUE NOT NULL,
#                  order_num INTEGER NOT NULL
#                  );
#
# -- Habits
#              CREATE TABLE IF NOT EXISTS habits \
#              ( \
#                  id \
#                  SERIAL \
#                  PRIMARY \
#                  KEY, \
#                  user_id \
#                  INTEGER \
#                  REFERENCES \
#                  users \
#              ( \
#                  id \
#              ) ON DELETE CASCADE,
#                  name VARCHAR \
#              ( \
#                  100 \
#              ) NOT NULL,
#                  description TEXT,
#                  frequency VARCHAR \
#              ( \
#                  20 \
#              ) DEFAULT 'daily',
#                  streak_current INTEGER DEFAULT 0,
#                  streak_max INTEGER DEFAULT 0,
#                  created_at TIMESTAMP DEFAULT NOW \
#              ( \
#              )
#                  );
#
# -- Time-series completions (TimescaleDB hypertable)
#              CREATE TABLE IF NOT EXISTS habit_completions \
#              ( \
#                  id \
#                  BIGSERIAL, \
#                  user_id \
#                  INTEGER \
#                  REFERENCES \
#                  users \
#              ( \
#                  id \
#              ) ON DELETE CASCADE,
#                  habit_id INTEGER REFERENCES habits \
#              ( \
#                  id \
#              ) \
#                ON DELETE CASCADE,
#                  completed_at TIMESTAMP NOT NULL DEFAULT NOW \
#              ( \
#              ),
#                  PRIMARY KEY \
#              ( \
#                  id, \
#                  completed_at \
#              )
#                  );
#
# -- Clans
#              CREATE TABLE IF NOT EXISTS clans \
#              ( \
#                  id \
#                  SERIAL \
#                  PRIMARY \
#                  KEY, \
#                  name \
#                  VARCHAR \
#              ( \
#                  50 \
#              ) UNIQUE NOT NULL,
#                  leader_id INTEGER REFERENCES users \
#              ( \
#                  id \
#              ),
#                  description TEXT,
#                  total_clan_progress DECIMAL \
#              ( \
#                  10, \
#                  2 \
#              ) DEFAULT 0,
#                  member_count INTEGER DEFAULT 0,
#                  created_at TIMESTAMP DEFAULT NOW \
#              ( \
#              )
#                  );
#
#              CREATE TABLE IF NOT EXISTS clan_members \
#              ( \
#                  clan_id \
#                  INTEGER \
#                  REFERENCES \
#                  clans \
#              ( \
#                  id \
#              ) ON DELETE CASCADE,
#                  user_id INTEGER REFERENCES users \
#              ( \
#                  id \
#              ) \
#                ON DELETE CASCADE,
#                  joined_at TIMESTAMP DEFAULT NOW \
#              ( \
#              ),
#                  role VARCHAR \
#              ( \
#                  20 \
#              ) DEFAULT 'member',
#                  PRIMARY KEY \
#              ( \
#                  clan_id, \
#                  user_id \
#              )
#                  );
#
# -- Items & inventory
#              CREATE TABLE IF NOT EXISTS items \
#              ( \
#                  id \
#                  SERIAL \
#                  PRIMARY \
#                  KEY, \
#                  name \
#                  VARCHAR \
#              ( \
#                  100 \
#              ) NOT NULL,
#                  effect_type VARCHAR \
#              ( \
#                  50 \
#              ),
#                  effect_value DECIMAL \
#              ( \
#                  5, \
#                  2 \
#              ),
#                  rarity VARCHAR \
#              ( \
#                  20 \
#              ) DEFAULT 'common'
#                  );
#
#              CREATE TABLE IF NOT EXISTS user_items \
#              ( \
#                  id \
#                  SERIAL \
#                  PRIMARY \
#                  KEY, \
#                  user_id \
#                  INTEGER \
#                  REFERENCES \
#                  users \
#              ( \
#                  id \
#              ) ON DELETE CASCADE,
#                  item_id INTEGER REFERENCES items \
#              ( \
#                  id \
#              ),
#                  equipped BOOLEAN DEFAULT FALSE,
#                  acquired_at TIMESTAMP DEFAULT NOW \
#              ( \
#              )
#                  ); \
#              """
#
# print("Creating tables and hypertable...")
# with engine.begin() as conn:
#     conn.execute(text(schema_sql))
#     # Make habit_completions a Timescale hypertable
#     try:
#         conn.execute(text("SELECT create_hypertable('habit_completions', 'completed_at', if_not_exists => TRUE);"))
#         print("Hypertable created successfully!")
#     except Exception as e:
#         print("Hypertable warning (probably already exists):", e)
#
# # Seed some sample data
# with engine.begin() as conn:
#     conn.execute(text("""
#                       INSERT INTO realms (name, order_num)
#                       VALUES ('Mortal', 0),
#                              ('Foundation', 1),
#                              ('Copper', 2),
#                              ('Iron', 3),
#                              ('Jade', 4),
#                              ('Lowgold', 5),
#                              ('Highgold', 6),
#                              ('Truegold', 7),
#                              ('Underlord', 8),
#                              ('Overlord', 9),
#                              ('Archlord', 10),
#                              ('Herald', 11),
#                              ('Monarch', 12) ON CONFLICT DO NOTHING;
#
#                       INSERT INTO paths (name, madra_type, description)
#                       VALUES ('Path of Blackflame', 'Blackflame', 'Dragon destroys, flame devours.'),
#                              ('Path of Pure Madra', 'Pure', 'The steady path of Lindon.'),
#                              ('Path of Twin Stars', 'Twin',
#                               'Balance of destruction and creation.') ON CONFLICT DO NOTHING;
#                       """))
#
# print("Sacred Valley database is ready! You may now ascend.")