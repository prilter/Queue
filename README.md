# This repository contains the open-source program of my TG bot for controlling queues at my university
  
# Installation guide
1) Use next commands:   
```bash
git clone https://github.com/prilter/queue
cd queue
python -m venv .venv
source .venv/bin/active
pip install -r requirements.py
```  
2) Make .env file and add next lines:  
BOT_API          = "<YOUR API>"  
kill_limits_pass = "<YOUR ADMIN PASSWORD>"  
3) Start your bot:  
```bash
python main.py
```
