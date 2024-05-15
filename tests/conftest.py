"""
Configuration and fixtures for pytest testing environment.
This module prepares and configures the testing environment before running tests, including setting up import paths.
"""

import sys
import os

# Add the src directory to the PYTHONPATH for easy import of the modules under test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
