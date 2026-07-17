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
    '/start': ['/start', '❓ help', 'help', '/menu'],
    '/track': ['/track', '🔍 track', 'track'],
    '/retrieve': ['/retrieve'],
    '/analyze': ['/analyze', '📊 analyze', 'analyze'],
    '/hack_tiktok': ['/hack_tiktok', '🎯 hack tiktok', 'hack tiktok'],
    '/hack_wa': ['/hack_wa', '📱 hack whatsapp', 'hack whatsapp'],
    '/verify': ['/verify', '✅ verify', 'verify'],
    '/list': ['/list', '📋 list', 'list'],
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
    '/sentiment': ['/sentiment'],
    '/phish_link': ['/phish_link'],
    '/plugin_list': ['/plugin_list'],
    '/plugin_load': ['/plugin_load'],
    '/monitor': ['/monitor'],
    '/record_outcome': ['/record_outcome'],
    '/best_attack': ['/best_attack'],
    '/defensive': ['/defensive'],
    '/share': ['/share'],
    '/unshare': ['/unshare'],
    '/shodan': ['/shodan'],
    '/encrypt': ['/encrypt'],
    '/decrypt': ['/decrypt'],
    '/geolocate': ['/geolocate'],
    '/darkweb': ['/darkweb'],
    '/score': ['/score'],
}

def get_command(text):
    text_lower = text.strip().lower()
    for canonical, aliases in COMMAND_ALIASES.items():
        if text_lower in [a.lower() for a in aliases]:
            return canonical
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
            ["❓ Menu"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def is_admin(chat_id):
    return chat_id == SUPER_ADMIN_ID or orch.admin.is_admin(chat_id)

def get_help_text():
    return """
<b>🤖 SpectraX – Command Menu</b>

<b>🔵 OSINT & Reconnaissance</b>
/track &lt;identifier&gt; – OSINT on username/email/phone
/retrieve &lt;tid&gt; &lt;platform&gt; – Retrieve profile (TikTok)
/breach &lt;email&gt; – Check data breaches
/whois &lt;domain&gt; – WHOIS lookup
/dns &lt;domain&gt; – DNS resolution
/reverseimage &lt;url&gt; – Reverse image search
/instagram &lt;username&gt; – Instagram profile
/twitter &lt;username&gt; – Twitter profile

<b>🔴 Attacks & Exploits</b>
/hack_tiktok &lt;username&gt; &lt;email&gt; – Generate XSS + IDOR (admin)
/hack_wa &lt;phone&gt; – WhatsApp registration check (admin)
/phish &lt;email&gt; [template] – Generate phishing email (admin)
/stuff &lt;user&gt; &lt;passwords&gt; – Credential stuffing (admin)
/session &lt;cookie&gt; – Test session cookie (admin)
/nmap &lt;host&gt; [ports] – Port scan (admin)

<b>🟢 Analysis & Reporting</b>
/analyze &lt;tid&gt; – Risk report
/report &lt;tid&gt; – Generate PDF report
/sentiment &lt;text&gt; – Sentiment analysis
/score &lt;tid&gt; – Target priority score
/best_attack &lt;tid&gt; – Best attack from past outcomes

<b>🟣 Utilities & Intelligence</b>
/list – Show all targets
/verify &lt;tid&gt; &lt;platform&gt; – Verify platform presence
/geolocate &lt;ip&gt; – Geolocation
/shodan &lt;ip&gt; – Shodan IP lookup (requires key)
/darkweb &lt;email&gt; – Breach check (same as /breach)
/encrypt &lt;text&gt; – Encrypt text
/decrypt &lt;encrypted&gt; – Decrypt text
/phish_link &lt;email&gt; – Shorten phishing link (if Bitly key set)

<b>⚙️ Admin & System</b>
/diagnose – System diagnostics
/model &lt;provider&gt; – Switch AI (groq/gemini/deepseek/ollama)
/add_admin &lt;user_id&gt; – Add admin (super admin)
/remove_admin &lt;user_id&gt; – Remove admin (super admin)
/list_admins – List admins (super admin)
/defensive – Defensive scan (admin)
/monitor &lt;tid&gt; &lt;chat_id&gt; – Start monitoring (admin)
/record_outcome &lt;tid&gt; &lt;attack&gt; &lt;success&gt; – Record outcome
/share &lt;tid&gt; &lt;user_id&gt; – Share target
/unshare &lt;tid&gt; &lt;user_id&gt; – Unshare target
/plugin_list – List available plugins
/plugin_load &lt;name&gt; – Load plugin

📌 <i>Use /start to see this menu anytime.</i>
"""

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
            send_message(chat_id, "❓ Unknown command. Type <code>/start</code> or <code>/menu</code> for help.")
            return 'OK', 200

    parts = text.split()
    args = parts[1:] if len(parts) > 1 else []

    try:
        # ---------- Core Commands ----------
        if cmd == '/start' or cmd == '/menu':
            reply = get_help_text()
            send_message(chat_id, reply, reply_markup=get_main_keyboard())

        elif cmd == '/track':
            if not args:
                reply = "❌ Usage: <code>/track &lt;identifier&gt;</code>\nExample: <code>/track john_doe</code>"
                send_message(chat_id, reply)
            else:
                ident = args[0]
                send_message(chat_id, "⏳ Tracking... Please wait.")
                threading.Thread(target=process_long_task, args=(chat_id, orch.track, ident)).start()

        elif cmd == '/retrieve':
            if len(args) < 2:
                reply = "❌ Usage: <code>/retrieve &lt;target_id&gt; &lt;platform&gt;</code>"
                send_message(chat_id, reply)
            else:
                try:
                    tid = int(args[0])
                    plat = args[1]
                    send_message(chat_id, f"⏳ Retrieving from {plat}...")
                    threading.Thread(target=process_long_task, args=(chat_id, orch.retrieve, tid, plat)).start()
                except ValueError:
                    send_message(chat_id, "❌ Invalid target ID. Must be a number.")

        elif cmd == '/analyze':
            if not args or not args[0].isdigit():
                reply = "❌ Usage: <code>/analyze &lt;target_id&gt;</code>\nExample: <code>/analyze 5</code>"
                send_message(chat_id, reply)
            else:
                tid = int(args[0])
                send_message(chat_id, f"⏳ Analyzing target {tid}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.analyze, tid)).start()

        elif cmd == '/hack_tiktok':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                reply = "❌ Usage: <code>/hack_tiktok &lt;username&gt; &lt;attacker_email&gt;</code>"
                send_message(chat_id, reply)
            else:
                username, email = args[0], args[1]
                send_message(chat_id, f"⏳ Launching TikTok attack on {username}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.hack_tiktok, username, email)).start()

        elif cmd == '/hack_wa':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif not args:
                reply = "❌ Usage: <code>/hack_wa &lt;phone&gt;</code>\nExample: <code>/hack_wa +2348012345678</code>"
                send_message(chat_id, reply)
            else:
                phone = args[0]
                send_message(chat_id, f"⏳ Checking WhatsApp for {phone}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.hack_whatsapp, phone)).start()

        elif cmd == '/verify':
            if len(args) < 2:
                reply = "❌ Usage: <code>/verify &lt;target_id&gt; &lt;platform&gt;</code>"
                send_message(chat_id, reply)
            else:
                try:
                    tid = int(args[0])
                    plat = args[1]
                    send_message(chat_id, f"⏳ Verifying {plat}...")
                    threading.Thread(target=process_long_task, args=(chat_id, orch.verify_target, tid, plat)).start()
                except ValueError:
                    send_message(chat_id, "❌ Invalid target ID.")

        elif cmd == '/list':
            send_message(chat_id, "⏳ Fetching target list...")
            threading.Thread(target=process_long_task, args=(chat_id, orch.list_targets)).start()

        # ---------- OSINT Commands ----------
        elif cmd == '/breach':
            if not args:
                reply = "❌ Usage: <code>/breach &lt;email&gt;</code>"
                send_message(chat_id, reply)
            else:
                email = args[0]
                send_message(chat_id, f"⏳ Checking email breach for {email}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.breach_check, email)).start()

        elif cmd == '/whois':
            if not args:
                reply = "❌ Usage: <code>/whois &lt;domain&gt;</code>"
                send_message(chat_id, reply)
            else:
                domain = args[0]
                send_message(chat_id, f"⏳ Looking up WHOIS for {domain}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.whois_lookup, domain)).start()

        elif cmd == '/dns':
            if not args:
                reply = "❌ Usage: <code>/dns &lt;domain&gt;</code>"
                send_message(chat_id, reply)
            else:
                domain = args[0]
                send_message(chat_id, f"⏳ Resolving DNS for {domain}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.dns_enum, domain)).start()

        elif cmd == '/reverseimage':
            if not args:
                reply = "❌ Usage: <code>/reverseimage &lt;image_url&gt;</code>"
                send_message(chat_id, reply)
            else:
                url = args[0]
                send_message(chat_id, f"⏳ Searching reverse image...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.reverse_image, url)).start()

        elif cmd == '/instagram':
            if not args:
                reply = "❌ Usage: <code>/instagram &lt;username&gt;</code>"
                send_message(chat_id, reply)
            else:
                username = args[0]
                send_message(chat_id, f"⏳ Fetching Instagram profile...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.instagram_profile, username)).start()

        elif cmd == '/twitter':
            if not args:
                reply = "❌ Usage: <code>/twitter &lt;username&gt;</code>"
                send_message(chat_id, reply)
            else:
                username = args[0]
                send_message(chat_id, f"⏳ Fetching Twitter profile...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.twitter_profile, username)).start()

        # ---------- Attack/Exploit Commands (admin) ----------
        elif cmd == '/phish':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif len(args) < 1:
                reply = "❌ Usage: <code>/phish &lt;email&gt; [template]</code>\nTemplates: generic, bank, social"
                send_message(chat_id, reply)
            else:
                email = args[0]
                template = args[1] if len(args) > 1 else 'generic'
                send_message(chat_id, f"⏳ Generating phishing email...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.generate_phish, email, template)).start()

        elif cmd == '/stuff':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                reply = "❌ Usage: <code>/stuff &lt;username&gt; &lt;passwords&gt;</code>\nPasswords: comma-separated list"
                send_message(chat_id, reply)
            else:
                username = args[0]
                passwords = args[1].split(',')
                send_message(chat_id, f"⏳ Attempting credential stuffing...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.credential_stuff, username, passwords)).start()

        elif cmd == '/session':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif not args:
                reply = "❌ Usage: <code>/session &lt;cookie&gt;</code>"
                send_message(chat_id, reply)
            else:
                cookie = args[0]
                send_message(chat_id, f"⏳ Testing session cookie...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.session_hijack, cookie)).start()

        elif cmd == '/nmap':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif not args:
                reply = "❌ Usage: <code>/nmap &lt;host&gt; [ports]</code>\nPorts optional (default: 1-1024)"
                send_message(chat_id, reply)
            else:
                host = args[0]
                ports = args[1] if len(args) > 1 else '1-1024'
                send_message(chat_id, f"⏳ Scanning ports...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.nmap_scan, host, ports)).start()

        # ---------- Reporting & Analysis ----------
        elif cmd == '/report':
            if not args or not args[0].isdigit():
                reply = "❌ Usage: <code>/report &lt;target_id&gt;</code>"
                send_message(chat_id, reply)
            else:
                tid = int(args[0])
                send_message(chat_id, f"⏳ Generating PDF report...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.generate_report_pdf, tid)).start()

        elif cmd == '/sentiment':
            if not args:
                reply = "❌ Usage: <code>/sentiment &lt;text&gt;</code>"
                send_message(chat_id, reply)
            else:
                text = ' '.join(args)
                result = orch.sentiment_analysis(text)
                send_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/score':
            if not args or not args[0].isdigit():
                reply = "❌ Usage: <code>/score &lt;target_id&gt;</code>"
                send_message(chat_id, reply)
            else:
                result = orch.score_target(int(args[0]))
                send_message(chat_id, json.dumps(result, indent=2))

        # ---------- Utilities ----------
        elif cmd == '/phish_link':
            if not args:
                reply = "❌ Usage: <code>/phish_link &lt;email&gt;</code>"
                send_message(chat_id, reply)
            else:
                link = orch.create_phishing_link(args[0])
                send_message(chat_id, json.dumps({'link': link}, indent=2))

        elif cmd == '/geolocate':
            if not args:
                reply = "❌ Usage: <code>/geolocate &lt;ip&gt;</code>"
                send_message(chat_id, reply)
            else:
                result = orch.geolocate_ip(args[0])
                send_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/shodan':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif not args:
                reply = "❌ Usage: <code>/shodan &lt;ip&gt;</code>"
                send_message(chat_id, reply)
            else:
                result = orch.shodan_ip(args[0])
                send_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/darkweb':
            if not args:
                reply = "❌ Usage: <code>/darkweb &lt;email&gt;</code>"
                send_message(chat_id, reply)
            else:
                result = orch.darkweb_search(args[0])
                send_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/encrypt':
            if not args:
                reply = "❌ Usage: <code>/encrypt &lt;text&gt;</code>"
                send_message(chat_id, reply)
            else:
                encrypted = orch.encrypt_data(' '.join(args))
                send_message(chat_id, f"Encrypted: {encrypted}")

        elif cmd == '/decrypt':
            if not args:
                reply = "❌ Usage: <code>/decrypt &lt;encrypted_text&gt;</code>"
                send_message(chat_id, reply)
            else:
                decrypted = orch.decrypt_data(args[0])
                send_message(chat_id, f"Decrypted: {decrypted}")

        # ---------- Admin & System ----------
        elif cmd == '/diagnose':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            else:
                send_message(chat_id, "⏳ Running diagnostics...")
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
                    send_message(chat_id, "❌ Invalid user ID.")

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

        elif cmd == '/defensive':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            else:
                result = orch.defensive_scan()
                send_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/monitor':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                reply = "❌ Usage: <code>/monitor &lt;target_id&gt; &lt;chat_id&gt;</code>"
                send_message(chat_id, reply)
            else:
                orch.start_monitor(int(args[0]), int(args[1]), send_message)
                send_message(chat_id, "✅ Monitoring started.")

        elif cmd == '/record_outcome':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif len(args) < 3:
                reply = "❌ Usage: <code>/record_outcome &lt;target_id&gt; &lt;attack&gt; &lt;success&gt;</code>"
                send_message(chat_id, reply)
            else:
                orch.record_outcome(int(args[0]), args[1], args[2].lower() == 'true')
                send_message(chat_id, "✅ Outcome recorded.")

        elif cmd == '/best_attack':
            if not args or not args[0].isdigit():
                reply = "❌ Usage: <code>/best_attack &lt;target_id&gt;</code>"
                send_message(chat_id, reply)
            else:
                best = orch.get_best_attack(int(args[0]))
                if best:
                    send_message(chat_id, f"Best attack: {best}")
                else:
                    send_message(chat_id, "No data yet for that target.")

        elif cmd == '/share':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                reply = "❌ Usage: <code>/share &lt;target_id&gt; &lt;user_id&gt;</code>"
                send_message(chat_id, reply)
            else:
                orch.share_target(int(args[0]), int(args[1]))
                send_message(chat_id, "✅ Target shared.")

        elif cmd == '/unshare':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                reply = "❌ Usage: <code>/unshare &lt;target_id&gt; &lt;user_id&gt;</code>"
                send_message(chat_id, reply)
            else:
                orch.unshare_target(int(args[0]), int(args[1]))
                send_message(chat_id, "✅ Target unshared.")

        elif cmd == '/plugin_list':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            else:
                plugins = orch.fetch_plugins()
                send_message(chat_id, json.dumps(plugins, indent=2))

        elif cmd == '/plugin_load':
            if not is_admin(chat_id):
                send_message(chat_id, "⛔ Admin only.")
            elif not args:
                reply = "❌ Usage: <code>/plugin_load &lt;plugin_name&gt;</code>"
                send_message(chat_id, reply)
            else:
                result = orch.load_plugin(args[0])
                send_message(chat_id, json.dumps(result, indent=2))

        else:
            reply = "❓ Unknown command. Type <code>/start</code> or <code>/menu</code> for help."
            send_message(chat_id, reply)

    except Exception as e:
        send_message(chat_id, f"⚠️ Unexpected error: {str(e)}")

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
