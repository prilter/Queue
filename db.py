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
            hist INTEGER DEFAULT 0, -- =0 - not in queue
            org INTEGER DEFAULT 0   -- >0 - in queue
        )
    ''')
    conn.commit()
    conn.close()

# ADD OR REFRESH USER

def adduser(uid, uname, sub):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # CHECK EXISTING USER
    cursor.execute('SELECT * FROM users WHERE uid = ?', (uid,))
    if cursor.fetchone():
        # UPDATE CURRENT USER
        cursor.execute('''
            UPDATE users 
            SET uname = ?, sub = ?
            WHERE uid = ?
        ''', (uname or "noname", sub, uid))
    else:
        # ADD NEW USER
        cursor.execute('''
            INSERT INTO users (uid, uname, sub, hist, org)
            VALUES (?, ?, ?, 0, 0)
        ''', (uid, uname or "noname", sub))
    
    conn.commit()
    conn.close()

def get_max_position(list_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if list_name == hist_name:
        cursor.execute('SELECT MAX(hist) FROM users WHERE hist > 0')
    elif list_name == org_name:
        cursor.execute('SELECT MAX(org) FROM users WHERE org > 0')
    else:
        conn.close()
        return 0
    
    max_pos = cursor.fetchone()[0]
    conn.close()
    return max_pos if max_pos else 0

# ADD TO QUEUE
def add_to_list(uid, uname, list_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # GET CURRENT USER DATA
    cursor.execute('SELECT hist, org FROM users WHERE uid = ?', (uid,))
    user = cursor.fetchone()
    
    if not user: conn.close(); return False
    
    # IS USER IN QUEUE
    hist_val, org_val = user
    if list_name == org_name and org_val > 0:     conn.close(); return False
    elif list_name == hist_name and hist_val > 0: conn.close(); return False
    
    # UPDATE POSITION OF USER
    if   list_name == org_name:  cursor.execute('UPDATE users SET org = ? WHERE uid = ?',  (get_max_position(list_name)+1, uid))
    elif list_name == hist_name: cursor.execute('UPDATE users SET hist = ? WHERE uid = ?', (get_max_position(list_name)+1, uid))
    else:                        conn.close(); return False
    
    conn.commit()
    conn.close()
    return True

# GET QUEUE BY NAME OF QUEUE
def get_queue_by_sub(list_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if list_name == hist_name:
        cursor.execute('''
            SELECT uname, hist 
            FROM users 
            WHERE hist > 0 
            ORDER BY hist ASC
        ''')
    elif list_name == org_name:
        cursor.execute('''
            SELECT uname, org 
            FROM users 
            WHERE org > 0 
            ORDER BY org ASC
        ''')
    else: conn.close(); return []
    
    result = [f"{i+1}: @{row[0]}" for i, row in enumerate(cursor.fetchall())]
    conn.close()
    return result

# GET USER DATA
def get_user(uid):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE uid = ?', (uid,))
    row = cursor.fetchone()
    conn.close()
    
    return { "uid": row[0], "uname": row[1], "sub": row[2], "hist": row[3], "org": row[4] } if row else None

# UPDATE USER STATUS
def mark_done(uid, sub):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # GET USER POSITION
    cursor.execute('SELECT hist, org FROM users WHERE uid = ?', (uid,))
    user = cursor.fetchone()
    
    if not user: conn.close(); return
    
    hist_val, org_val = user
    
    # HIST
    if sub == org_name and org_val > 0:
        # DELETE USER
        cursor.execute('UPDATE users SET org = 0 WHERE uid = ?', (uid,))
        
        # RECALCULATE QUEUE POSITIONS
        cursor.execute('''
            UPDATE users 
            SET org = org - 1 
            WHERE org > ? AND org > 0
        ''', (org_val,))
        
    # ORG
    elif sub == hist_name and hist_val > 0:
        # DELETE USER
        cursor.execute('UPDATE users SET hist = 0 WHERE uid = ?', (uid,))
        
        # RECALCULATE QUEUE POSITIONS
        cursor.execute('''
            UPDATE users 
            SET hist = hist - 1 
            WHERE hist > ? AND hist > 0
        ''', (hist_val,))
    
    conn.commit()
    conn.close()

# GET USER POSITION
def get_user_position(uid, list_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if   list_name == hist_name: cursor.execute('SELECT hist FROM users WHERE uid = ?', (uid,))
    elif list_name == org_name:  cursor.execute('SELECT org FROM users WHERE uid = ?', (uid,))
    else:                        conn.close(); return 0
    
    pos = cursor.fetchone()[0]
    conn.close()
    return pos if pos else 0

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
    
    # CALCULATE QUEUE
    cursor.execute('SELECT hist, org FROM users WHERE uid = ?', (uid,))
    user = cursor.fetchone()
    
    if user:
        hist_val, org_val = user
        
        # CALCULATE HIST QUEUE
        if hist_val > 0:
            cursor.execute('''
                UPDATE users 
                SET hist = hist - 1 
                WHERE hist > ?
            ''', (hist_val,))
        
        # CALCULATE ORG QUEUE
        if org_val > 0:
            cursor.execute('''
                UPDATE users 
                SET org = org - 1 
                WHERE org > ?
            ''', (org_val,))
    
    # DELETE USER
    cursor.execute('DELETE FROM users WHERE uid = ?', (uid,))
    conn.commit()
    conn.close()
