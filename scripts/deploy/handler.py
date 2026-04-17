import os
import sys

parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_directory not in sys.path:
    sys.path.insert(0, parent_directory)

from src.handler import *  # noqa: F401,F403
