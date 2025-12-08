"""
ANALISE AND REALISE QUEUE LOGIC
"""
users_db  = {} # {user_id: {"username": "@nick", "subject": "math"}}
org_list  = {} # {user_id: {"username": "@nick"}} for "орг"
hist_list = {} # {user_id: {"username": "@nick"}} for "история"

hist_name = "история"
org_name  = "ОРГ"

is_kill_time_limit = False

def adduser(uid, uname, sub): users_db[uid] = {"username": uname or "noname", "subject": sub} # SMART ADDING USER TO UB(user base)

def add_to_list(uid, uname, list_name):
    if list_name   == org_name  and uid not in org_list:  org_list[uid]  = {"username": uname or "noname"}
    elif list_name == hist_name and uid not in hist_list: hist_list[uid] = {"username": uname or "noname"}
    else:                                                 return False
    return True

def get_list_status():        return f"📋 ОЧЕРЕДИ\n• орг: {len(org_list)} чел.\n• история: {len(hist_list)} чел."
def get_unames_by_list(list): return [f"@{data["username"]}" for user_id, data in list.items()]
