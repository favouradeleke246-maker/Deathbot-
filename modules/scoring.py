def calculate_score(target_data):
    score = 0
    if target_data.get('emails'):
        score += 10
    if target_data.get('phones'):
        score += 15
    profiles = target_data.get('profiles', {})
    if profiles:
        score += 5 * len(profiles)
    if target_data.get('social_media'):
        score += 10
    return min(score, 100)
