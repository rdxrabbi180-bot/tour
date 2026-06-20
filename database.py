# database.py
# এই ফাইলে SQLite ডেটাবেজ-এর সব ফাংশন আছে
# এখানে টুর্নামেন্ট, রেজিস্ট্রেশন, পেমেন্ট-এর তথ্য জমা থাকবে

import sqlite3
from config import DB_NAME


def get_connection():
    """ডেটাবেজের সাথে কানেকশন তৈরি করে"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # এটা দিয়ে আমরা কলামের নাম দিয়ে ডেটা অ্যাক্সেস করতে পারব
    return conn


def init_db():
    """প্রথমবার বট চালু হলে টেবিলগুলো তৈরি করে (যদি আগে থেকে না থাকে)"""
    conn = get_connection()
    cur = conn.cursor()

    # টুর্নামেন্ট টেবিল
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            entry_fee INTEGER NOT NULL,
            max_slots INTEGER NOT NULL,
            match_time TEXT,
            status TEXT DEFAULT 'open',   -- open / closed / completed
            room_id TEXT,
            room_password TEXT
        )
    """)

    # রেজিস্ট্রেশন টেবিল (একটা squad = একটা রো)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            telegram_user_id INTEGER NOT NULL,
            telegram_username TEXT,
            team_name TEXT NOT NULL,
            player1_ign TEXT,
            player1_uid TEXT,
            player2_ign TEXT,
            player2_uid TEXT,
            player3_ign TEXT,
            player3_uid TEXT,
            player4_ign TEXT,
            player4_uid TEXT,
            trx_id TEXT,
            payment_status TEXT DEFAULT 'pending',  -- pending / approved / rejected
            slot_number INTEGER,
            FOREIGN KEY (tournament_id) REFERENCES tournaments (id)
        )
    """)

    conn.commit()
    conn.close()


# ---------- টুর্নামেন্ট রিলেটেড ফাংশন ----------

def create_tournament(name, entry_fee, max_slots, match_time):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tournaments (name, entry_fee, max_slots, match_time) VALUES (?, ?, ?, ?)",
        (name, entry_fee, max_slots, match_time)
    )
    conn.commit()
    tournament_id = cur.lastrowid
    conn.close()
    return tournament_id


def get_open_tournaments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tournaments WHERE status = 'open'")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_tournament(tournament_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
    row = cur.fetchone()
    conn.close()
    return row


def count_approved_slots(tournament_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) as cnt FROM registrations WHERE tournament_id = ? AND payment_status = 'approved'",
        (tournament_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row["cnt"]


def set_room_details(tournament_id, room_id, room_password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tournaments SET room_id = ?, room_password = ? WHERE id = ?",
        (room_id, room_password, tournament_id)
    )
    conn.commit()
    conn.close()


def close_tournament(tournament_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tournaments SET status = 'closed' WHERE id = ?", (tournament_id,))
    conn.commit()
    conn.close()


# ---------- রেজিস্ট্রেশন রিলেটেড ফাংশন ----------

def create_registration(data):
    """data হবে একটা dict, যেখানে সব ফর্ম-এর তথ্য থাকবে"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO registrations (
            tournament_id, telegram_user_id, telegram_username, team_name,
            player1_ign, player1_uid, player2_ign, player2_uid,
            player3_ign, player3_uid, player4_ign, player4_uid, trx_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["tournament_id"], data["telegram_user_id"], data["telegram_username"], data["team_name"],
        data["player1_ign"], data["player1_uid"], data["player2_ign"], data["player2_uid"],
        data["player3_ign"], data["player3_uid"], data["player4_ign"], data["player4_uid"], data["trx_id"]
    ))
    conn.commit()
    reg_id = cur.lastrowid
    conn.close()
    return reg_id


def get_registration(reg_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM registrations WHERE id = ?", (reg_id,))
    row = cur.fetchone()
    conn.close()
    return row


def get_pending_registrations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM registrations WHERE payment_status = 'pending'")
    rows = cur.fetchall()
    conn.close()
    return rows


def approve_registration(reg_id, slot_number):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE registrations SET payment_status = 'approved', slot_number = ? WHERE id = ?",
        (slot_number, reg_id)
    )
    conn.commit()
    conn.close()


def reject_registration(reg_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE registrations SET payment_status = 'rejected' WHERE id = ?", (reg_id,))
    conn.commit()
    conn.close()


def get_approved_registrations(tournament_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM registrations WHERE tournament_id = ? AND payment_status = 'approved' ORDER BY slot_number",
        (tournament_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows
