"""Test configuration templates and runners for integration tests.

This module provides predefined test configurations and scenario runners
for different installation scenarios and edge cases.
"""

# Re-export the classes from test_config_validation.py for compatibility
from .test_config_validation import TestConfigTemplates, TestScenarioRunner

__all__ = ["TestConfigTemplates", "TestScenarioRunner"]
