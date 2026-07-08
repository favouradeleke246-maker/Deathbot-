"""
Sample plugin – shows how to extend the bot with custom functionality.
"""
from modules.utils import logger

class Plugin:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.name = "SamplePlugin"
        self.description = "Demonstrates plugin architecture"

    def run(self, target_data):
        """Called by orchestrator when plugin is invoked."""
        logger.info(f"SamplePlugin running on {target_data}")
        return {
            'success': True,
            'output': f'Plugin executed on {target_data.get("identifier", "unknown")}'
        }

    def on_load(self):
        """Called when plugin is first loaded."""
        logger.info(f"SamplePlugin loaded. Description: {self.description}")
