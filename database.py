import sqlite3
import json
from pathlib import Path

DB_PATH = "afteron.db"

DEFAULT_RESOURCES = {
    "سکه": 5000,
    "غلات": 500,
    "گوشت": 200,
    "شراب": 50,
    "چوب": 200,
    "سنگ": 200,
    "آهن": 200,
    "رعیت": 150,
    "اسب": 0,
    "دراگون‌گلس": 0,
    "ماهی": 0
}

DEFAULT_MILITARY = {
    "شمشیرزن": 1000,
    "کماندار": 1000,
    "نیزه‌دار": 1000,
    "سوارکار": 500,
    "نیروی ویژه": 0,
    "اژدها": 0,
    "هیرو": 0
}

DEFAULT_NAVY = {
    "قایق پارویی": 5,
    "کشتی چوبی": 3,
    "کشتی جنگی": 2
}

DEFAULT_SIEGE = {
    "نردبان": 5,
    "دژکوب": 2,
    "منجنیق": 0,
    "برج محاصره": 0,
    "اسکورپیون": 0,
    "بشکه قیر": 0
}

DEFAULT_POWER = {
    "دفاع شهر": 5,
    "وفاداری رعیت": 50,
    "بدنامی": 0
}

DEFAULT_BUILDINGS = {
    "شهر": 1,
    "قلعه": 1,
    "بازارچه": 1,
    "میخانه": 0,
    "فاحشه‌خانه": 0,
    "خزانه": 1,
    "معبد": 0,
    "مزرعه": 1,
    "دامداری": 0,
    "چوب‌بری": 1,
    "معدن": 1,
    "انبار آذوقه": 1,
    "کمپ شمشیرزن": 1,
    "کمپ کماندار": 1,
    "کمپ نیزه‌دار": 1,
    "کمپ سوارکار": 0,
    "کمپ نیروی ویژه": 0,
    "پادگان": 1,
    "کارگاه ادوات": 0,
    "گودال اژدها": 0,
    "بندرگاه": 0,
    "کشتی‌سازی": 0
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
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
        "user_id": row[0],
        "username": row[1],
        "clan_name": row[2],
        "castle_name": row[3],
        "clan_emoji": row[4],
        "region": row[5],
        "resources": json.loads(row[6]),
        "military": json.loads(row[7]),
        "navy": json.loads(row[8]),
        "siege": json.loads(row[9]),
        "power": json.loads(row[10]),
        "buildings": json.loads(row[11])
    }

def create_player(user_id, username, clan_name, castle_name, clan_emoji, region):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO players 
        (user_id, username, clan_name, castle_name, clan_emoji, region, resources, military, navy, siege, power, buildings)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
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
    c.execute(f"UPDATE players SET {field}=? WHERE user_id=?", (json.dumps(data, ensure_ascii=False), user_id))
    conn.commit()
    conn.close()

def get_all_players():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id, username, clan_name, castle_name FROM players")
    rows = c.fetchall()
    conn.close()
    return rows

init_db()
