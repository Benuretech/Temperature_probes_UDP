"""
This module enables other modules to find the project root directory regardless of their location in the directory structure.
"""

# Importing the 'os' module to work with file and directory paths
import os

# Function to find the directory path of the current script
def rooth_path_finder():
    """
    This function determines the absolute directory path of the current script file.

    Steps:
    1. `__file__` provides the relative path of the current script.
    2. `os.path.abspath(__file__)` converts the relative path to an absolute path.
    3. `os.path.dirname()` extracts the directory portion of the absolute path.

    Args:
        None
        
    Returns:
        str: The absolute directory path of the current script.
    """

    # Returns the absolute directory path of the current file
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))