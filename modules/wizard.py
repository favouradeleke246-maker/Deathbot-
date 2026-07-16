class Wizard:
    """Interactive wizard for novice users (stateful)."""
    def __init__(self):
        self.sessions = {}

    def start_track(self, chat_id, send_func):
        """Start tracking wizard."""
        send_func(chat_id, "Please enter the target identifier (username, email, or phone):")
        self.sessions[chat_id] = {'step': 'track_identifier'}

    def process_input(self, chat_id, text, orchestrator):
        """Process user input based on current wizard step."""
        session = self.sessions.get(chat_id, {})
        step = session.get('step')
        if step == 'track_identifier':
            result = orchestrator.track(text)
            orchestrator.send_message(chat_id, json.dumps(result, indent=2))
            del self.sessions[chat_id]
            return True
        return False
