import os
import importlib
from veez.logger import LOGGER

MODULES_DIR = os.path.join(os.path.dirname(__file__), "modules")

def load_modules():
    LOGGER.info("Loading modules...")
    for filename in os.listdir(MODULES_DIR):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"veez.modules.{filename[:-3]}"
            try:
                importlib.import_module(module_name)
                LOGGER.info(f"Successfully loaded module: {module_name}")
            except Exception as e:
                LOGGER.error(f"Failed to load module {module_name}: {e}")

load_modules()
