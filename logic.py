"""
ANALISE AND REALISE QUEUE LOGIC
"""
from os import path

users_db  = {} # {user_id: {"username": "@nick", "subject": "math"}}
org_list  = {} # {user_id: {"username": "@nick"}} for "орг"
hist_list = {} # {user_id: {"username": "@nick"}} for "история"

udbsrc  = ".users_db"
orgsrc  = ".org_db"
histsrc = ".hist_db"

hist_name = "История"
org_name  = "ОРГ"

is_kill_time_limit = False

def save_users_db(list: dict):
    with open(udbsrc, "w", encoding="utf-8") as w:
        for id in list:
            w.write(f"{id} {list[id]['username']} {list[id]['subject']} \n")
def get_users_db(list: dict):
    list.clear()
    if path.exists(udbsrc):
        with open(udbsrc, "r", encoding="utf-8") as r:
            for s in r:
                arr = s.split()
                list[int(arr[0])] = {"username": arr[1], "subject": arr[2]}
def adduser(uid, uname, sub): users_db[uid] = {"username": uname or "noname", "subject": sub} # SMART ADDING USER TO UB(user base)
def save_queue_db(list: dict, dbsrc: str):
    with open(dbsrc, "w", encoding="utf-8") as w:
        for id in list:
            w.write(f"{id} {list[id]['username']} \n")
def get_queue_db(list: dict, dbsrc: str):
    list.clear()
    if path.exists(dbsrc):
        with open(dbsrc, "r", encoding="utf-8") as r:
            for s in r:
                arr = s.split()
                list[int(arr[0])] = {"username": arr[1]}
def refresh_db(uid, uname):
    if uid not in users_db: # NEW USER
        adduser(uid, uname, None)
        save_users_db(users_db)
        print(f"DB was updated: new user(caused by {uname})")
    if uname != users_db[uid]["username"]: # REFRESH NAME
        adduser(uid, uname, users_db[uid]["subject"]) 
        if uid in org_list:  org_list[uid]["username"]  = uname; save_queue_db(org_list, orgsrc)
        if uid in hist_list: hist_list[uid]["username"] = uname; save_queue_db(org_list, orgsrc)
        save_users_db(users_db)
        print(f"DB was updated: changed username(caused by {uname})")

def add_to_list_and_save(uid, uname, list_name):
    if list_name   == org_name  and uid not in org_list:  org_list[uid]  = {"username": uname or "noname"}; save_queue_db(org_list, orgsrc)
    elif list_name == hist_name and uid not in hist_list: hist_list[uid] = {"username": uname or "noname"}; save_queue_db(hist_list, histsrc)
    else:                                                 return False
    return True

def get_list_status():        return f"📋 ОЧЕРЕДИ\n• орг: {len(org_list)} чел.\n• история: {len(hist_list)} чел."
def get_unames_by_list(list): return [f"@{data["username"]}" for user_id, data in list.items()]
def delete(list, id):
    if id in list: del list[id]

