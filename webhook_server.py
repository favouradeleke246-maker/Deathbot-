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
    '/track': ['/track', '🔍 track', 'track', '☠️ hunt'],
    '/retrieve': ['/retrieve'],
    '/analyze': ['/analyze', '📊 analyze', 'analyze', '💀 slaughter'],
    '/hack_tiktok': ['/hack_tiktok', '🎯 hack tiktok', 'hack tiktok', '🔥 assassinate'],
    '/hack_wa': ['/hack_wa', '📱 hack whatsapp', 'hack whatsapp', '⚡ terminate'],
    '/verify': ['/verify', '✅ verify', 'verify'],
    '/list': ['/list', '📋 list', 'list', '📋 prey list'],
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
    '/instagram': ['/instagram', '🌐 stalk instagram'],
    '/twitter': ['/twitter', '🐦 stalk twitter'],
    '/diagnose': ['/diagnose', '🛡️ diagnostics'],
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
    '/wa_send': ['/wa_send'],
    '/wa_call': ['/wa_call'],
    '/wa_delete': ['/wa_delete'],
    '/wa_hijack': ['/wa_hijack'],
    '/wa_deactivate': ['/wa_deactivate'],
    '/tt_comment': ['/tt_comment'],
    '/tt_reset': ['/tt_reset'],
    '/tt_follow': ['/tt_follow'],
    '/tt_delete': ['/tt_delete'],
    '/tt_report': ['/tt_report'],
    '/wipe_target': ['/wipe_target'],
    '/ransom': ['/ransom'],
    '/panic': ['/panic'],
    '/anonymize': ['/anonymize'],
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

def send_formatted_message(chat_id, text, parse_mode='HTML', reply_markup=None):
    header = "☠️ **SPECTRAX**\n━━━━━━━━━━━━━━━━━━━━\n"
    footer = "\n━━━━━━━━━━━━━━━━━━━━\n⚡"
    full_text = header + text + footer
    replacements = {
        'analysis': 'slaughter',
        'tracking': 'hunting',
        'attack': 'assassination',
        'target': 'prey',
        'success': 'termination',
        'error': 'malfunction'
    }
    for old, new in replacements.items():
        full_text = full_text.replace(old, new)
    send_message(chat_id, full_text, parse_mode, reply_markup)

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
            send_formatted_message(chat_id, json.dumps(result, indent=2, default=default_serializer))
        except Exception as e:
            send_formatted_message(chat_id, f"⚠️ <b>Malfunction:</b> {str(e)}")
    thread = threading.Thread(target=wrapper)
    thread.daemon = True
    thread.start()

def get_main_keyboard():
    return {
        "keyboard": [
            ["☠️ Hunt", "💀 Slaughter"],
            ["🔥 Assassinate", "⚡ Terminate"],
            ["📋 Prey List", "✅ Verify Kill"],
            ["🛡️ Diagnostics", "📄 Execution Report"],
            ["🌐 Stalk Instagram", "🐦 Stalk Twitter"],
            ["❓ Help – Despair"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def is_admin(chat_id):
    return chat_id == SUPER_ADMIN_ID or orch.admin.is_admin(chat_id)

def get_help_text():
    return """
<b>☠️ SpectraX</b>

<b>🔵 Reconnaissance</b>
/track &lt;identifier&gt; – OSINT on username/email/phone
/retrieve &lt;tid&gt; &lt;platform&gt; – Retrieve profile (TikTok)
/breach &lt;email&gt; – Check data breaches
/whois &lt;domain&gt; – WHOIS lookup
/dns &lt;domain&gt; – DNS resolution
/reverseimage &lt;url&gt; – Reverse image search
/instagram &lt;username&gt; – Instagram profile
/twitter &lt;username&gt; – Twitter profile
/geolocate &lt;ip&gt; – IP geolocation
/darkweb &lt;email&gt; – Breach check

<b>🔴 Assassinations</b>
/hack_tiktok &lt;user&gt; &lt;email&gt; – XSS + IDOR (admin)
/hack_wa &lt;phone&gt; – WhatsApp registration check (admin)
/wa_send &lt;phone&gt; &lt;message&gt; – Send real WhatsApp message (admin)
/wa_call &lt;phone&gt; – Initiate WhatsApp call (admin)
/wa_delete &lt;session&gt; – Delete WhatsApp account (admin)
/wa_hijack &lt;phone&gt; &lt;code&gt; – Hijack WhatsApp (admin)
/wa_deactivate &lt;phone&gt; – Send deactivation request (admin)
/tt_comment &lt;video_id&gt; &lt;comment&gt; – Post XSS comment (admin)
/tt_reset &lt;username&gt; &lt;email&gt; – Trigger password reset (admin)
/tt_follow &lt;username&gt; – Follow target (admin)
/tt_delete &lt;session&gt; &lt;user_id&gt; – Delete TikTok account (admin)
/tt_report &lt;session&gt; &lt;username&gt; – Report TikTok account (admin)
/phish &lt;email&gt; [template] – Generate phishing email (admin)
/phish_link &lt;email&gt; – Shorten phishing link (admin)
/stuff &lt;user&gt; &lt;passwords&gt; – Credential stuffing (admin)
/session &lt;cookie&gt; – Test session cookie (admin)
/nmap &lt;host&gt; [ports] – Port scan (admin)

<b>🟢 Analysis</b>
/analyze &lt;tid&gt; – Risk report
/report &lt;tid&gt; – Generate PDF report
/sentiment &lt;text&gt; – Sentiment analysis
/score &lt;tid&gt; – Target priority score
/best_attack &lt;tid&gt; – Best attack from past outcomes

<b>🟣 Utilities</b>
/list – Show all targets
/verify &lt;tid&gt; &lt;platform&gt; – Verify platform presence
/encrypt &lt;text&gt; – Encrypt text
/decrypt &lt;encrypted&gt; – Decrypt text
/wipe_target &lt;tid&gt; – Delete target and all traces (admin)
/ransom – Simulate ransom note (admin)
/panic – Clear all logs (admin)
/anonymize – Refresh Tor identity (admin)

<b>⚙️ Admin & System</b>
/diagnose – System diagnostics
/model &lt;provider&gt; – Switch AI (groq/gemini/deepseek/ollama)
/add_admin &lt;user_id&gt; – Add admin (super admin)
/remove_admin &lt;user_id&gt; – Remove admin (super admin)
/list_admins – List admins (super admin)
/defensive – Scan for exposed keys (admin)
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
            send_formatted_message(chat_id, "❓ Unknown command. Type <code>/start</code> or <code>/menu</code> for help.")
            return 'OK', 200

    parts = text.split()
    args = parts[1:] if len(parts) > 1 else []

    try:
        # ---------- Core Commands ----------
        if cmd == '/start' or cmd == '/menu':
            reply = get_help_text()
            send_formatted_message(chat_id, reply, reply_markup=get_main_keyboard())

        elif cmd == '/track':
            if not args:
                reply = "❌ Usage: <code>/track &lt;identifier&gt;</code>\nExample: <code>/track john_doe</code>"
                send_formatted_message(chat_id, reply)
            else:
                ident = args[0]
                send_formatted_message(chat_id, "⏳ Hunting... Please wait.")
                threading.Thread(target=process_long_task, args=(chat_id, orch.track, ident)).start()

        elif cmd == '/retrieve':
            if len(args) < 2:
                reply = "❌ Usage: <code>/retrieve &lt;target_id&gt; &lt;platform&gt;</code>"
                send_formatted_message(chat_id, reply)
            else:
                try:
                    tid = int(args[0])
                    plat = args[1]
                    send_formatted_message(chat_id, f"⏳ Retrieving from {plat}...")
                    threading.Thread(target=process_long_task, args=(chat_id, orch.retrieve, tid, plat)).start()
                except ValueError:
                    send_formatted_message(chat_id, "❌ Invalid target ID. Must be a number.")

        elif cmd == '/analyze':
            if not args or not args[0].isdigit():
                reply = "❌ Usage: <code>/analyze &lt;target_id&gt;</code>\nExample: <code>/analyze 5</code>"
                send_formatted_message(chat_id, reply)
            else:
                tid = int(args[0])
                send_formatted_message(chat_id, f"⏳ Slaughtering analysis...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.analyze, tid)).start()

        elif cmd == '/hack_tiktok':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                reply = "❌ Usage: <code>/hack_tiktok &lt;username&gt; &lt;attacker_email&gt;</code>"
                send_formatted_message(chat_id, reply)
            else:
                username, email = args[0], args[1]
                send_formatted_message(chat_id, f"⏳ Launching assassination on {username}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.hack_tiktok, username, email)).start()

        elif cmd == '/hack_wa':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif not args:
                reply = "❌ Usage: <code>/hack_wa &lt;phone&gt;</code>\nExample: <code>/hack_wa +2348012345678</code>"
                send_formatted_message(chat_id, reply)
            else:
                phone = args[0]
                send_formatted_message(chat_id, f"⏳ Checking prey for WhatsApp...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.hack_whatsapp, phone)).start()

        elif cmd == '/verify':
            if len(args) < 2:
                reply = "❌ Usage: <code>/verify &lt;target_id&gt; &lt;platform&gt;</code>"
                send_formatted_message(chat_id, reply)
            else:
                try:
                    tid = int(args[0])
                    plat = args[1]
                    send_formatted_message(chat_id, f"⏳ Verifying...")
                    threading.Thread(target=process_long_task, args=(chat_id, orch.verify_target, tid, plat)).start()
                except ValueError:
                    send_formatted_message(chat_id, "❌ Invalid target ID.")

        elif cmd == '/list':
            send_formatted_message(chat_id, "⏳ Fetching prey list...")
            threading.Thread(target=process_long_task, args=(chat_id, orch.list_targets)).start()

        # ---------- OSINT Commands ----------
        elif cmd == '/breach':
            if not args:
                reply = "❌ Usage: <code>/breach &lt;email&gt;</code>"
                send_formatted_message(chat_id, reply)
            else:
                email = args[0]
                send_formatted_message(chat_id, f"⏳ Checking breach for {email}...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.breach_check, email)).start()

        elif cmd == '/whois':
            if not args:
                reply = "❌ Usage: <code>/whois &lt;domain&gt;</code>"
                send_formatted_message(chat_id, reply)
            else:
                domain = args[0]
                send_formatted_message(chat_id, f"⏳ WHOIS lookup...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.whois_lookup, domain)).start()

        elif cmd == '/dns':
            if not args:
                reply = "❌ Usage: <code>/dns &lt;domain&gt;</code>"
                send_formatted_message(chat_id, reply)
            else:
                domain = args[0]
                send_formatted_message(chat_id, f"⏳ DNS resolution...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.dns_enum, domain)).start()

        elif cmd == '/reverseimage':
            if not args:
                reply = "❌ Usage: <code>/reverseimage &lt;image_url&gt;</code>"
                send_formatted_message(chat_id, reply)
            else:
                url = args[0]
                send_formatted_message(chat_id, f"⏳ Reverse image search...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.reverse_image, url)).start()

        elif cmd == '/instagram':
            if not args:
                reply = "❌ Usage: <code>/instagram &lt;username&gt;</code>"
                send_formatted_message(chat_id, reply)
            else:
                username = args[0]
                send_formatted_message(chat_id, f"⏳ Stalking Instagram...")
                threading.Thread(target=process_long_task, args=(chat_id, orch.instagram_profile, username)).start()

        elif cmd == '/twitter':
            if not args:
