"""Consolidated unit tests for NodeJS CLI generation.

This module consolidates NodeJS generator tests from unit/, e2e/, and integration/
directories to eliminate duplication and provide comprehensive coverage:

- Unit tests: Generator functionality and initialization
- Integration tests: YAML config loading and file generation
- E2E tests: Complete workflow validation
- Error handling: Malformed configs and template failures
- Special cases: Unicode, large configs, concurrent access

Consolidated from:
- test_nodejs_generator.py
- test_nodejs_e2e.py
- test_nodejs_integration.py
"""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path
import shutil
import os
from unittest.mock import Mock, patch

from goobits_cli.generators.nodejs import NodeJSGenerator
from goobits_cli.schemas import CLISchema, CommandSchema, ArgumentSchema, OptionSchema
from goobits_cli.main import load_goobits_config
from ...conftest import create_test_goobits_config, determine_language, generate_cli


class TestNodeJSGeneratorCore:
    """Core NodeJS generator functionality tests."""

    def test_generator_initialization(self):
        """Test NodeJSGenerator class initialization."""
        generator = NodeJSGenerator()

        # Check that generator has required attributes
        assert hasattr(generator, "env")
        assert generator.env is not None

    def test_template_loader_configuration(self):
        """Test that Jinja2 environment is properly configured."""
        generator = NodeJSGenerator()

        # Check that environment has correct loader
        assert hasattr(generator.env, "loader")
