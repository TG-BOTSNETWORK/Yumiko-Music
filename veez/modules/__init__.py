import os
import importlib
from veez.logger import LOGGER

MODULES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ""))

def load_modules():
    if not os.path.exists(MODULES_DIR):
        LOGGER.error(f"Modules directory not found: {MODULES_DIR}")
        raise FileNotFoundError(f"Modules directory not found: {MODULES_DIR}")

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
