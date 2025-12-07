"""
ANALISE AND REALISE QUEUE LOGIC
"""
users_db  = {} # {user_id: {"username": "@nick"}}
org_list  = {} # {user_id: {"username": "@nick"}} for "орг"
hist_list = {} # {user_id: {"username": "@nick"}} for "история"

def adduser(user_id, username):
    """Добавляет/обновляет пользователя (умный — по ID)"""
    users_db[user_id] = {"username": username or "no_username"}

def add_to_list(uid, uname, list_name):
    if list_name == "орг" and uid not in org_list:        org_list[uid]  = {"username": uname or "noname"}
    elif list_name == "история" and uid not in hist_list: hist_list[uid] = {"username": uname or "noname"}
    else:                                                 return False
    return True

def get_list_status():
    return f"📋 **ОЧЕРЕДИ**\n• орг: {len(org_list)} чел.\n• история: {len(hist_list)} чел."

def get_unames_by_list(list): return [f"@{data["username"]}" for user_id, data in list.items()]
