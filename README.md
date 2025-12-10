# SacredValley
Sacred Valley is a full-stack, stateful habit-tracking web app inspired by Will Wight’s *Cradle* series, where users advance from Copper to Monarch by consistently completing daily habits, such as gathering "madra," equipping sacred items, joining clans, and competing on real-time leaderboards. It features Redis caching, Postgres + TimescaleDB for time-series data, concurrency-safe updates, and a scalable architecture designed to handle 5000+ reads/writes per second.
# Time Log

| Date       | What                      | Hours |
|------------|---------------------------|-------|
| 11/11/2025 | Worked on initial designs | 2.5   |
| 11/16/2025 | Developement              | 4     |
| 11/26/2025 | Added features            | 6     |
| 11/27/2025 | Worked on UI/Frontend     | 9     |
| 12/01/2025 | Worked on UI/Frontend     | 7     |
| 12/01/2025 | Worked on database        | 4     |
| 12/02/2025 | Setup demo and practice   | 2     |

Total: 34.5



# Project Design

I plan to use a python backend with a simple html page decorated with css. I plan on connecting to redis using docker. I will host this application on my local machine.


### Why This Project Is Interesting to Me

*Cradle* is one of my all-time favorite series. I wanted to build something I’d actually use every day, while proving I can design and implement a real production-grade stateful system from scratch. This project became both a personal motivation tool and a love letter to one of my favorite book series.

### Key learnings

Caching with Redis made everything way faster
Dashboard used to take 200–300 ms to load. After adding Redis caching, it went a lot faster. Simple change, huge difference.

Concurrency bugs only show up when multiple users hit the same thing at once
Clan leaderboards were getting messed up during updates. Now I actually get why concurrency matters.

Load testing tells you the truth your local machine lies about
Everything worked fine on my laptop. Then I simulated more and found bottlenecks. 

### ERD

```mermaid
    USER ||--o{ HABIT : creates
    USER ||--o{ COMPLETION : records
    USER ||--o{ USER_CLAN : belongs_to
    CLAN ||--o{ USER_CLAN : contains
    USER ||--o{ EQUIPPED_ITEM : wears
    ITEM ||--o{ EQUIPPED_ITEM : "can be equipped"
    PATH ||--o{ HABIT : suggests

    USER {
        int id PK
        string username
        string password_hash
        int current_realm
        float madra_progress
        int streak_count
        datetime last_active
    }
    HABIT {
        int id PK
        int user_id FK
        string name
        string madra_type
        int target_minutes
        bool is_active
    }
    COMPLETION {
        int id PK
        int habit_id FK
        date completion_date
        int minutes_done
    }
    CLAN {
        int id PK
        string name
        string motto
    }
    USER_CLAN {
        int user_id PK,FK
        int clan_id PK,FK
        datetime joined_at
    }
    ITEM {
        int id PK
        string name
        string effect_description
        float multiplier
    }
    PATH {
        int id PK
        string name "Path of the Blackflame"
        string description
    }
```


