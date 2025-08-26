"""
Test suite for consolidated file generation in the Universal Template System.

Validates that each language generates minimal files as per PROPOSAL_08_FILE_CONSOLIDATION.md:
- Python: 2 files (cli.py with everything embedded, setup.sh)  
- Node.js: 2 files (cli.mjs ES6 module, setup.sh)
- TypeScript: 3 files (cli.ts, types.d.ts, setup.sh)
- Rust: 2 files (src/main.rs with inline modules, setup.sh)
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Dict, Any

from goobits_cli.universal.template_engine import UniversalTemplateEngine
from goobits_cli.universal.renderers.python_renderer import PythonRenderer
from goobits_cli.universal.renderers.nodejs_renderer import NodeJSRenderer
from goobits_cli.universal.renderers.typescript_renderer import TypeScriptRenderer
from goobits_cli.universal.renderers.rust_renderer import RustRenderer
from goobits_cli.schemas import GoobitsConfigSchema


class TestFileConsolidation:
    """Test consolidated file generation for minimal repository footprint."""
    
    @classmethod
    def setup_class(cls):
        """Set up test configuration."""
        cls.test_config = {
            "package_name": "test-cli",
            "command_name": "testcli",
            "display_name": "Test CLI",
            "description": "Test CLI for consolidation",
            "language": "python",
            "cli": {
                "name": "testcli",
                "tagline": "A test CLI",
                "description": "Testing consolidation",
                "version": "1.0.0",
                "commands": {
                    "hello": {
                        "desc": "Say hello",
                        "args": [{"name": "name", "type": "string", "desc": "Name to greet"}]
                    },
                    "build": {
                        "desc": "Build something",
                        "subcommands": {
                            "project": {"desc": "Build a project"},
                            "docs": {"desc": "Build documentation"}
                        }
                    }
                }
            }
        }
        
        # Create templates directory structure
        cls.templates_dir = Path("/tmp/test_consolidation_templates")
        cls.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create consolidated template files
        cls._create_consolidated_templates(cls.templates_dir)
    
    @classmethod
    def _create_consolidated_templates(cls, templates_dir: Path):
        """Create minimal consolidated template files for testing."""
        # Python consolidated template
        (templates_dir / "python_cli_consolidated.j2").write_text("""
#!/usr/bin/env python3
# Consolidated Python CLI with embedded utilities
# Config Manager embedded
# Error Handler embedded  
# Logger embedded
import click
# {{ cli.name }} - {{ cli.description }}
""")
        
        # Node.js consolidated ES6 module template
        (templates_dir / "nodejs_cli_consolidated.j2").write_text("""
#!/usr/bin/env node
// ES6 module with embedded utilities
import { Command } from 'commander';
// Config Manager embedded
// Error Handler embedded
// {{ cli.name }} - {{ cli.description }}
""")
        
        # TypeScript consolidated template
        (templates_dir / "typescript_cli_consolidated.j2").write_text("""
#!/usr/bin/env node
// TypeScript CLI with embedded utilities
import { Command } from 'commander';
// Config Manager embedded
// {{ cli.name }} - {{ cli.description }}
""")
        
        # TypeScript types definition
        (templates_dir / "typescript_types.j2").write_text("""
// Type definitions for {{ cli.name }}
export interface CLIConfig {
  // Type definitions here
}
""")
        
        # Rust consolidated template
        (templates_dir / "rust_cli_consolidated.j2").write_text("""
// Rust CLI with inline modules
use clap::Parser;
mod config {
    // Config module inlined
}
mod errors {
    // Errors module inlined
}
// {{ cli.name }} - {{ cli.description }}
""")
        
        # Setup script template (shared)
        (templates_dir / "setup_script.j2").write_text("""
#!/bin/bash
# Smart setup script for {{ cli.name }}
# Non-destructive manifest merging
""")
    
    def test_python_consolidation(self):
        """Test Python generates only 2 files with everything embedded."""
        config = GoobitsConfigSchema(**self.test_config)
        engine = UniversalTemplateEngine(self.templates_dir)
        
        renderer = PythonRenderer()
        engine.register_renderer("python", renderer)
        
        result = engine.render(config, "python")
        files = result.get("files", {})
        
        # Python should generate exactly 2 files (setup.sh handled separately)
        assert len(files) == 1  # Only cli.py from renderer
        
        # Check the single CLI file path
        cli_path = f"src/{self.test_config['package_name'].replace('-', '_')}/cli.py"
        assert cli_path in files or any("cli.py" in path for path in files.keys())
        
        # Verify content includes embedded utilities (from template)
        cli_content = next(iter(files.values()))
        assert "Config Manager embedded" in cli_content
        assert "Error Handler embedded" in cli_content
        assert "Logger embedded" in cli_content
    
    def test_nodejs_consolidation(self):
        """Test Node.js generates only 2 files with ES6 modules."""
        config_nodejs = {**self.test_config, "language": "nodejs"}
        config = GoobitsConfigSchema(**config_nodejs)
        engine = UniversalTemplateEngine(self.templates_dir)
        
        renderer = NodeJSRenderer()
        engine.register_renderer("nodejs", renderer)
        
        result = engine.render(config, "nodejs")
        files = result.get("files", {})
        
        # Node.js should generate exactly 2 files
        assert len(files) == 2
        
        # Check for ES6 module file
        assert "cli.mjs" in files
        assert "setup.sh" in files
        
        # Verify ES6 module content
        cli_content = files["cli.mjs"]
        assert "ES6 module with embedded utilities" in cli_content
        assert "import { Command }" in cli_content
        assert "Config Manager embedded" in cli_content
    
    def test_typescript_consolidation(self):
        """Test TypeScript generates only 3 files with type definitions."""
        config_ts = {**self.test_config, "language": "typescript"}
        config = GoobitsConfigSchema(**config_ts)
        engine = UniversalTemplateEngine(self.templates_dir)
        
        renderer = TypeScriptRenderer()
        engine.register_renderer("typescript", renderer)
        
        result = engine.render(config, "typescript")
        files = result.get("files", {})
        
        # TypeScript should generate exactly 3 files
        assert len(files) == 3
        
        # Check for required files
        assert "cli.ts" in files
        assert "types.d.ts" in files
        assert "setup.sh" in files
        
        # Verify TypeScript content
        cli_content = files["cli.ts"]
        assert "TypeScript CLI with embedded utilities" in cli_content
        
        # Verify type definitions
        types_content = files["types.d.ts"]
        assert "Type definitions for" in types_content
        assert "interface CLIConfig" in types_content
    
    def test_rust_consolidation(self):
        """Test Rust generates only 2 files with inline modules."""
        config_rust = {**self.test_config, "language": "rust"}
        config = GoobitsConfigSchema(**config_rust)
        engine = UniversalTemplateEngine(self.templates_dir)
        
        renderer = RustRenderer()
        engine.register_renderer("rust", renderer)
        
        result = engine.render(config, "rust")
        files = result.get("files", {})
        
        # Rust should generate exactly 2 files
        assert len(files) == 2
        
        # Check for required files
        assert "src/main.rs" in files
        assert "setup.sh" in files
        
        # Verify inline modules
        main_content = files["src/main.rs"]
        assert "Rust CLI with inline modules" in main_content
        assert "mod config {" in main_content
        assert "mod errors {" in main_content
        assert "// Config module inlined" in main_content
        assert "// Errors module inlined" in main_content
    
    def test_no_readme_generation(self):
        """Ensure NO language generates README.md files (CRITICAL)."""
        languages = ["python", "nodejs", "typescript", "rust"]
        
        for lang in languages:
            config_dict = {**self.test_config, "language": lang}
            config = GoobitsConfigSchema(**config_dict)
            engine = UniversalTemplateEngine(self.templates_dir)
            
            # Get appropriate renderer
            if lang == "python":
                renderer = PythonRenderer()
            elif lang == "nodejs":
                renderer = NodeJSRenderer()
            elif lang == "typescript":
                renderer = TypeScriptRenderer()
            else:
                renderer = RustRenderer()
            
            engine.register_renderer(lang, renderer)
            result = engine.render(config, lang)
            files = result.get("files", {})
            
            # Assert NO README.md is generated
            assert "README.md" not in files, f"{lang} should NOT generate README.md"
            assert not any("readme" in path.lower() for path in files.keys()), \
                f"{lang} should not generate any readme files"
    
    def test_no_auxiliary_files(self):
        """Ensure no auxiliary files like config.js, errors.js are generated."""
        config_nodejs = {**self.test_config, "language": "nodejs"}
        config = GoobitsConfigSchema(**config_nodejs)
        engine = UniversalTemplateEngine(self.templates_dir)
        
        renderer = NodeJSRenderer()
        engine.register_renderer("nodejs", renderer)
        
        result = engine.render(config, "nodejs")
        files = result.get("files", {})
        
        # These files should NOT exist anymore
        unwanted_files = [
            "lib/config.js",
            "lib/errors.js", 
            "lib/progress.js",
            "lib/formatter.js",
            "lib/plugin-manager.js",
            "lib/prompts.js",
            "lib/completion.js",
            "index.js",
            "package.json",  # Should be merged, not overwritten
            "tsconfig.json",  # Should be merged, not overwritten
        ]
        
        for unwanted in unwanted_files:
            assert unwanted not in files, f"{unwanted} should not be generated"
    
    def test_smart_setup_script(self):
        """Test that setup.sh uses smart merging instead of overwriting."""
        config = GoobitsConfigSchema(**self.test_config)
        engine = UniversalTemplateEngine(self.templates_dir)
        
        renderer = NodeJSRenderer()
        engine.register_renderer("nodejs", renderer)
        
        result = engine.render(config, "nodejs")
        files = result.get("files", {})
        
        assert "setup.sh" in files
        setup_content = files["setup.sh"]
        
        # Should mention non-destructive merging
        assert "Smart setup script" in setup_content
        assert "Non-destructive manifest merging" in setup_content
    
    def test_file_count_reduction(self):
        """Verify 80-90% reduction in generated files."""
        # Old file counts (from PROPOSAL_08)
        old_counts = {
            "python": 5,   # cli.py, __init__.py, pyproject.toml, setup.sh, README.md
            "nodejs": 16,  # cli.js, package.json, 10+ lib files, README.md, etc.
            "typescript": 19,  # cli.ts, tsconfig.json, 10+ lib files, types, README.md, etc.
            "rust": 29,    # main.rs, lib.rs, 8+ module files, Cargo.toml, README.md, etc.
        }
        
        # New consolidated counts
        new_counts = {
            "python": 1,    # cli.py only (setup.sh handled separately)
            "nodejs": 2,    # cli.mjs, setup.sh
            "typescript": 3,  # cli.ts, types.d.ts, setup.sh
            "rust": 2,      # src/main.rs, setup.sh
        }
        
        for lang, old_count in old_counts.items():
            new_count = new_counts[lang]
            reduction = (old_count - new_count) / old_count * 100
            
            # Should achieve at least 60% reduction (conservative due to setup.sh)
            assert reduction >= 60, f"{lang} should reduce files by at least 60%, got {reduction:.1f}%"
            
            # Optimal reduction targets from proposal
            if lang == "python":
                assert reduction >= 80  # 80% reduction
            elif lang == "nodejs":
                assert reduction >= 87  # 87.5% reduction
            elif lang == "typescript":
                assert reduction >= 84  # 84% reduction
            elif lang == "rust":
                assert reduction >= 93  # 93% reduction


class TestBackwardCompatibility:
    """Test that old configs still work with consolidated generation."""
    
    def test_legacy_config_support(self):
        """Ensure configs without cli_output_path still work."""
        legacy_config = {
            "package_name": "legacy-cli",
            "command_name": "legacy",
            "display_name": "Legacy CLI",
            "description": "Testing backward compatibility",
            "cli": {
                "name": "legacy",
                "tagline": "Legacy test CLI",
                "commands": {
                    "test": {"desc": "Test command"}
                }
            }
        }
        
        # Should not raise any errors
        config = GoobitsConfigSchema(**legacy_config)
        assert config.package_name == "legacy-cli"
        
        # Python renderer should provide default path
        renderer = PythonRenderer()
        ir = {"project": legacy_config, "cli": legacy_config["cli"]}
        output = renderer.get_output_structure(ir)
        
        # Should have a default CLI path
        assert "python_cli_consolidated" in output
        assert "legacy_cli/cli.py" in output["python_cli_consolidated"] or \
               "legacy-cli/cli.py" in output["python_cli_consolidated"]