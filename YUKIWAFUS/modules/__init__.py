import glob
import logging
from os.path import basename, dirname, isfile

from YUKIWAFUS.logging import LOGGER

# ── Auto load all .py files in modules/ ──────────────────────────────────────
def _list_all_modules():
    mod_paths = glob.glob(dirname(__file__) + "/*.py")
    all_modules = [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]
    return all_modules

ALL_MODULES = _list_all_modules()
LOGGER.info(f"Modules found: {ALL_MODULES}")

__all__ = ALL_MODULES + ["ALL_MODULES"]

