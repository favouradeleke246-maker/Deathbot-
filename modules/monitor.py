import threading
import time
from modules.utils import db_get_target
from orchestrator import Orchestrator

orch = Orchestrator()

def monitor_target(target_id, chat_id, send_func):
    last_profile = None
    while True:
        target = db_get_target(target_id)
        if not target:
            break
        current_profile = target.get('profile', {})
        if last_profile and current_profile != last_profile:
            send_func(chat_id, f"🔔 Target {target['identifier']} profile changed!")
        last_profile = current_profile
        time.sleep(3600)  # check every hour
