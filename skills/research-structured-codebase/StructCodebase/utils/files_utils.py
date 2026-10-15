"""File system utility helpers."""

import os
import shutil
from loguru import logger


def remove_dir(dir_path):
    """Remove a single directory.
    """
    if not os.path.exists(dir_path):
        return True
    try:
      shutil.rmtree(dir_path, ignore_errors=False)
    except Exception as e:
      logger.error(f"Failed to remove directory {dir_path} with error: {e}")

    return not os.path.exists(dir_path)
