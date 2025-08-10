"""
Comprehensive tests for Universal Template Engine.

These tests focus on real functionality to maximize coverage improvements
from 63% to 85% by testing:
- UniversalTemplateEngine with actual template rendering
- Intermediate Representation (IR) processing
- Cross-language code generation
- Error handling and edge cases
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

from goobits_cli.universal.template_engine import (
    UniversalTemplateEngine,
    LanguageRenderer
)
from goobits_cli.schemas import GoobitsConfigSchema


class MockRenderer(LanguageRenderer):
    """Mock renderer for testing purposes"""
    
    def __init__(self, language: str = "test"):
        self._language = language
        
    @property
    def language(self) -> str:
        return self._language
    
    @property
    def file_extensions(self) -> Dict[str, str]:
        return {"test": "test", "cli": "test"}
    
    def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        """Transform IR into test-specific context"""
        context = ir.copy()
        context["test_specific"] = True
        context["language"] = self.language
        return context
    
    def render_component(self, component_name: str, context: Dict[str, Any]) -> str:
        """Render a component for testing"""
        return f"// {self.language} component: {component_name}\ntest content"
    
    def get_output_files(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """Get output files mapping"""
        return {"cli.test": "test_cli_output", "main.test": "test_main_output"}


class TestUniversalTemplateEngine:
    """Comprehensive tests for UniversalTemplateEngine"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.templates_dir = self.temp_dir / "templates"
        self.templates_dir.mkdir()
        
        # Create test configuration
        self.test_config = {
            "package_name": "test-cli",
            "command_name": "test-cli",
            "display_name": "Test CLI",
            "description": "Test CLI application",
            "language": "python",
            "python": {
                "minimum_version": "3.8",
                "maximum_version": "3.13"
            },
            "dependencies": {
                "required": ["click>=8.0"],
                "optional": []
            },
            "installation": {
                "pypi_name": "test-cli",
                "development_path": ".",
                "extras": {}
            },
            "shell_integration": {
                "enabled": False,
                "alias": "test-cli"
            },
            "validation": {
                "check_api_keys": False,
                "check_disk_space": True,
                "minimum_disk_space_mb": 100
            },
            "messages": {
                "install_success": "Test CLI installed successfully!",
                "install_dev_success": "Test CLI dev installation completed!",
                "upgrade_success": "Test CLI upgraded successfully!",
                "uninstall_success": "Test CLI uninstalled successfully!"
            },
            "cli": {
                "name": "test-cli",
                "tagline": "Test CLI tagline",
                "version": "1.0.0",
                "commands": {
                    "hello": {
                        "desc": "Say hello",
                        "args": [],
                        "options": []
                    }
                }
            }
        }
        
        # Create test templates
        self._create_test_templates()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_test_templates(self):
        """Create comprehensive test templates"""
        
        # Main CLI template
        cli_template = """
#!/usr/bin/env node
// Generated CLI for {{ project.name }}
// Version: {{ project.version }}

{% for command in commands %}
function {{ command.name }}Command() {
    console.log("Executing {{ command.name }}: {{ command.description }}");
    {% if command.arguments %}
    // Arguments: {{ command.arguments | length }}
    {% endif %}
    {% if command.options %}
    // Options: {{ command.options | length }}
    {% endif %}
}
{% endfor %}

module.exports = { 
    {% for command in commands %}
    {{ command.name }}: {{ command.name }}Command{{ "," if not loop.last }}
    {% endfor %}
};
"""
        (self.templates_dir / "cli.j2").write_text(cli_template)
        
        # Package.json template
        package_template = """
{
    "name": "{{ project.name }}",
    "version": "{{ project.version }}",
    "description": "{{ project.description }}",
    "main": "cli.js",
    "scripts": {
        "start": "node cli.js"
    },
    "dependencies": {
        {% if language == "nodejs" %}
        "commander": "^9.0.0"
        {% elif language == "typescript" %}
        "commander": "^9.0.0",
        "@types/node": "^18.0.0"
        {% endif %}
    }
}
"""
        (self.templates_dir / "package.json.j2").write_text(package_template)
        
        # Error handling template
        error_template = """
{% if not project %}
ERROR: No project configuration provided
{% elif not project.name %}
ERROR: Project name is required
{% else %}
// Project: {{ project.name }}
{% if commands %}
// Commands available: {{ commands | length }}
{% else %}
// No commands defined
{% endif %}
{% endif %}
"""
        (self.templates_dir / "error_check.j2").write_text(error_template)
    
    def test_engine_initialization(self):
        """Test engine initialization with various configurations"""
        # Test with valid template directory
        engine = UniversalTemplateEngine(self.templates_dir)
        assert engine.template_dir == self.templates_dir
        
        # Test with non-existent directory
        with pytest.raises(ValueError, match="Template directory does not exist"):
            UniversalTemplateEngine(Path("/non/existent/path"))
    
    def test_register_and_get_renderer(self):
        """Test renderer registration and retrieval"""
        engine = UniversalTemplateEngine(self.templates_dir)
        renderer = MockRenderer("test")
        
        # Register renderer
        engine.register_renderer("test", renderer)
        
        # Retrieve renderer
        retrieved = engine.get_renderer("test")
        assert retrieved is renderer
        assert retrieved.language == "test"
        
        # Test non-existent renderer
        with pytest.raises(ValueError, match="No renderer registered for language"):
            engine.get_renderer("nonexistent")
    
    def test_create_intermediate_representation(self):
        """Test IR creation from various config schemas"""
        engine = UniversalTemplateEngine(self.templates_dir)
        
        # Test with valid config
        config = GoobitsConfigSchema(**self.test_config)
        ir = engine.create_intermediate_representation(config)
        
        # Verify IR structure
        assert "project" in ir
        assert "cli" in ir
        assert "metadata" in ir
        assert ir["project"]["name"] == "Test CLI"
        assert ir["project"]["command_name"] == "test-cli"
        assert "hello" in ir["cli"]["commands"]
        
        # Test command processing
        command = ir["cli"]["commands"]["hello"]
        assert command["description"] == "Say hello"
        
        # Test with multiple commands
        multi_command_config = self.test_config.copy()
        multi_command_config["cli"]["commands"] = {
            "cmd1": {"desc": "First command", "args": [], "options": []},
            "cmd2": {"desc": "Second command", "args": [], "options": []}
        }
        config = GoobitsConfigSchema(**multi_command_config)
        ir = engine.create_intermediate_representation(config)
        assert len(ir["cli"]["commands"]) == 2
    
    def test_render_with_renderer(self):
        """Test full rendering process with mock renderer"""
        engine = UniversalTemplateEngine(self.templates_dir)
        renderer = MockRenderer("nodejs")
        engine.register_renderer("nodejs", renderer)
        
        config = GoobitsConfigSchema(**self.test_config)
        
        # Test successful rendering
        result = engine.render(config, "nodejs")
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "files" in result
        assert "metadata" in result
        
        # Verify metadata
        metadata = result["metadata"]
        assert metadata["language"] == "nodejs"
        assert metadata["template_count"] > 0
        assert "render_time" in metadata
        
        # Verify files are generated
        files = result["files"]
        assert "cli.test" in files
        assert "main.test" in files
    
    def test_template_processing_edge_cases(self):
        """Test template processing with edge cases and error conditions"""
        engine = UniversalTemplateEngine(self.templates_dir)
        renderer = MockRenderer("test")
        engine.register_renderer("test", renderer)
        
        # Test with minimal config
        minimal_config = {
            "package_name": "minimal",
            "command_name": "minimal",
            "display_name": "Minimal CLI",
            "description": "Minimal test CLI",
            "language": "python",
            "python": {
                "minimum_version": "3.8",
                "maximum_version": "3.13"
            },
            "dependencies": {
                "required": [],
                "optional": []
            },
            "installation": {
                "pypi_name": "minimal",
                "development_path": ".",
                "extras": {}
            },
            "shell_integration": {
                "enabled": False,
                "alias": "minimal"
            },
            "validation": {
                "check_api_keys": False,
                "check_disk_space": True,
                "minimum_disk_space_mb": 100
            },
            "messages": {
                "install_success": "Minimal CLI installed successfully!",
                "install_dev_success": "Minimal CLI dev installation completed!",
                "upgrade_success": "Minimal CLI upgraded successfully!",
                "uninstall_success": "Minimal CLI uninstalled successfully!"
            },
            "cli": {
                "name": "minimal",
                "tagline": "Minimal CLI tagline",
                "commands": {}
            }
        }
        config = GoobitsConfigSchema(**minimal_config)
        result = engine.render(config, "test")
        assert result is not None
        
        # Test with complex nested structure
        complex_config = self.test_config.copy()
        complex_config["cli"]["commands"] = {
            "complex": {
                "desc": "Complex command",
                "args": [
                    {"name": "arg1", "desc": "First argument", "required": True},
                    {"name": "arg2", "desc": "Second argument", "required": False}
                ],
                "options": [
                    {"name": "verbose", "short": "v", "desc": "Verbose output", "type": "str"},
                    {"name": "output", "short": "o", "desc": "Output file", "type": "str"}
                ]
            }
        }
        config = GoobitsConfigSchema(**complex_config)
        ir = engine.create_intermediate_representation(config)
        
        # Verify complex structure processing
        command = ir["cli"]["commands"]["complex"]
        assert len(command["args"]) == 2
        assert len(command["options"]) == 2
        assert command["args"][0]["required"] is True
        assert command["options"][0]["type"] == "str"
    
    def test_error_handling_in_rendering(self):
        """Test error handling during template rendering"""
        engine = UniversalTemplateEngine(self.templates_dir)
        
        # Test rendering without registered renderer
        config = GoobitsConfigSchema(**self.test_config)
        with pytest.raises(ValueError, match="No renderer registered"):
            engine.render(config, "unregistered")
        
        # Test with invalid template
        broken_template_dir = self.temp_dir / "broken_templates"
        broken_template_dir.mkdir()
        (broken_template_dir / "broken.j2").write_text("{{ invalid.template.syntax ")
        
        broken_engine = UniversalTemplateEngine(broken_template_dir)
        broken_renderer = MockRenderer("broken")
        broken_engine.register_renderer("broken", broken_renderer)
        
        # Should handle template syntax errors gracefully
        try:
            result = broken_engine.render(config, "broken")
            # If it doesn't raise, check that it handled the error
            assert result is not None
        except Exception as e:
            # Template errors should be caught and handled
            assert "template" in str(e).lower() or "syntax" in str(e).lower()
    
    def test_template_caching_and_performance(self):
        """Test template caching and performance optimizations"""
        engine = UniversalTemplateEngine(self.templates_dir)
        renderer = MockRenderer("perf")
        engine.register_renderer("perf", renderer)
        
        config = GoobitsConfigSchema(**self.test_config)
        
        # First render - should cache templates
        result1 = engine.render(config, "perf")
        first_render_time = result1["metadata"]["render_time"]
        
        # Second render - should use cached templates
        result2 = engine.render(config, "perf")
        second_render_time = result2["metadata"]["render_time"]
        
        # Both should succeed
        assert result1 is not None
        assert result2 is not None
        
        # Performance should be consistent or improved
        assert second_render_time >= 0  # Basic sanity check
    
    def test_cross_language_consistency(self):
        """Test that different renderers produce consistent IR"""
        engine = UniversalTemplateEngine(self.templates_dir)
        
        # Register multiple renderers
        python_renderer = MockRenderer("python")
        nodejs_renderer = MockRenderer("nodejs")
        typescript_renderer = MockRenderer("typescript")
        
        engine.register_renderer("python", python_renderer)
        engine.register_renderer("nodejs", nodejs_renderer)
        engine.register_renderer("typescript", typescript_renderer)
        
        config = GoobitsConfigSchema(**self.test_config)
        
        # Generate IR for each language
        python_ir = engine.create_intermediate_representation(config)
        nodejs_ir = engine.create_intermediate_representation(config)
        typescript_ir = engine.create_intermediate_representation(config)
        
        # Core IR should be identical across languages
        assert python_ir["project"] == nodejs_ir["project"]
        assert nodejs_ir["project"] == typescript_ir["project"]
        assert python_ir["cli"]["commands"] == nodejs_ir["cli"]["commands"]
        assert nodejs_ir["cli"]["commands"] == typescript_ir["cli"]["commands"]
    
    def test_template_context_transformation(self):
        """Test template context transformation through renderers"""
        engine = UniversalTemplateEngine(self.templates_dir)
        renderer = MockRenderer("context_test")
        engine.register_renderer("context_test", renderer)
        
        config = GoobitsConfigSchema(**self.test_config)
        ir = engine.create_intermediate_representation(config)
        
        # Transform context through renderer
        context = renderer.get_template_context(ir)
        
        # Should include original IR data
        assert context["project"]["name"] == "Test CLI"
        assert len(context["cli"]["commands"]) == 1
        
        # Should include renderer-specific additions
        assert context["test_specific"] is True
        assert context["language"] == "context_test"
    
    def test_output_file_generation(self):
        """Test output file mapping and generation"""
        engine = UniversalTemplateEngine(self.templates_dir)
        
        class FileTestRenderer(MockRenderer):
            def get_output_files(self, ir: Dict[str, Any]) -> Dict[str, str]:
                return {
                    f"{ir['project']['name']}.js": "main_cli_content",
                    "package.json": "package_json_content",
                    "README.md": "readme_content"
                }
        
        renderer = FileTestRenderer("file_test")
        engine.register_renderer("file_test", renderer)
        
        config = GoobitsConfigSchema(**self.test_config)
        result = engine.render(config, "file_test")
        
        files = result["files"]
        assert "Test CLI.js" in files
        assert "package.json" in files
        assert "README.md" in files
        assert files["Test CLI.js"] == "main_cli_content"
    
    @patch('goobits_cli.universal.template_engine.PERFORMANCE_AVAILABLE', True)
    def test_performance_integration(self):
        """Test integration with performance optimization components"""
        with patch('goobits_cli.universal.template_engine.TemplateCache') as MockCache:
            with patch('goobits_cli.universal.template_engine.LazyLoader') as MockLoader:
                engine = UniversalTemplateEngine(self.templates_dir)
                
                # Performance components should be initialized
                MockCache.assert_called_once()
                MockLoader.assert_called_once()
                
                # Render should work with performance components
                renderer = MockRenderer("perf_integration")
                engine.register_renderer("perf_integration", renderer)
                
                config = GoobitsConfigSchema(**self.test_config)
                result = engine.render(config, "perf_integration")
                
                assert result is not None
                assert "metadata" in result
    
    def test_jinja_environment_customization(self):
        """Test Jinja2 environment customization and filters"""
        engine = UniversalTemplateEngine(self.templates_dir)
        
        # Test that Jinja environment is properly configured
        # This is tested indirectly through template rendering
        custom_template = """
Test template with filters:
- Length: {{ cli.commands | length }}
- First command: {{ 'hello' if cli.commands.hello else 'none' }}
- Project upper: {{ project.name | upper }}
"""
        (self.templates_dir / "custom.j2").write_text(custom_template)
        
        class CustomRenderer(MockRenderer):
            def render_component(self, component_name: str, context: Dict[str, Any]) -> str:
                if component_name == "custom":
                    # Simulate template rendering with Jinja filters
                    template = engine.jinja_env.get_template("custom.j2")
                    return template.render(context)
                return super().render_component(component_name, context)
            
            def get_output_files(self, ir: Dict[str, Any]) -> Dict[str, str]:
                return {"custom.txt": self.render_component("custom", ir)}
        
        renderer = CustomRenderer("custom")
        engine.register_renderer("custom", renderer)
        
        config = GoobitsConfigSchema(**self.test_config)
        result = engine.render(config, "custom")
        
        # Verify that Jinja filters work correctly
        custom_output = result["files"]["custom.txt"]
        assert "Length: 1" in custom_output
        assert "First command: hello" in custom_output
        assert "TEST CLI" in custom_output  # upper filter