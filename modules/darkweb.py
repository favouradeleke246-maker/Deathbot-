from modules.advanced_osint import AdvancedOSINT

def search_breaches(email):
    result = AdvancedOSINT.email_breach(email)
    return result
