"""
Plugin system for Exploit Bot.
Place custom plugins in this folder. They will be auto‑loaded by the orchestrator.
"""
import importlib
import pkgutil
import os
from modules.utils import logger

PLUGIN_DIR = os.path.dirname(__file__)

def load_plugins(orchestrator):
    """
    Discover and load all Python modules in the plugins folder
    that have a `Plugin` class.
    """
    plugins = {}
    for finder, name, ispkg in pkgutil.iter_modules([PLUGIN_DIR]):
        try:
            module = importlib.import_module(f'plugins.{name}')
            if hasattr(module, 'Plugin'):
                plugin_instance = module.Plugin(orchestrator)
                plugins[name] = plugin_instance
                logger.info(f"Loaded plugin: {name}")
        except Exception as e:
            logger.error(f"Failed to load plugin {name}: {e}")
    return plugins
