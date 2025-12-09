"""
ANALISE AND REALISE QUEUE LOGIC
"""
from os import path

users_db  = {} # {user_id: {"username": "@nick", "subject": "math", "hist": 0, "org": 1}}
hist_name = "История"
org_name  = "ОРГ"

is_kill_time_limit = False

def adduser(uid, uname, sub, hist_val, org_val): users_db[uid] = {"username": uname or "noname", "subject": sub, "hist": hist_val, "org": org_val} # SMART ADDING USER TO UB(user base)

def add_to_list(uid, uname, list_name):
    if list_name   == org_name  and not users_db[uid]["org"]:  users_db[uid]["org"]  = True
    elif list_name == hist_name and not users_db[uid]["hist"]: users_db[uid]["hist"] = True
    else:                                                      return False
    return True

#def get_list_status():        return f"📋 ОЧЕРЕДИ\n• орг: {len(get_queue_by_sub('org'))} чел.\n• история: {len(get_queue_by_sub('hist'))} чел."

def get_queue_by_sub(list_name):
    if list_name == hist_name: return [f"@{data['username']}" for uid, data in users_db.items() if data.get('hist')]
    if list_name == org_name:  return [f"@{data['username']}" for uid, data in users_db.items() if data.get('org')]

def delete(list, id):
    if id in list: del list[id]

