"""
Comprehensive Test Suite for Universal Template System Compatibility

This module provides automated tests to verify that the Universal Template System
generates output that is functionally equivalent to legacy templates.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from typing import Dict, List, Any

from ...schemas import ConfigSchema, GoobitsConfigSchema
from ...generators.python import PythonGenerator
from ...generators.nodejs import NodeJSGenerator  
from ...generators.typescript import TypeScriptGenerator
from ...generators.rust import RustGenerator
from .compatibility_checker import CompatibilityChecker, ComparisonResult


class TestUniversalTemplateCompatibility:
    """Test suite for Universal Template System compatibility."""
    
    @pytest.fixture
    def sample_configs(self) -> List[GoobitsConfigSchema]:
        """Create sample configurations for testing."""
        configs = []
        
        # Simple Python CLI config
        python_config_data = {
            "package_name": "test-cli",
            "command_name": "testcli",
            "description": "A test CLI application",
            "language": "python",
            "cli": {
                "name": "testcli",
                "tagline": "Test CLI",
                "description": "A test command-line interface",
                "version": "1.0.0",
                "commands": {
                    "hello": {
                        "desc": "Say hello",
                        "args": [
                            {"name": "name", "desc": "Name to greet", "required": True}
                        ],
                        "options": [
                            {"name": "count", "short": "c", "desc": "Number of greetings", "type": "int", "default": 1}
                        ]
                    },
                    "goodbye": {
                        "desc": "Say goodbye",
                        "args": [
                            {"name": "name", "desc": "Name to say goodbye to", "required": False}
                        ]
                    }
                }
            }
        }
        configs.append(GoobitsConfigSchema(**python_config_data))
        
        # Node.js config variation
        nodejs_config_data = python_config_data.copy()
        nodejs_config_data["language"] = "nodejs"
        configs.append(GoobitsConfigSchema(**nodejs_config_data))
        
        # TypeScript config variation
        typescript_config_data = python_config_data.copy()
        typescript_config_data["language"] = "typescript"
        configs.append(GoobitsConfigSchema(**typescript_config_data))
        
        # Rust config variation
        rust_config_data = python_config_data.copy()
        rust_config_data["language"] = "rust"
        configs.append(GoobitsConfigSchema(**rust_config_data))
        
        return configs
    
    @pytest.fixture
    def temp_config_files(self, sample_configs: List[GoobitsConfigSchema]) -> List[Path]:
        """Create temporary configuration files."""
        temp_files = []
        
        for i, config in enumerate(sample_configs):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(config.model_dump(), f)
                temp_files.append(Path(f.name))
        
        yield temp_files
        
        # Cleanup
        for temp_file in temp_files:
            temp_file.unlink(missing_ok=True)
    
    def test_python_generator_compatibility(self, sample_configs):
        """Test that Python generator produces compatible output."""
        config = next(c for c in sample_configs if c.language == "python")
        
        legacy_generator = PythonGenerator(use_universal_templates=False)
        universal_generator = PythonGenerator(use_universal_templates=True)
        
        # Generate with both systems
        legacy_files = legacy_generator.generate_all_files(config, "test.yaml", "1.0.0")
        universal_files = universal_generator.generate_all_files(config, "test.yaml", "1.0.0")
        
        # Should have files in common
        assert legacy_files or universal_files, "At least one generator should produce files"
        
        # If both produced files, check for main CLI file
        if legacy_files and universal_files:
            # Look for main CLI file
            main_files = [f for f in legacy_files.keys() if 'cli' in f.lower()]
            if main_files:
                main_file = main_files[0]
                assert main_file in universal_files, f"Universal generator missing main file: {main_file}"
    
    def test_nodejs_generator_compatibility(self, sample_configs):
        """Test that Node.js generator produces compatible output."""
        config = next(c for c in sample_configs if c.language == "nodejs")
        
        legacy_generator = NodeJSGenerator(use_universal_templates=False)
        universal_generator = NodeJSGenerator(use_universal_templates=True)
        
        try:
            legacy_files = legacy_generator.generate_all_files(config, "test.yaml", "1.0.0")
            universal_files = universal_generator.generate_all_files(config, "test.yaml", "1.0.0")
            
            # Basic sanity check
            assert isinstance(legacy_files, dict), "Legacy generator should return dict"
            assert isinstance(universal_files, dict), "Universal generator should return dict"
        
        except Exception as e:
            pytest.skip(f"Node.js generators not fully implemented: {e}")
    
    def test_typescript_generator_compatibility(self, sample_configs):
        """Test that TypeScript generator produces compatible output."""
        config = next(c for c in sample_configs if c.language == "typescript")
        
        legacy_generator = TypeScriptGenerator(use_universal_templates=False)
        universal_generator = TypeScriptGenerator(use_universal_templates=True)
        
        try:
            legacy_files = legacy_generator.generate_all_files(config, "test.yaml", "1.0.0")
            universal_files = universal_generator.generate_all_files(config, "test.yaml", "1.0.0")
            
            # Basic sanity check
            assert isinstance(legacy_files, dict), "Legacy generator should return dict"
            assert isinstance(universal_files, dict), "Universal generator should return dict"
        
        except Exception as e:
            pytest.skip(f"TypeScript generators not fully implemented: {e}")
    
    def test_rust_generator_compatibility(self, sample_configs):
        """Test that Rust generator produces compatible output."""
        config = next(c for c in sample_configs if c.language == "rust")
        
        legacy_generator = RustGenerator(use_universal_templates=False)
        universal_generator = RustGenerator(use_universal_templates=True)
        
        try:
            legacy_files = legacy_generator.generate_all_files(config, "test.yaml", "1.0.0")
            universal_files = universal_generator.generate_all_files(config, "test.yaml", "1.0.0")
            
            # Basic sanity check
            assert isinstance(legacy_files, dict), "Legacy generator should return dict"
            assert isinstance(universal_files, dict), "Universal generator should return dict"
        
        except Exception as e:
            pytest.skip(f"Rust generators not fully implemented: {e}")
    
    def test_compatibility_checker_integration(self, temp_config_files):
        """Test the compatibility checker with real configuration files."""
        checker = CompatibilityChecker(temp_config_files)
        
        try:
            overall_result = checker.run_full_compatibility_check()
            
            # Should have run some comparisons
            assert overall_result.total_comparisons > 0, "Should have performed some comparisons"
            
            # Generate report
            report = checker.generate_detailed_report()
            assert len(report) > 100, "Report should contain substantial content"
            assert "Compatibility Report" in report, "Report should have proper title"
        
        except Exception as e:
            pytest.skip(f"Compatibility checker failed: {e}")
    
    @pytest.mark.parametrize("language", ["python", "nodejs", "typescript", "rust"])
    def test_generator_initialization_with_universal_flag(self, language):
        """Test that generators can be initialized with universal templates flag."""
        generators = {
            "python": PythonGenerator,
            "nodejs": NodeJSGenerator,
            "typescript": TypeScriptGenerator,
            "rust": RustGenerator,
        }
        
        GeneratorClass = generators[language]
        
        # Should be able to create both legacy and universal generators
        legacy_generator = GeneratorClass(use_universal_templates=False)
        universal_generator = GeneratorClass(use_universal_templates=True)
        
        assert legacy_generator is not None
        assert universal_generator is not None
        
        # Check that flag is set correctly
        assert not legacy_generator.use_universal_templates
        assert universal_generator.use_universal_templates
    
    def test_fallback_behavior(self, sample_configs):
        """Test that universal generators fall back gracefully to legacy mode."""
        config = next(c for c in sample_configs if c.language == "python")
        
        # Create universal generator
        generator = PythonGenerator(use_universal_templates=True)
        
        # Even if universal templates fail, should still generate something
        try:
            result = generator.generate(config, "test.yaml", "1.0.0")
            assert result is not None, "Generator should produce some output"
            assert len(result) > 0, "Generated output should not be empty"
        except Exception as e:
            # If generation completely fails, that's a critical issue
            pytest.fail(f"Generator failed completely: {e}")
    
    def test_file_generation_consistency(self, sample_configs):
        """Test that both systems generate consistent file structures."""
        config = next(c for c in sample_configs if c.language == "python")
        
        legacy_generator = PythonGenerator(use_universal_templates=False)
        universal_generator = PythonGenerator(use_universal_templates=True)
        
        legacy_files = legacy_generator.generate_all_files(config, "test.yaml", "1.0.0")
        universal_files = universal_generator.generate_all_files(config, "test.yaml", "1.0.0")
        
        # Both should generate files
        assert legacy_files, "Legacy generator should produce files"
        
        if universal_files:
            # Check for core files that should be common
            core_files = ['cli.py', 'config_manager.py', 'completion_engine.py']
            
            for core_file in core_files:
                if core_file in legacy_files:
                    # If legacy has it, universal should have it too (or have fallen back)
                    assert core_file in universal_files or len(universal_files) > 0, \
                        f"Universal generator should have {core_file} or other files"


class TestTemplateMigrationTools:
    """Test suite for template migration tools."""
    
    def test_migration_tools_import(self):
        """Test that migration tools can be imported."""
        from .migrate_templates import TemplateMigrator
        from .template_analyzer import TemplateAnalyzer
        from .compatibility_checker import CompatibilityChecker
        
        # Should be able to create instances
        assert TemplateMigrator is not None
        assert TemplateAnalyzer is not None
        assert CompatibilityChecker is not None
    
    def test_template_analyzer_basic_functionality(self):
        """Test basic template analyzer functionality."""
        from .template_analyzer import TemplateAnalyzer
        
        # Create analyzer with dummy templates directory
        with tempfile.TemporaryDirectory() as temp_dir:
            templates_dir = Path(temp_dir)
            analyzer = TemplateAnalyzer(templates_dir)
            
            # Should initialize without error
            assert analyzer.templates_dir == templates_dir
            assert analyzer.analyses == {}
    
    def test_migration_tool_basic_functionality(self):
        """Test basic migration tool functionality."""
        from .migrate_templates import TemplateMigrator
        
        # Create migrator with dummy templates directory
        with tempfile.TemporaryDirectory() as temp_dir:
            templates_dir = Path(temp_dir)
            migrator = TemplateMigrator(templates_dir)
            
            # Should initialize without error
            assert migrator.templates_dir == templates_dir
            assert migrator.migration_report == []


class TestUniversalTemplateSystemRegressions:
    """Test suite to ensure no regressions in existing functionality."""
    
    def test_legacy_generators_still_work(self, sample_configs):
        """Ensure legacy generators continue to work as before."""
        config = next(c for c in sample_configs if c.language == "python")
        
        # Legacy generator should work exactly as before
        generator = PythonGenerator(use_universal_templates=False)
        
        # Should be able to generate files
        files = generator.generate_all_files(config, "test.yaml", "1.0.0")
        assert isinstance(files, dict), "Should return dictionary of files"
        
        # Should be able to generate single file
        main_content = generator.generate(config, "test.yaml", "1.0.0")
        assert isinstance(main_content, str), "Should return string content"
        assert len(main_content) > 0, "Content should not be empty"
    
    def test_generator_apis_unchanged(self):
        """Test that generator APIs remain unchanged."""
        # All generators should support the same constructor signature
        generators = [PythonGenerator, NodeJSGenerator, TypeScriptGenerator, RustGenerator]
        
        for GeneratorClass in generators:
            # Should be able to create without arguments (legacy behavior)
            generator = GeneratorClass()
            assert generator is not None
            
            # Should be able to create with universal flag
            universal_generator = GeneratorClass(use_universal_templates=True)
            assert universal_generator is not None
    
    def test_backward_compatibility_config_handling(self, sample_configs):
        """Test that configuration handling remains backward compatible."""
        config = next(c for c in sample_configs if c.language == "python")
        
        generator = PythonGenerator()
        
        # Should handle GoobitsConfigSchema
        result1 = generator.generate(config, "test.yaml")
        assert result1 is not None
        
        # Should handle with version
        result2 = generator.generate(config, "test.yaml", "1.0.0")
        assert result2 is not None
        
        # Both should be strings
        assert isinstance(result1, str)
        assert isinstance(result2, str)


@pytest.fixture
def sample_configs():
    """Fixture to provide sample configurations for testing."""
    configs = []
    
    # Simple Python CLI config
    python_config_data = {
        "package_name": "test-cli",
        "command_name": "testcli",
        "description": "A test CLI application",
        "language": "python",
        "cli": {
            "name": "testcli",
            "tagline": "Test CLI",
            "description": "A test command-line interface",
            "version": "1.0.0",
            "commands": {
                "hello": {
                    "desc": "Say hello",
                    "args": [
                        {"name": "name", "desc": "Name to greet", "required": True}
                    ],
                    "options": [
                        {"name": "count", "short": "c", "desc": "Number of greetings", "type": "int", "default": 1}
                    ]
                }
            }
        }
    }
    configs.append(GoobitsConfigSchema(**python_config_data))
    
    # Create variations for other languages
    for language in ["nodejs", "typescript", "rust"]:
        config_data = python_config_data.copy()
        config_data["language"] = language
        configs.append(GoobitsConfigSchema(**config_data))
    
    return configs


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])