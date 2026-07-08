import re

class Analyzer:
    @staticmethod
    def generate_report(target_id, osint_data, profile_data):
        sherlock = osint_data.get('sherlock', {})
        maigret = osint_data.get('maigret', {})
        total = len(sherlock) + len(maigret)
        report = {
            'target_id': target_id,
            'profiles_found': total,
            'top_sites': list(sherlock.keys())[:10],
            'emails': [],
            'phones': [],
            'risk_score': min(100, total * 5)
        }
        if profile_data:
            for key, value in profile_data.items():
                if isinstance(value, str):
                    if '@' in value and '.' in value:
                        report['emails'].append(value)
                    if re.search(r'\+?\d[\d\s\-]{8,}', value):
                        report['phones'].append(value)
        # Also from OSINT URLs
        for site, url in sherlock.items():
            if '@' in url:
                report['emails'].append(url)
        return report
