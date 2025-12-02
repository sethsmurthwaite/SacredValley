# app/models/db.py
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://sacred:valley123@localhost:5432/sacredvalley"
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)


def init_db():
    """Run on startup to ensure all tables and columns exist."""
    with engine.begin() as conn:
        # === Create all tables ===
        conn.execute(text("""
            -- Users
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                path_id INTEGER,
                current_realm VARCHAR(20) NOT NULL DEFAULT 'Mortal',
                progress_to_next DECIMAL(5,2) DEFAULT 0.00 CHECK (progress_to_next >= 0 AND progress_to_next <= 100),
                madra_type VARCHAR(50) DEFAULT 'Pure',
                clan_id INTEGER,
                total_habits_completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );

            -- Paths
            CREATE TABLE IF NOT EXISTS paths (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                madra_type VARCHAR(50) NOT NULL,
                description TEXT
            );

            -- Realms
            CREATE TABLE IF NOT EXISTS realms (
                id SERIAL PRIMARY KEY,
                name VARCHAR(20) UNIQUE NOT NULL,
                order_num INTEGER NOT NULL
            );

            -- Habits
            CREATE TABLE IF NOT EXISTS habits (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                frequency VARCHAR(20) DEFAULT 'daily',
                streak_current INTEGER DEFAULT 0,
                streak_max INTEGER DEFAULT 0,
                progress_value DECIMAL(5,2) DEFAULT 10.0,
                repeat_days INTEGER DEFAULT 127,
                created_at TIMESTAMP DEFAULT NOW()
            );

            -- Habit completions (TimescaleDB hypertable)
            CREATE TABLE IF NOT EXISTS habit_completions (
                id BIGSERIAL,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                habit_id INTEGER REFERENCES habits(id) ON DELETE CASCADE,
                completed_at TIMESTAMP NOT NULL DEFAULT NOW(),
                PRIMARY KEY (id, completed_at)
            );

            -- Clans
            CREATE TABLE IF NOT EXISTS clans (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                leader_id INTEGER REFERENCES users(id),
                description TEXT,
                total_clan_progress DECIMAL(10,2) DEFAULT 0,
                member_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS clan_members (
                clan_id INTEGER REFERENCES clans(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                joined_at TIMESTAMP DEFAULT NOW(),
                role VARCHAR(20) DEFAULT 'member',
                PRIMARY KEY (clan_id, user_id)
            );

            -- Items
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                effect_type VARCHAR(50),
                effect_value DECIMAL(5,2),
                rarity VARCHAR(20) DEFAULT 'common'
            );

            CREATE TABLE IF NOT EXISTS user_items (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                item_id INTEGER REFERENCES items(id),
                equipped BOOLEAN DEFAULT FALSE,
                acquired_at TIMESTAMP DEFAULT NOW()
            );
        """))

        # === Ensure habit_completions is a hypertable ===
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM timescaledb_information.hypertables 
                    WHERE hypertable_name = 'habit_completions'
                ) THEN
                    PERFORM create_hypertable('habit_completions', 'completed_at');
                END IF;
            END $$;
        """))

        # === Add missing columns to habits ===
        conn.execute(text("ALTER TABLE habits ADD COLUMN IF NOT EXISTS progress_value DECIMAL(5,2) DEFAULT 10.0;"))
        conn.execute(text("ALTER TABLE habits ADD COLUMN IF NOT EXISTS repeat_days INTEGER DEFAULT 127;"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS show_progress_public BOOLEAN DEFAULT true;"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_visible_to_clan BOOLEAN DEFAULT true;"))

        # === Seed realms if table is empty ===
        result = conn.execute(text("SELECT COUNT(*) FROM realms")).scalar()
        if result == 0:
            conn.execute(text("""
                INSERT INTO realms (name, order_num) VALUES

                ('Foundation', 1), 
                ('Copper', 2), 
                ('Iron', 3),
                ('Jade', 4), 
                ('Lowgold', 5), 
                ('Highgold', 6), 
                ('Truegold', 7),
                ('Underlord', 8), 
                ('Overlord', 9), 
                ('Archlord', 10),
                ('Herald', 11), 
                ('Sage', 12), 
                ('Monarch', 13);
            """))

        # === Seed paths if table is empty ===
        result = conn.execute(text("SELECT COUNT(*) FROM paths")).scalar()
        if result == 0:
            conn.execute(text("""
                              INSERT INTO paths (name, madra_type)
                              VALUES ('No Path', 'Pure');
                              """))


print("\t\t> Database schema verified and up to date.")