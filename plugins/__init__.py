"""
Plugin loader for Exploit Bot.
"""
import importlib
import pkgutil
import os
from modules.utils import logger

PLUGIN_DIR = os.path.dirname(__file__)

def load_plugins(orchestrator):
    plugins = {}
    for finder, name, ispkg in pkgutil.iter_modules([PLUGIN_DIR]):
        try:
            module = importlib.import_module(f'plugins.{name}')
            if hasattr(module, 'Plugin'):
                plugins[name] = module.Plugin(orchestrator)
                logger.info(f"Loaded plugin: {name}")
        except Exception as e:
            logger.error(f"Failed to load plugin {name}: {e}")
    return plugins
