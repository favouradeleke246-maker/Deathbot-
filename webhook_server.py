import os
import json
import requests
import threading
from flask import Flask, request, jsonify
from orchestrator import Orchestrator
from config import TELEGRAM_TOKEN

app = Flask(__name__)
orch = Orchestrator()
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ---------- Helper Functions ----------
def send_typing(chat_id):
    """Show 'typing…' animation."""
    try:
        requests.post(f"{TELEGRAM_API}/sendChatAction",
                      json={"chat_id": chat_id, "action": "typing"},
                      timeout=5)
    except Exception:
        pass

def send_message(chat_id, text, parse_mode='HTML', reply_markup=None):
    """Send a formatted message."""
    payload = {
        'chat_id': chat_id,
        'text': text[:4096],
        'parse_mode': parse_mode
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        print(f"Send failed: {e}")

def process_long_task(chat_id, func, *args, **kwargs):
    """Run long tasks in background."""
    def wrapper():
        try:
            result = func(*args, **kwargs)
            send_message(chat_id, json.dumps(result, indent=2))
        except Exception as e:
            send_message(chat_id, f"⚠️ <b>Error:</b> {str(e)}")
    thread = threading.Thread(target=wrapper)
    thread.daemon = True
    thread.start()

def get_main_keyboard():
    """Persistent keyboard with emoji buttons."""
    return {
        "keyboard": [
            ["🔍 Track", "📊 Analyze"],
            ["🎯 Hack TikTok", "📱 Hack WhatsApp"],
            ["📋 List", "✅ Verify"],
            ["❓ Help"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

# ---------- Flask Routes ----------
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return 'OK', 200

    # Handle callback queries (if you add inline buttons)
    if 'callback_query' in data:
        return 'OK', 200

    if 'message' not in data:
        return 'OK', 200

    msg = data['message']
    chat_id = msg['chat']['id']
    text = msg.get('text', '').strip()
    if not text:
        return 'OK', 200

    # Show typing indicator
    send_typing(chat_id)

    # Parse command
    parts = text.split()
    cmd = parts[0].lower()
    args = parts[1:]

    try:
        # ---------- Command Handlers ----------
        if cmd == '/start' or cmd == '❓ help' or cmd == 'help':
            reply = (
                "🤖 <b>SpectraX – Silent Intelligence</b>\n\n"
                "🔴 <b>Attack</b> – <code>/hack_tiktok</code> or <code>/hack_wa</code>\n"
                "🟢 <b>Analyze</b> – <code>/analyze &lt;target_id&gt;</code>\n"
                "🔵 <b>Track</b> – <code>/track &lt;identifier&gt;</code>\n"
                "🟣 <b>Verify</b> – <code>/verify &lt;tid&gt; &lt;platform&gt;</code>\n\n"
                "📋 <b>List</b> – <code>/list</code>\n\n"
                "Use the buttons below or type commands directly."
            )
            send_message(chat_id, reply, reply_markup=get_main_keyboard())

        elif cmd == '/track' or cmd == '🔍 track':
            if not args:
                reply = "❌ <b>Usage:</b> <code>/track &lt;identifier&gt;</code>\nExample: <code>/track john_doe</code>"
                send_message(chat_id, reply)
            else:
                ident = args[0]
                send_message(chat_id, "⏳ <b>Tracking...</b> Please wait.")
                threading.Thread(target=process_long_task, args=(chat_id, orch.track, ident)).start()

        elif cmd == '/retrieve':
            if len(args) < 2:
                reply = "❌ <b>Usage:</b> <code>/retrieve &lt;target_id&gt; &lt;platform&gt;</code>"
                send_message(chat_id, reply)
            else:
                tid, plat = int(args[0]), args[1]
                send_message(chat_id, f"⏳ <b>Retrieving</b> from {plat}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.retrieve, tid, plat)).start()

        elif cmd == '/analyze' or cmd == '📊 analyze':
            if not args:
                reply = "❌ <b>Usage:</b> <code>/analyze &lt;target_id&gt;</code>"
                send_message(chat_id, reply)
            else:
                tid = int(args[0])
                send_message(chat_id, f"⏳ <b>Analyzing</b> target {tid}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.analyze, tid)).start()

        elif cmd == '/hack_tiktok' or cmd == '🎯 hack tiktok':
            if len(args) < 2:
                reply = "❌ <b>Usage:</b> <code>/hack_tiktok &lt;username&gt; &lt;attacker_email&gt;</code>"
                send_message(chat_id, reply)
            else:
                username, email = args[0], args[1]
                send_message(chat_id, f"⏳ <b>Launching</b> TikTok attack on {username}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.hack_tiktok, username, email)).start()

        elif cmd == '/hack_wa' or cmd == '📱 hack whatsapp':
            if not args:
                reply = "❌ <b>Usage:</b> <code>/hack_wa &lt;phone&gt;</code>"
                send_message(chat_id, reply)
            else:
                phone = args[0]
                send_message(chat_id, f"⏳ <b>Launching</b> WhatsApp attack on {phone}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.hack_whatsapp, phone)).start()

        elif cmd == '/verify' or cmd == '✅ verify':
            if len(args) < 2:
                reply = "❌ <b>Usage:</b> <code>/verify &lt;target_id&gt; &lt;platform&gt;</code>"
                send_message(chat_id, reply)
            else:
                tid, plat = int(args[0]), args[1]
                send_message(chat_id, f"⏳ <b>Verifying</b> {plat}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.verify, tid, plat)).start()

        elif cmd == '/list' or cmd == '📋 list':
            send_message(chat_id, "⏳ <b>Fetching</b> target list...")
            threading.Thread(target=process_long_task, args=(chat_id, orch.list_targets)).start()

        else:
            reply = "❓ <b>Unknown command.</b> Type <code>/start</code> for help."
            send_message(chat_id, reply)

    except Exception as e:
        send_message(chat_id, f"⚠️ <b>Unexpected error:</b> {str(e)}")

    return 'OK', 200

# ---------- Health Check ----------
@app.route('/health', methods=['GET'])
def health():
    try:
        from modules.utils import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        db_ok = True
    except Exception as e:
        db_ok = False
        print(f"Health DB check failed: {e}")
    ai_ok = bool(orch.ai.groq_client or orch.ai.gemini_model)
    return jsonify({
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
        "ai": ai_ok,
        "service": "SpectraX"
    }), 200 if db_ok else 503

# ---------- AI Test Route ----------
@app.route('/test_ai', methods=['GET'])
def test_ai():
    try:
        from modules.ai_analysis import AIAnalyzer
        class Dummy: pass
        dummy_orch = Dummy()
        ai = AIAnalyzer(dummy_orch)
        result = ai._call_llm("Say 'hello' in one word.")
        return f"AI works! Response: {result}"
    except Exception as e:
        return f"AI error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
