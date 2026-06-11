import sqlite3
import json

DB_PATH = "afteron.db"

DEFAULT_RESOURCES = {
    "سکه": 5000, "غلات": 500, "گوشت": 200, "شراب": 50,
    "چوب": 200, "سنگ": 200, "آهن": 200, "رعیت": 150,
    "اسب": 0, "دراگون‌گلس": 0, "ماهی": 0, "فولاد": 0
}

DEFAULT_MILITARY = {
    "شمشیرزن": 1000, "کماندار": 1000, "نیزه‌دار": 1000,
    "سوارکار": 500, "نیروی ویژه": 0, "اژدها": 0, "هیرو": 0
}

DEFAULT_NAVY = {
    "قایق پارویی": 5, "قایق بادبانی سبک": 0, "کشتی تجاری": 0,
    "کشتی جنگی سبک": 0, "کشتی جنگی سنگین": 2, "ناو فرماندهی": 0
}

DEFAULT_SIEGE = {
    "نردبان": 5, "دژکوب": 2, "منجنیق": 0,
    "برج محاصره": 0, "اسکورپیون": 0, "بشکه قیر": 0, "ارابه جنگی": 0
}

DEFAULT_POWER = {
    "دفاع شهر": 5, "وفاداری رعیت": 50, "بدنامی": 0
}

DEFAULT_BUILDINGS = {
    "شهر": 1, "قلعه": 1, "بازارچه": 1, "میخانه": 0,
    "فاحشه‌خانه": 0, "خزانه": 1, "معبد": 0, "مزرعه": 1,
    "دامداری": 0, "چوب‌بری": 1, "معدن": 1, "انبار آذوقه": 1,
    "کمپ شمشیرزن": 1, "کمپ کماندار": 1, "کمپ نیزه‌دار": 1,
    "کمپ سوارکار": 0, "کمپ نیروی ویژه": 0, "پادگان": 1,
    "کارگاه ادوات": 0, "گودال اژدها": 0, "بندرگاه": 0,
    "کشتی‌سازی": 0, "ساختمان ویژه": 0
}

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        clan_name TEXT,
        castle_name TEXT,
        clan_emoji TEXT,
        region TEXT,
        resources TEXT,
        military TEXT,
        navy TEXT,
        siege TEXT,
        power TEXT,
        buildings TEXT,
        is_banned INTEGER DEFAULT 0,
        is_restricted INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS shop_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        emoji TEXT,
        category TEXT,
        price TEXT,
        gives_field TEXT,
        gives_key TEXT,
        gives_amount INTEGER,
        active INTEGER DEFAULT 1
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        reward TEXT,
        status TEXT DEFAULT 'active',
        winner_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS event_participants (
        event_id INTEGER,
        user_id INTEGER,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (event_id, user_id)
    )''')
    conn.commit()
    conn.close()
    _init_default_shop()

def _init_default_shop():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM shop_items")
    if c.fetchone()[0] == 0:
        items = [
            ("نردبان", "🪜", "ادوات", '{"سکه":20,"چوب":10}', "siege", "نردبان", 1),
            ("دژکوب", "🐏", "ادوات", '{"سکه":150,"چوب":80,"فولاد":20}', "siege", "دژکوب", 1),
            ("منجنیق", "🪨", "ادوات", '{"سکه":1000,"چوب":250,"فولاد":100}', "siege", "منجنیق", 1),
            ("برج محاصره", "🏰", "ادوات", '{"سکه":3000,"چوب":1000,"فولاد":300}', "siege", "برج محاصره", 1),
            ("اسکورپیون", "🦂", "ادوات", '{"سکه":500,"چوب":100,"فولاد":50}', "siege", "اسکورپیون", 1),
            ("ارابه جنگی", "🛞", "ادوات", '{"سکه":700,"چوب":150,"فولاد":50}', "siege", "ارابه جنگی", 1),
            ("قایق پارویی", "🚤", "ناوگان", '{"سکه":50,"چوب":30}', "navy", "قایق پارویی", 1),
            ("قایق بادبانی سبک", "⛵", "ناوگان", '{"سکه":150,"چوب":80}', "navy", "قایق بادبانی سبک", 1),
            ("کشتی تجاری", "🚢", "ناوگان", '{"سکه":500,"چوب":250}', "navy", "کشتی تجاری", 1),
            ("کشتی جنگی سبک", "🛶", "ناوگان", '{"سکه":1000,"چوب":500,"آهن":100}', "navy", "کشتی جنگی سبک", 1),
            ("کشتی جنگی سنگین", "⚓", "ناوگان", '{"سکه":2500,"چوب":1200,"آهن":300}', "navy", "کشتی جنگی سنگین", 1),
            ("ناو فرماندهی", "🏴‍☠️", "ناوگان", '{"سکه":5000,"چوب":2000,"آهن":600}', "navy", "ناو فرماندهی", 1),
            ("اسب", "🐎", "منابع", '{"سکه":200}', "resources", "اسب", 5),
            ("شراب", "🍷", "منابع", '{"سکه":100}', "resources", "شراب", 10),
            ("دراگون‌گلس", "💎", "منابع", '{"سکه":1000}', "resources", "دراگون‌گلس", 5),
            ("فولاد", "⚙️", "منابع", '{"سکه":500,"آهن":50}', "resources", "فولاد", 10),
        ]
        c.executemany("INSERT INTO shop_items (name,emoji,category,price,gives_field,gives_key,gives_amount,active) VALUES (?,?,?,?,?,?,?,1)", items)
        conn.commit()
    conn.close()

def get_player(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "user_id": row[0], "username": row[1], "clan_name": row[2],
        "castle_name": row[3], "clan_emoji": row[4], "region": row[5],
        "resources": json.loads(row[6]), "military": json.loads(row[7]),
        "navy": json.loads(row[8]), "siege": json.loads(row[9]),
        "power": json.loads(row[10]), "buildings": json.loads(row[11]),
        "is_banned": row[12], "is_restricted": row[13]
    }

def create_player(user_id, username, clan_name, castle_name, clan_emoji, region):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO players
        (user_id,username,clan_name,castle_name,clan_emoji,region,resources,military,navy,siege,power,buildings,is_banned,is_restricted)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,0,0)''',
        (user_id, username, clan_name, castle_name, clan_emoji, region,
         json.dumps(DEFAULT_RESOURCES, ensure_ascii=False),
         json.dumps(DEFAULT_MILITARY, ensure_ascii=False),
         json.dumps(DEFAULT_NAVY, ensure_ascii=False),
         json.dumps(DEFAULT_SIEGE, ensure_ascii=False),
         json.dumps(DEFAULT_POWER, ensure_ascii=False),
         json.dumps(DEFAULT_BUILDINGS, ensure_ascii=False)))
    conn.commit()
    conn.close()

def update_player(user_id, field, data):
    conn = get_conn()
    c = conn.cursor()
    if field in ("is_banned", "is_restricted"):
        c.execute(f"UPDATE players SET {field}=? WHERE user_id=?", (data, user_id))
    else:
        c.execute(f"UPDATE players SET {field}=? WHERE user_id=?", (json.dumps(data, ensure_ascii=False), user_id))
    conn.commit()
    conn.close()

def get_all_players():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id, username, clan_name, castle_name, is_banned, is_restricted FROM players")
    rows = c.fetchall()
    conn.close()
    return rows

def get_shop_items(active_only=True):
    conn = get_conn()
    c = conn.cursor()
    if active_only:
        c.execute("SELECT * FROM shop_items WHERE active=1")
    else:
        c.execute("SELECT * FROM shop_items")
    rows = c.fetchall()
    conn.close()
    return rows

def add_shop_item(name, emoji, category, price_dict, gives_field, gives_key, gives_amount):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO shop_items (name,emoji,category,price,gives_field,gives_key,gives_amount,active) VALUES (?,?,?,?,?,?,?,1)",
              (name, emoji, category, json.dumps(price_dict, ensure_ascii=False), gives_field, gives_key, gives_amount))
    conn.commit()
    conn.close()

def toggle_shop_item(item_id, active):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE shop_items SET active=? WHERE id=?", (active, item_id))
    conn.commit()
    conn.close()

# Events
def create_event(title, description, reward_dict):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO events (title,description,reward,status) VALUES (?,?,?,'active')",
              (title, description, json.dumps(reward_dict, ensure_ascii=False)))
    conn.commit()
    event_id = c.lastrowid
    conn.close()
    return event_id

def get_active_events():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM events WHERE status='active'")
    rows = c.fetchall()
    conn.close()
    return rows

def get_event(event_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM events WHERE id=?", (event_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "title": row[1], "description": row[2],
            "reward": json.loads(row[3]), "status": row[4], "winner_id": row[5]}

def join_event(event_id, user_id):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO event_participants (event_id,user_id) VALUES (?,?)", (event_id, user_id))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def leave_event(event_id, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM event_participants WHERE event_id=? AND user_id=?", (event_id, user_id))
    conn.commit()
    conn.close()

def get_event_participants(event_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT p.user_id, p.username, p.clan_name 
                 FROM event_participants ep 
                 JOIN players p ON ep.user_id=p.user_id 
                 WHERE ep.event_id=?""", (event_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def is_in_event(event_id, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT 1 FROM event_participants WHERE event_id=? AND user_id=?", (event_id, user_id))
    result = c.fetchone()
    conn.close()
    return result is not None

def end_event(event_id, winner_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE events SET status='ended', winner_id=? WHERE id=?", (winner_id, event_id))
    conn.commit()
    conn.close()

def delete_player(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM players WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

init_db()

# سیستم ردیابی فعالیت
def log_activity(user_id):
    """ثبت فعالیت بازیکن"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS activity_log (
        user_id INTEGER,
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute("INSERT INTO activity_log (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_weekly_activity():
    """دریافت فعالیت هفت روز گذشته"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS activity_log (
        user_id INTEGER,
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''SELECT p.user_id, p.username, p.clan_name, COUNT(a.user_id) as actions
                 FROM players p
                 LEFT JOIN activity_log a ON p.user_id = a.user_id
                 AND a.logged_at >= datetime('now', '-7 days')
                 GROUP BY p.user_id
                 ORDER BY actions DESC''')
    rows = c.fetchall()
    conn.close()
    return rows
