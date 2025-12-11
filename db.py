""" ANALISE AND REALISE QUEUE LOGIC WITH SQLITE DATABASE """
import sqlite3

DB_NAME = 'queue_bot.db'
hist_name = "История"
org_name = "ОРГ"
is_kill_time_limit = False

# INIT DB
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY,
            uname TEXT,
            sub TEXT,
            hist BOOLEAN DEFAULT 0,
            org BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# ADD OR REFRESH USER
def adduser(uid, uname, sub, hist_val, org_val):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # CHECK USER EXISTING
    cursor.execute('SELECT * FROM users WHERE uid = ?', (uid,))
    if cursor.fetchone():
        # REFRESH REAL USER
        cursor.execute('''
            UPDATE users 
            SET uname = ?, sub = ?, hist = ?, org = ?
            WHERE uid = ?
        ''', (uname or "noname", sub, hist_val, org_val, uid))
    else:
        # ADD NEW USER
        cursor.execute('''
            INSERT INTO users (uid, uname, sub, hist, org)
            VALUES (?, ?, ?, ?, ?)
        ''', (uid, uname or "noname", sub, hist_val, org_val))
    
    conn.commit()
    conn.close()

# ADD TO QUEUE
def add_to_list(uid, uname, list_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT hist, org FROM users WHERE uid = ?', (uid,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return False
    
    hist_val, org_val = user
    if   list_name == org_name  and not org_val:  cursor.execute('UPDATE users SET org = 1 WHERE uid = ?', (uid,))
    elif list_name == hist_name and not hist_val: cursor.execute('UPDATE users SET hist = 1 WHERE uid = ?', (uid,))
    else:                                         return False
    
    conn.commit()
    conn.close()
    return True

# GET QUEUE BY NAME OF QUEUE
def get_queue_by_sub(list_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if   list_name == hist_name: cursor.execute('SELECT uname FROM users WHERE hist = 1')
    elif list_name == org_name:  cursor.execute('SELECT uname FROM users WHERE org = 1')
    else:                        conn.close(); return []
    
    result = [f"@{row[0]}" for row in cursor.fetchall()]
    conn.close()
    return result

# GET USER DATA
def get_user(uid):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE uid = ?', (uid,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "uid": row[0],
            "uname": row[1],
            "sub": row[2],
            "hist": bool(row[3]),
            "org": bool(row[4])
        }
    return None

# UPDATE USER STATUS
def mark_done(uid, sub):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if   sub == org_name:  cursor.execute('UPDATE users SET org = 0 WHERE uid = ?',  (uid,))
    elif sub == hist_name: cursor.execute('UPDATE users SET hist = 0 WHERE uid = ?', (uid,))
    
    conn.commit()
    conn.close()

# GET ALL TABLE BY DICT(FOR NOTIFICATIONS)
def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT uid, uname FROM users')
    users = cursor.fetchall()
    conn.close()
    return {uid: {"uname": uname} for uid, uname in users}

# DELETE NON-ACTIVE USER(DELETED ACOUNT OR OTHER STUFF)
def delete_user(uid):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE uid = ?', (uid,))
    conn.commit()
    conn.close()
