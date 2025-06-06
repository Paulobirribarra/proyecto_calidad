# This file makes the scripts directory a Python package
# and ensures that our modules can be imported

from .logger_config import setup_script_logging

__all__ = ['setup_script_logging']
