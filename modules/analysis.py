import re
class Analyzer:
    @staticmethod
    def generate_report(target_id, osint_data, profile_data):
        report = {
            'target_id': target_id,
            'profiles_found': len(osint_data.get('sherlock', {})) + len(osint_data.get('maigret', {})),
            'top_sites': list(osint_data.get('sherlock', {}).keys())[:10],
            'emails': [],
            'phones': [],
            'risk_score': min(100, (len(osint_data.get('sherlock', {})) + len(osint_data.get('maigret', {}))) * 5)
        }
        if profile_data:
            for v in profile_data.values():
                if isinstance(v, str):
                    if '@' in v:
                        report['emails'].append(v)
                    if re.search(r'\+?\d[\d\s\-]{8,}', v):
                        report['phones'].append(v)
        return report
