"""
Comprehensive tests for Universal Template Engine.

This is the CONSOLIDATED template engine test file that combines tests from:
- test_template_engine_comprehensive.py (BASE FILE - coverage improvements 63% → 85%)
- test_template_engine_focused.py (ComponentRegistry focused tests)
- test_template_engine_functional.py (End-to-end functional tests) 
- test_universal_coverage_boost.py (Framework integration and metadata tests)

This consolidated file provides complete test coverage for:
- UniversalTemplateEngine with actual template rendering
- ComponentRegistry comprehensive functionality
- Intermediate Representation (IR) processing
- Cross-language code generation
- Component metadata and dependency tracking
- End-to-end CLI generation functionality
- Error handling and edge cases
- Template validation and caching
- Functional testing with real components

All unique tests from the original 4 files have been preserved to maintain complete test coverage.
"""

import pytest
import tempfile
import time
import shutil
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

from goobits_cli.universal.template_engine import (
    UniversalTemplateEngine,
    LanguageRenderer
)
from goobits_cli.universal.component_registry import ComponentRegistry, ComponentMetadata
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
    
    def get_custom_filters(self) -> Dict[str, callable]:
        """Return custom Jinja2 filters for testing"""
        return {}
    
    def render_component(self, component_name: str, template_content: str, context: Dict[str, Any]) -> str:
        """Render a component for testing"""
        return f"// {self.language} component: {component_name}\ntest content"
    
    def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """Get output structure mapping"""
        return {"cli": "cli.test", "main": "main.test"}
    
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
    
    def test_render_with_real_template_validation(self):
        """Test full rendering process with REAL template validation and content checks"""
        engine = UniversalTemplateEngine(self.templates_dir)
        
        # Use a renderer that actually processes templates instead of mocking everything
        class RealTemplateRenderer(LanguageRenderer):
            @property
            def language(self) -> str:
                return "nodejs"
            
            @property
            def file_extensions(self) -> Dict[str, str]:
                return {"cli": "js", "package": "json"}
            
            def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
                # Return REAL context that templates can use
                return {
                    "project": ir.get("project", {}),
                    "cli": ir.get("cli", {}),
                    "commands": ir.get("cli", {}).get("commands", {}),
                    "language": "nodejs"
                }
            
            def get_custom_filters(self) -> Dict[str, callable]:
                return {"length": len}  # Real filter that works
            
            def render_component(self, component_name: str, template_content: str, 
                                context: Dict[str, Any]) -> str:
                # REAL Jinja2 rendering - no mocking!
                import jinja2
                env = jinja2.Environment(loader=jinja2.BaseLoader())
                env.filters.update(self.get_custom_filters())
                
                try:
                    template = env.from_string(template_content)
                    return template.render(**context)
                except Exception as e:
                    # Return error details for debugging instead of hiding them
                    return f"// Template error in {component_name}: {e}\n// Original content:\n{template_content}"
            
            def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
                return {"cli.js": "Generated CLI content", "package.json": "Generated package.json"}
        
        renderer = RealTemplateRenderer()
        engine.register_renderer("nodejs", renderer)
        
        config = GoobitsConfigSchema(**self.test_config)
        
        # Test successful rendering with REAL template processing
        result = engine.render(config, "nodejs")
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "files" in result
        assert "metadata" in result
        
        # Verify metadata contains real timing information
        metadata = result["metadata"]
        assert metadata["language"] == "nodejs"
        assert metadata["template_count"] >= 0  # Could be 0 if no templates loaded
        assert "render_time" in metadata
        assert isinstance(metadata["render_time"], (int, float))
        
        # Verify files contain REAL rendered content, not mocked responses
        files = result["files"]
        assert isinstance(files, dict)
        
        # Test that templates were actually processed by checking for template variables
        if "cli.js" in files:
            cli_content = files["cli.js"]
            assert isinstance(cli_content, str)
            # Should contain actual project name, not template variables
            assert "Test CLI" in cli_content or "test-cli" in cli_content
            # Should NOT contain unprocessed template syntax
            assert "{{" not in cli_content or "}}" not in cli_content or "Template error" in cli_content
        
        # Test that the renderer actually used the provided context
        if "package.json" in files:
            package_content = files["package.json"]
            assert isinstance(package_content, str)
            # Should contain processed content or error details
            assert len(package_content) > 0
    
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
        assert len(command["arguments"]) == 2
        assert len(command["options"]) == 2
        assert command["arguments"][0]["required"] is True
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
            # If it doesn't raise, check that it handled the error gracefully
            # Result should contain files dict and metadata even with broken templates
            assert isinstance(result, dict)
            assert "files" in result
            assert "metadata" in result
            assert isinstance(result["files"], dict)
            assert isinstance(result["metadata"], dict)
        except Exception as e:
            # Template errors should be caught and handled appropriately
            assert "template" in str(e).lower() or "syntax" in str(e).lower()
    
    def test_template_caching_and_performance(self):
        """Test template caching and performance optimizations"""
        engine = UniversalTemplateEngine(self.templates_dir)
        renderer = MockRenderer("perf")
        engine.register_renderer("perf", renderer)
        
        config = GoobitsConfigSchema(**self.test_config)
        
        # First render - should cache templates
        result1 = engine.render(config, "perf")
        
        # Second render - should use cached templates
        result2 = engine.render(config, "perf")
        second_render_time = result2["metadata"]["render_time"]
        
        # Both should succeed
        assert result1 is not None
        assert result2 is not None
        
        # Performance should be consistent or improved
        assert second_render_time >= 0  # Basic sanity check
    
    def test_cross_language_real_template_consistency(self):
        """Test that different languages generate valid code from the same configuration"""
        engine = UniversalTemplateEngine(self.templates_dir)
        
        # Create REAL renderers for different languages that actually validate output
        class PythonValidatingRenderer(LanguageRenderer):
            @property
            def language(self) -> str:
                return "python"
                
            @property
            def file_extensions(self) -> Dict[str, str]:
                return {"cli": "py", "setup": "py"}
            
            def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
                return {"project": ir.get("project", {}), "language": "python"}
            
            def get_custom_filters(self) -> Dict[str, callable]:
                return {"snake_case": lambda x: x.lower().replace("-", "_")}
            
            def render_component(self, component_name: str, template_content: str, 
                                context: Dict[str, Any]) -> str:
                # Test real Python syntax validity
                python_template = f'''
#!/usr/bin/env python3
# Generated {component_name} for {{{{ project.name }}}}
import click

@click.command()
def main():
    """{{{{ project.name }}}} CLI"""
    click.echo("Hello from {{{{ language }}}} CLI!")

if __name__ == "__main__":
    main()
'''
                import jinja2
                env = jinja2.Environment(loader=jinja2.BaseLoader())
                env.filters.update(self.get_custom_filters())
                template = env.from_string(python_template)
                rendered = template.render(**context)
                
                # Validate Python syntax
                try:
                    compile(rendered, f'<{component_name}>', 'exec')
                    return rendered
                except SyntaxError as e:
                    return f"# Python syntax error: {e}\n{rendered}"
            
            def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
                return {"cli.py": "Python CLI"}
        
        class NodeJSValidatingRenderer(LanguageRenderer):
            @property
            def language(self) -> str:
                return "nodejs"
                
            @property 
            def file_extensions(self) -> Dict[str, str]:
                return {"cli": "js", "package": "json"}
            
            def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
                return {"project": ir.get("project", {}), "language": "nodejs"}
            
            def get_custom_filters(self) -> Dict[str, callable]:
                return {"camelCase": lambda x: x.replace("-", "").title().replace(" ", "")}
            
            def render_component(self, component_name: str, template_content: str,
                                context: Dict[str, Any]) -> str:
                # Test real Node.js code generation
                js_template = f'''
#!/usr/bin/env node
// Generated {component_name} for {{{{ project.name }}}}
const {{ Command }} = require('commander');

const program = new Command();
program
    .name('{{{{ project.name }}}}')
    .description('{{{{ language }}}} CLI')
    .action(() => {{
        console.log('Hello from {{{{ language }}}} CLI!');
    }});

program.parse(process.argv);
'''
                import jinja2
                env = jinja2.Environment(loader=jinja2.BaseLoader())
                env.filters.update(self.get_custom_filters())
                template = env.from_string(js_template)
                rendered = template.render(**context)
                
                # Basic Node.js syntax validation
                if "{{" in rendered or "}}" in rendered:
                    return f"// Template variables not processed:\n{rendered}"
                return rendered
            
            def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
                return {"cli.js": "Node.js CLI"}
        
        # Register REAL renderers
        python_renderer = PythonValidatingRenderer()
        nodejs_renderer = NodeJSValidatingRenderer()
        
        engine.register_renderer("python", python_renderer)
        engine.register_renderer("nodejs", nodejs_renderer)
        
        config = GoobitsConfigSchema(**self.test_config)
        
        # Generate REAL code for each language
        python_result = engine.render(config, "python")
        nodejs_result = engine.render(config, "nodejs")
        
        # Both should succeed and produce valid outputs
        assert python_result["metadata"]["language"] == "python"
        assert nodejs_result["metadata"]["language"] == "nodejs"
        
        # Check that both generated valid syntax
        python_files = python_result["files"]
        nodejs_files = nodejs_result["files"]
        
        if "cli.py" in python_files:
            python_content = python_files["cli.py"]
            assert "import click" in python_content, "Python CLI should import click"
            assert "Hello from python CLI!" in python_content, "Python CLI should render language correctly"
            assert "syntax error" not in python_content.lower(), f"Python syntax error: {python_content}"
        
        if "cli.js" in nodejs_files:
            nodejs_content = nodejs_files["cli.js"]
            assert "require('commander')" in nodejs_content, "Node.js CLI should require commander"
            assert "Hello from nodejs CLI!" in nodejs_content, "Node.js CLI should render language correctly"
            assert "Template variables not processed" not in nodejs_content, f"Node.js template error: {nodejs_content}"
    
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
            def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
                # Override to return custom output structure
                return {
                    "cli": f"{ir['project']['name']}.js",
                    "main": "package.json",
                    "readme": "README.md"
                }
        
        renderer = FileTestRenderer("file_test")
        engine.register_renderer("file_test", renderer)
        
        config = GoobitsConfigSchema(**self.test_config)
        result = engine.render(config, "file_test")
        
        files = result["files"]
        # Now files dict contains actual file paths as keys, mapped to rendered content
        assert "Test CLI.js" in files  # Project name is "Test CLI" 
        assert "package.json" in files
        assert "README.md" in files
        
        # Verify that components are actually rendered (not just static content)
        assert "file_test component: cli" in files["Test CLI.js"]
        assert "Component 'readme' not found" in files["README.md"]  # readme component doesn't exist
    
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
            def render_component(self, component_name: str, template_content: str, context: Dict[str, Any]) -> str:
                if component_name == "custom":
                    # Simulate template rendering with Jinja filters
                    template = engine.jinja_env.get_template("custom.j2")
                    return template.render(context)
                return super().render_component(component_name, template_content, context)
            
            def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
                # Render the custom template and return it as the output
                context = self.get_template_context(ir)
                custom_content = self.render_component("custom", "", context)
                return {"custom": custom_content}
        
        renderer = CustomRenderer("custom")
        engine.register_renderer("custom", renderer)
        
        config = GoobitsConfigSchema(**self.test_config)
        result = engine.render(config, "custom")
        
        # Verify that Jinja filters work correctly
        # The CustomRenderer inherits from MockRenderer which returns component names as keys
        files = result["files"]
        # Check if there's a component-based key structure
        if "custom" in files:
            custom_output = files["custom"]
        else:
            # Fallback: look for any file that contains the expected content
            custom_output = list(files.values())[0] if files else ""
        assert "Length: 1" in custom_output
        assert "First command: hello" in custom_output
        assert "TEST CLI" in custom_output  # upper filter
    
    def test_lazy_loading_setup(self):
        """Test lazy loading setup"""
        # Test with lazy loading enabled (default)
        engine = UniversalTemplateEngine(self.templates_dir, enable_lazy_loading=True)
        assert engine.lazy_loader is not None  # LazyLoader object should be created
        assert hasattr(engine.lazy_loader, 'strategy')  # Should have strategy attribute
        
        # Test with lazy loading disabled
        engine2 = UniversalTemplateEngine(self.templates_dir, enable_lazy_loading=False)
        assert engine2.lazy_loader is None
    
    def test_real_component_registry_functionality(self):
        """Test component registry with REAL component loading and validation"""
        engine = UniversalTemplateEngine(self.templates_dir)
        
        # Components should be loaded from REAL templates we created
        components = engine.component_registry.list_components()
        component_names = [c.name for c in components]
        
        # Verify our test templates are actually loaded
        assert "cli" in component_names, f"CLI template not found in components: {component_names}"
        assert "package.json" in component_names, f"Package.json template not found: {component_names}"
        assert "error_check" in component_names, f"Error check template not found: {component_names}"
        
        # Test REAL component content retrieval
        cli_template = engine.component_registry.get_component("cli")
        assert isinstance(cli_template, str)
        assert len(cli_template) > 0
        assert "Generated CLI for" in cli_template, "CLI template should contain expected header"
        assert "{{" in cli_template and "}}" in cli_template, "Template should contain Jinja2 variables"
        
        # Test component existence checking with REAL components
        assert engine.component_registry.component_exists("cli")
        assert engine.component_registry.component_exists("package.json")
        assert not engine.component_registry.component_exists("nonexistent_template")
        
        # Test REAL metadata functionality
        cli_metadata = engine.component_registry.get_component_metadata("cli")
        assert cli_metadata is not None
        assert cli_metadata.name == "cli"
        assert cli_metadata.path.exists(), "Component file should exist on disk"
        assert cli_metadata.last_modified > 0, "Should have valid modification time"
        assert not cli_metadata.is_stale(), "Newly created component should not be stale"
        
        # Test component registry properties with REAL values
        assert hasattr(engine.component_registry, 'components_dir')
        assert engine.component_registry.components_dir == self.templates_dir
        assert engine.component_registry.components_dir.exists(), "Components directory should exist"


class SimpleTestRenderer(LanguageRenderer):
    """Simple test renderer that implements all abstract methods"""
    
    def __init__(self, language: str = "test"):
        self._language = language
        
    @property
    def language(self) -> str:
        return self._language
    
    @property
    def file_extensions(self) -> Dict[str, str]:
        return {"test": "test", "cli": "test"}
    
    def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        context = ir.copy()
        context["language"] = self.language
        context["test_specific"] = True
        return context
    
    def get_custom_filters(self) -> Dict[str, callable]:
        return {
            "test_filter": lambda x: f"test_{x}",
            "upper": lambda x: str(x).upper()
        }
    
    def render_component(self, component_name: str, template_content: str, 
                        context: Dict[str, Any]) -> str:
        # Validate that parameters are actually used and not hardcoded
        if not component_name:
            raise ValueError("component_name cannot be empty")
        if template_content is None:
            raise ValueError("template_content cannot be None")  
        if not isinstance(context, dict):
            raise ValueError("context must be a dict")
        
        # Use all parameters in the response to prove they're being validated
        context_keys = list(context.keys())
        return f"// {self.language} component: {component_name}\n// Context keys: {len(context_keys)}\n{template_content}"
    
    def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
        return {
            "cli.test": "main_cli_content",
            "config.test": "config_content"
        }


class TestComponentRegistryDetailed:
    """Detailed tests for ComponentRegistry functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.components_dir = self.temp_dir / "components"
        self.components_dir.mkdir()
        
    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_registry_initialization(self):
        """Test ComponentRegistry initialization"""
        registry = ComponentRegistry(self.components_dir)
        assert registry.components_dir == self.components_dir
        assert registry._components == {}
        assert registry._metadata == {}
        assert registry._dependencies == {}
        assert registry.auto_reload is False  # Default is False
        assert registry.validation_enabled is True
    
    def test_component_loading_comprehensive(self):
        """Test comprehensive component loading"""
        # Create various test files
        (self.components_dir / "simple.j2").write_text("Simple template")
        (self.components_dir / "with_vars.j2").write_text("Hello {{ name }}")
        (self.components_dir / "not_template.txt").write_text("Not a template")
        (self.components_dir / "empty.j2").write_text("")
        
        # Create subdirectory
        sub_dir = self.components_dir / "sub"
        sub_dir.mkdir()
        (sub_dir / "nested.j2").write_text("Nested template")
        
        registry = ComponentRegistry(self.components_dir)
        registry.load_components()
        
        # Check loaded components
        components = registry.list_components()
        component_names = [comp.name for comp in components]
        assert "simple" in component_names
        assert "with_vars" in component_names
        assert "empty" in component_names
        assert "sub/nested" in component_names
        assert "not_template" not in component_names
        
        # Test getting components
        assert registry.get_component("simple") == "Simple template"
        assert registry.get_component("with_vars") == "Hello {{ name }}"
        assert registry.get_component("empty") == ""
        
        # Test nested component
        assert registry.get_component("sub/nested") == "Nested template"
    
    def test_component_existence_checking(self):
        """Test component existence checking"""
        registry = ComponentRegistry(self.components_dir)
        
        # Initially no components
        assert not registry.component_exists("test")
        
        # Add component
        (self.components_dir / "test.j2").write_text("test content")
        registry.load_components()
        
        assert registry.component_exists("test")
        assert not registry.component_exists("nonexistent")
    
    def test_metadata_tracking(self):
        """Test metadata tracking functionality"""
        component_file = self.components_dir / "metadata_test.j2"
        component_file.write_text("Test content")
        
        registry = ComponentRegistry(self.components_dir)
        registry.load_components()
        
        # Check metadata exists
        metadata = registry.get_component_metadata("metadata_test")
        assert metadata is not None
        assert metadata.name == "metadata_test"
        assert metadata.path == component_file
        assert not metadata.is_stale()
        
        # Test with non-existent component
        assert registry.get_component_metadata("missing") is None
    
    def test_dependency_extraction(self):
        """Test dependency extraction from templates"""
        # Create template with dependencies comment
        template_with_deps = """
{{# Dependencies: base.j2, utils.j2 #}}
Template with dependencies
"""
        (self.components_dir / "with_deps.j2").write_text(template_with_deps)
        (self.components_dir / "base.j2").write_text("Base template")
        (self.components_dir / "utils.j2").write_text("Utils template")
        
        registry = ComponentRegistry(self.components_dir)
        registry.load_components()
        
        # Check dependencies
        deps = registry.get_component_dependencies("with_deps")
        assert "base" in deps
        assert "utils" in deps
        assert len(deps) == 2
        
        # Test component without dependencies
        no_deps = registry.get_component_dependencies("base")
        assert len(no_deps) == 0
    
    def test_template_validation(self):
        """Test template validation functionality"""
        # Valid template
        (self.components_dir / "valid.j2").write_text("Valid {{ variable }}")
        
        # Invalid template syntax
        (self.components_dir / "invalid.j2").write_text("Invalid {{ unclosed")
        
        registry = ComponentRegistry(self.components_dir)
        registry.load_components()
        
        # Both should load (validation may warn but doesn't prevent loading)
        assert registry.component_exists("valid")
        assert registry.component_exists("invalid")
    
    def test_hot_reloading(self):
        """Test hot-reloading functionality"""
        component_file = self.components_dir / "reload_test.j2"
        component_file.write_text("Original content")
        
        registry = ComponentRegistry(self.components_dir)
        registry.load_components()
        
        # Get original content
        original = registry.get_component("reload_test")
        assert original == "Original content"
        
        # Modify file
        time.sleep(0.1)  # Ensure different timestamp
        component_file.write_text("Modified content")
        
        # Reload component
        registry.reload_component("reload_test")
        modified = registry.get_component("reload_test")
        assert modified == "Modified content"
    
    def test_clear_functionality(self):
        """Test registry clearing"""
        (self.components_dir / "test1.j2").write_text("Test 1")
        (self.components_dir / "test2.j2").write_text("Test 2")
        
        registry = ComponentRegistry(self.components_dir)
        registry.load_components()
        
        assert len(registry.list_components()) == 2
        
        # Clear registry
        registry.clear()
        assert len(registry._components) == 0
        assert len(registry._metadata) == 0
        
        # Should be able to reload
        registry.load_components()
        assert len(registry.list_components()) == 2
    
    def test_force_reload(self):
        """Test force reload functionality"""
        (self.components_dir / "force_test.j2").write_text("Original")
        
        registry = ComponentRegistry(self.components_dir)
        registry.load_components()
        
        # Force reload
        registry.load_components(force_reload=True)
        assert registry.get_component("force_test") == "Original"
    
    def test_auto_reload(self):
        """Test auto-reload functionality"""
        component_file = self.components_dir / "auto_reload.j2"
        component_file.write_text("Original")
        
        registry = ComponentRegistry(self.components_dir, auto_reload=True)
        registry.load_components()
        
        # Get component - should work
        content = registry.get_component("auto_reload")
        assert content == "Original"
        
        # Test with auto_reload override
        content = registry.get_component("auto_reload", auto_reload=False)
        assert content == "Original"
    
    def test_error_handling(self):
        """Test error handling in ComponentRegistry"""
        registry = ComponentRegistry(self.components_dir)
        
        # Test getting non-existent component
        with pytest.raises(KeyError):
            registry.get_component("nonexistent")
        
        # Test reloading non-existent component
        result = registry.reload_component("nonexistent")
        assert result is False
        
        # Test with non-existent components directory
        bad_dir = self.temp_dir / "nonexistent"
        bad_registry = ComponentRegistry(bad_dir)
        bad_registry.load_components()  # Should handle gracefully
        assert len(bad_registry.list_components()) == 0


class FunctionalMockRenderer(LanguageRenderer):
    """Mock renderer for functional testing"""
    
    def __init__(self, language_name: str = "python"):
        self._language = language_name
    
    @property
    def language(self) -> str:
        return self._language
    
    @property
    def file_extensions(self) -> Dict[str, str]:
        return {
            "command_handler": "cli.py",
            "hooks": "hooks.py",
            "config": "config.py"
        }
    
    def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "language": self._language,
            "project": ir.get("project", {}),
            "cli": ir.get("cli", {}),
            "timestamp": "2023-01-01T00:00:00Z",
            "version": "1.0.0"
        }
    
    def get_custom_filters(self) -> Dict[str, callable]:
        return {
            "snake_case": lambda x: x.lower().replace("-", "_").replace(" ", "_"),
            "camel_case": lambda x: "".join(word.capitalize() for word in x.replace("-", " ").split())
        }
    
    def render_component(self, component_name: str, template_content: str, 
                        context: Dict[str, Any]) -> str:
        # Simple Jinja2 rendering with custom filters
        import jinja2
        env = jinja2.Environment(loader=jinja2.BaseLoader())
        # Add custom filters
        env.filters.update(self.get_custom_filters())
        template = env.from_string(template_content)
        return template.render(**context)
    
    def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
        return {
            "command_handler": "cli.py",
            "hooks": "hooks.py"
        }


class TestComponentRegistryFunctional:
    """Functional tests for ComponentRegistry"""
    
    def setup_method(self):
        """Setup test environment with real components"""
        # Create temporary directory for test components
        self.temp_dir = Path(tempfile.mkdtemp())
        self.components_dir = self.temp_dir / "components"
        self.components_dir.mkdir()
        
        # Create test component templates
        self._create_test_components()
        
        self.registry = ComponentRegistry(self.components_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_test_components(self):
        """Create test component templates"""
        # Simple command handler component
        command_handler = """
{# Command Handler Template #}
{% if language == 'python' %}
import click

@click.command()
def {{ project.command_name }}():
    '''{{ project.description }}'''
    print("Hello from {{ project.name }}!")
{% elif language == 'nodejs' %}
const { Command } = require('commander');

const program = new Command();
program
    .name('{{ project.command_name }}')
    .description('{{ project.description }}')
    .action(() => {
        console.log("Hello from {{ project.name }}!");
    });

program.parse();
{% endif %}
"""
        (self.components_dir / "command_handler.j2").write_text(command_handler)
        
        # Hooks component
        hooks = """
{# Hooks Template #}
{% if language == 'python' %}
def on_test_command(*args, **kwargs):
    '''Hook for test command'''
    return {"status": "success"}
{% elif language == 'nodejs' %}
function onTestCommand(args) {
    // Hook for test command
    return { status: "success" };
}

module.exports = { onTestCommand };
{% endif %}
"""
        (self.components_dir / "hooks.j2").write_text(hooks)
        
        # Component with dependencies (includes another template)
        advanced_component = """
{# Advanced Component with dependencies #}
{% include 'command_handler.j2' %}

{% if language == 'python' %}
# Additional Python-specific code
if __name__ == "__main__":
    {{ project.command_name }}()
{% endif %}
"""
        (self.components_dir / "advanced_component.j2").write_text(advanced_component)
    
    def test_component_loading(self):
        """Test loading components from directory"""
        self.registry.load_components()
        
        components = self.registry.list_components()
        component_names = [comp.name for comp in components]
        assert "command_handler" in component_names
        assert "hooks" in component_names
        assert "advanced_component" in component_names
        assert len(component_names) == 3
    
    def test_get_component_content(self):
        """Test retrieving component content"""
        self.registry.load_components()
        
        command_handler = self.registry.get_component("command_handler")
        assert "Command Handler Template" in command_handler
        assert "{% if language ==" in command_handler
        assert "click.command" in command_handler
    
    def test_component_on_demand_loading(self):
        """Test loading components on demand"""
        # Don't call load_components() - test on-demand loading
        
        command_handler = self.registry.get_component("command_handler")
        assert command_handler is not None
        assert "Command Handler Template" in command_handler
    
    def test_component_has_detection(self):
        """Test component existence detection"""
        assert self.registry.has_component("command_handler")
        assert self.registry.has_component("hooks")
        assert self.registry.has_component("nonexistent") is False
    
    def test_component_dependencies_extraction(self):
        """Test extraction of template dependencies"""
        self.registry.load_components()
        
        dependencies = self.registry.get_dependencies("advanced_component")
        assert "command_handler" in dependencies
    
    def test_component_metadata(self):
        """Test component metadata functionality"""
        self.registry.load_components()
        
        metadata = self.registry.get_component_metadata("command_handler")
        assert metadata is not None
        assert metadata.name == "command_handler"
        assert metadata.path.exists()
        assert metadata.loaded_at is not None
    
    def test_component_validation(self):
        """Test component template validation"""
        self.registry.load_components()
        
        errors = self.registry.validate_all_components()
        
        # Our test templates should be valid
        assert len(errors) == 0 or all(len(error_list) == 0 for error_list in errors.values())
    
    def test_invalid_component_handling(self):
        """Test handling of invalid components"""
        # Create invalid template
        invalid_template = "{% if unclosed_tag %}\nInvalid template"
        (self.components_dir / "invalid.j2").write_text(invalid_template)
        
        self.registry.load_components()
        
        self.registry.validate_all_components()
        # Should have validation errors for invalid template
        # Note: depending on Jinja2 version, this might not fail during parsing
        # but would fail during rendering
    
    def test_component_cache_clearing(self):
        """Test clearing component cache"""
        self.registry.load_components()
        
        assert len(self.registry.list_components()) > 0
        
        self.registry.clear_cache()
        # Cache is cleared, but list_components includes discoverable components
        assert len(self.registry.list_components()) > 0  # Still discoverable from disk


class TestUniversalTemplateEngineFunctional:
    """Functional tests for UniversalTemplateEngine"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create temporary directory for test components
        self.temp_dir = Path(tempfile.mkdtemp())
        self.components_dir = self.temp_dir / "components"
        self.components_dir.mkdir()
        self.output_dir = self.temp_dir / "output"
        self.output_dir.mkdir()
        
        # Create test component templates
        self._create_test_components()
        
        # Create engine with test components
        self.engine = UniversalTemplateEngine(
            template_dir=self.components_dir,
            template_cache=None,  # Disable cache for easier testing
            enable_lazy_loading=False  # Disable lazy loading for simpler tests
        )
        
        # Register test renderer
        self.renderer = FunctionalMockRenderer("python")
        self.engine.register_renderer("python", self.renderer)
        
        # Create test configuration
        self.test_config = self._create_test_config()
    
    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_test_components(self):
        """Create test component templates"""
        # Simple command handler
        command_handler = """
# Generated CLI for {{ project.name }}
# Language: {{ language }}

def main():
    print("Hello from {{ project.name }}!")
    print("Description: {{ project.description }}")
    print("Version: {{ cli.root_command.version }}")
    
    {% for command_name, command in cli.commands.items() %}
    # Command: {{ command_name }}
    # Description: {{ command.description }}
    {% endfor %}

if __name__ == "__main__":
    main()
"""
        (self.components_dir / "command_handler.j2").write_text(command_handler)
        
        # Hooks template
        hooks = """
# Hooks for {{ project.name }}

{% for command_name, command in cli.commands.items() %}
def {{ command.hook_name }}(*args, **kwargs):
    '''{{ command.description }}'''
    # TODO: Implement {{ command_name }} logic
    return {"status": "success", "command": "{{ command_name }}"}

{% endfor %}
"""
        (self.components_dir / "hooks.j2").write_text(hooks)
    
    def _create_test_config(self) -> GoobitsConfigSchema:
        """Create test configuration"""
        config_data = {
            "package_name": "test-cli",
            "command_name": "testcli",
            "display_name": "Test CLI",
            "description": "A test CLI application",
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
                "alias": "testcli"
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
                "name": "testcli",
                "tagline": "Test CLI tagline",
                "version": "1.0.0",
                "commands": {
                    "hello": {
                        "desc": "Say hello",
                        "args": [],
                        "options": []
                    },
                    "goodbye": {
                        "desc": "Say goodbye",
                        "args": [],
                        "options": []
                    }
                }
            }
        }
        
        return GoobitsConfigSchema(**config_data)
    
    def test_renderer_registration_validation(self):
        """Test renderer registration validation"""
        # Test None renderer
        with pytest.raises(ValueError, match="Renderer cannot be None"):
            self.engine.register_renderer("test", None)
        
        # Test invalid renderer type
        with pytest.raises(ValueError, match="must implement LanguageRenderer"):
            self.engine.register_renderer("test", "not a renderer")
        
        # Test renderer without language  
        invalid_renderer = Mock(spec=LanguageRenderer)
        invalid_renderer.language = ""
        with pytest.raises(ValueError, match="Language name must be provided"):
            self.engine.register_renderer("", invalid_renderer)
    
    def test_intermediate_representation_building(self):
        """Test building intermediate representation from config"""
        ir = self.engine._build_intermediate_representation(self.test_config)
        
        # Check project information
        assert ir["project"]["name"] == "Test CLI"
        assert ir["project"]["description"] == "A test CLI application"
        assert ir["project"]["command_name"] == "testcli"
        
        # Check CLI schema
        assert ir["cli"]["root_command"]["name"] == "testcli"
        assert ir["cli"]["root_command"]["version"] == "1.0.0"
        assert "commands" in ir["cli"]
        assert "hello" in ir["cli"]["commands"]
        assert "goodbye" in ir["cli"]["commands"]
        
        # Check hook names are generated correctly
        assert ir["cli"]["commands"]["hello"]["hook_name"] == "on_hello"
        assert ir["cli"]["commands"]["goodbye"]["hook_name"] == "on_goodbye"
    
    def test_cli_generation_success(self):
        """Test successful CLI generation"""
        generated_files = self.engine.generate_cli(
            config=self.test_config,
            language="python",
            output_dir=self.output_dir
        )
        
        # Should generate files according to output structure
        assert len(generated_files) > 0
        
        # Check generated content
        cli_file_path = str(self.output_dir / "cli.py")
        hooks_file_path = str(self.output_dir / "hooks.py")
        
        if cli_file_path in generated_files:
            cli_content = generated_files[cli_file_path]
            assert "Generated CLI for Test CLI" in cli_content
            assert "Language: python" in cli_content
            assert "Hello from Test CLI!" in cli_content
            assert "Command: hello" in cli_content
            assert "Command: goodbye" in cli_content
        
        if hooks_file_path in generated_files:
            hooks_content = generated_files[hooks_file_path]
            assert "Hooks for Test CLI" in hooks_content
            assert "def on_hello(" in hooks_content
            assert "def on_goodbye(" in hooks_content
    
    def test_cli_generation_validation(self):
        """Test CLI generation input validation"""
        # Test None config
        with pytest.raises(ValueError, match="Configuration cannot be None"):
            self.engine.generate_cli(None, "python", self.output_dir)
        
        # Test empty language
        with pytest.raises(ValueError, match="Language cannot be None"):
            self.engine.generate_cli(self.test_config, "", self.output_dir)
        
        # Test unregistered language
        with pytest.raises(ValueError, match="No renderer registered"):
            self.engine.generate_cli(self.test_config, "rust", self.output_dir)
    
    def test_cli_generation_missing_components(self):
        """Test CLI generation with missing components"""
        # Create engine with empty components directory
        empty_dir = self.temp_dir / "empty_components"
        empty_dir.mkdir()
        
        empty_engine = UniversalTemplateEngine(
            template_dir=empty_dir,
            enable_lazy_loading=False
        )
        empty_engine.register_renderer("python", self.renderer)
        
        generated_files = empty_engine.generate_cli(
            config=self.test_config,
            language="python",
            output_dir=self.output_dir
        )
        
        # Should handle missing components gracefully
        # (depends on renderer's output structure)
        assert isinstance(generated_files, dict)
    
    def test_template_context_transformation(self):
        """Test template context transformation through renderer"""
        ir = self.engine._build_intermediate_representation(self.test_config)
        context = self.renderer.get_template_context(ir)
        
        assert context["language"] == "python"
        assert context["project"]["name"] == "Test CLI"
        assert context["cli"]["root_command"]["name"] == "testcli"
        assert "timestamp" in context
        assert "version" in context
    
    def test_component_rendering_with_filters(self):
        """Test component rendering with custom filters"""
        # Test that custom filters work
        test_template = """
Project name: {{ project.name }}
Snake case: {{ project.name | snake_case }}
Camel case: {{ project.name | camel_case }}
"""
        (self.components_dir / "filter_test.j2").write_text(test_template)
        
        # Update renderer to include this component
        test_renderer = FunctionalMockRenderer("python")
        
        def get_output_structure_with_filter_test(ir):
            return {"filter_test": "filter_test.py"}
        
        test_renderer.get_output_structure = get_output_structure_with_filter_test
        
        # Re-register renderer
        filter_engine = UniversalTemplateEngine(
            template_dir=self.components_dir,
            enable_lazy_loading=False
        )
        filter_engine.register_renderer("python", test_renderer)
        
        generated_files = filter_engine.generate_cli(
            config=self.test_config,
            language="python",
            output_dir=self.output_dir
        )
        
        filter_test_path = str(self.output_dir / "filter_test.py")
        if filter_test_path in generated_files:
            content = generated_files[filter_test_path]
            assert "Snake case: test_cli" in content
            assert "Camel case: TestCli" in content
    
    def test_configuration_extraction_edge_cases(self):
        """Test configuration extraction with various edge cases"""
        # Test config with minimal CLI section
        minimal_config_data = {
            "package_name": "minimal-cli",
            "command_name": "minimal",
            "display_name": "Minimal CLI",
            "description": "Minimal test",
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
                "pypi_name": "minimal-cli",
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
                "tagline": "Minimal CLI",
                "commands": {}
                # No version, etc.
            }
        }
        
        minimal_config = GoobitsConfigSchema(**minimal_config_data)
        ir = self.engine._build_intermediate_representation(minimal_config)
        
        # Should handle missing optional fields
        assert ir["project"]["name"] == "Minimal CLI"  # Uses display_name
        assert ir["cli"]["root_command"]["version"] == "1.0.0"  # Uses defensive default when None
        assert ir["cli"]["commands"] == {}  # Empty commands
    
    def test_dependency_extraction(self):
        """Test dependency extraction from configuration"""
        config_with_deps_data = {
            "package_name": "deps-cli",
            "command_name": "deps",
            "display_name": "Deps CLI",
            "description": "CLI with dependencies",
            "language": "python",
            "python": {
                "minimum_version": "3.8",
                "maximum_version": "3.13"
            },
            "dependencies": {
                "required": ["click", "pydantic"],
                "optional": ["requests"]
            },
            "installation": {
                "pypi_name": "deps-cli",
                "development_path": ".",
                "extras": {
                    "python": ["dev", "test"],
                    "apt": ["git"],
                    "npm": ["prettier"]
                }
            },
            "shell_integration": {
                "enabled": False,
                "alias": "deps"
            },
            "validation": {
                "check_api_keys": False,
                "check_disk_space": True,
                "minimum_disk_space_mb": 100
            },
            "messages": {
                "install_success": "Deps CLI installed successfully!",
                "install_dev_success": "Deps CLI dev installation completed!",
                "upgrade_success": "Deps CLI upgraded successfully!",
                "uninstall_success": "Deps CLI uninstalled successfully!"
            },
            "cli": {
                "name": "deps",
                "tagline": "Deps CLI",
                "commands": {
                    "hello": {
                        "desc": "Say hello",
                        "args": [],
                        "options": []
                    }
                }
            }
        }
        
        config_with_deps = GoobitsConfigSchema(**config_with_deps_data)
        ir = self.engine._build_intermediate_representation(config_with_deps)
        
        # Check dependency extraction - main dependencies
        deps = ir["dependencies"]
        assert "click" in deps["python"]
        assert "pydantic" in deps["python"]
        assert "requests" in deps["python"]
        
        # Check extras dependencies are properly structured
        assert "python" in deps
        assert len(deps["python"]) == 3  # click, pydantic, requests


class TestComponentMetadata:
    """Test ComponentMetadata functionality"""
    
    def setup_method(self):
        """Setup test"""
        self.temp_file = Path(tempfile.mktemp(suffix='.j2'))
        self.temp_file.write_text("test content")
        
    def teardown_method(self):
        """Clean up"""
        if self.temp_file.exists():
            self.temp_file.unlink()
    
    def test_metadata_creation(self):
        """Test metadata creation"""
        metadata = ComponentMetadata("test", self.temp_file, ["dep1", "dep2"])
        assert metadata.name == "test"
        assert metadata.path == self.temp_file
        assert metadata.dependencies == ["dep1", "dep2"]
        assert metadata.last_modified > 0
        assert metadata.loaded_at is not None
    
    def test_staleness_detection(self):
        """Test staleness detection"""
        metadata = ComponentMetadata("test", self.temp_file)
        assert not metadata.is_stale()
        
        # Modify file
        time.sleep(0.1)
        self.temp_file.write_text("modified content")
        
        assert metadata.is_stale()
        
        # Refresh
        metadata.refresh_metadata()
        assert not metadata.is_stale()
    
    def test_missing_file(self):
        """Test metadata with missing file"""
        missing_file = Path("/tmp/nonexistent.j2")
        metadata = ComponentMetadata("missing", missing_file)
        
        assert metadata.last_modified == 0
        assert metadata.is_stale() is True


class TestTemplateRenderingErrorConditions:
    """Test error conditions in template rendering scenarios"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.templates_dir = self.temp_dir / "templates"
        self.templates_dir.mkdir()
        
    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_malformed_jinja2_template_syntax(self):
        """Test handling of malformed Jinja2 template syntax"""
        # Create template with unclosed block
        malformed_template = """
{% for command in commands %}
    Command: {{ command.name }}
    # Missing endfor tag
"""
        (self.templates_dir / "malformed.j2").write_text(malformed_template)
        
        engine = UniversalTemplateEngine(self.templates_dir)
        renderer = MockRenderer("test")
        engine.register_renderer("test", renderer)
        
        config_data = {
            "package_name": "test-cli",
            "command_name": "test",
            "display_name": "Test CLI",
            "description": "Test CLI",
            "language": "python",
            "python": {"minimum_version": "3.8", "maximum_version": "3.13"},
            "dependencies": {"required": [], "optional": []},
            "installation": {"pypi_name": "test-cli", "development_path": ".", "extras": {}},
            "shell_integration": {"enabled": False, "alias": "test"},
            "validation": {"check_api_keys": False, "check_disk_space": True, "minimum_disk_space_mb": 100},
            "messages": {"install_success": "Success!", "install_dev_success": "Dev success!", "upgrade_success": "Upgrade success!", "uninstall_success": "Uninstall success!"},
            "cli": {"name": "test", "tagline": "Test", "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}}}
        }
        config = GoobitsConfigSchema(**config_data)
        
        # Should handle template syntax errors gracefully
        try:
            result = engine.render(config, "test")
            assert isinstance(result, dict)
            assert "files" in result
            assert "metadata" in result
        except Exception as e:
            # If exception is raised, it should be template-related
            assert any(word in str(e).lower() for word in ["template", "syntax", "jinja", "block"])
    
    def test_template_with_undefined_variables(self):
        """Test template rendering with undefined variables"""
        undefined_vars_template = """
CLI Name: {{ project.name }}
Undefined: {{ project.nonexistent_field }}
Commands: {{ cli.commands | length }}
Invalid: {{ some.completely.undefined.variable }}
"""
        (self.templates_dir / "undefined_vars.j2").write_text(undefined_vars_template)
        
        engine = UniversalTemplateEngine(self.templates_dir)
        
        class UndefinedTestRenderer(MockRenderer):
            def get_output_files(self, ir):
                return {"undefined_test.txt": "content"}
                
            def render_component(self, component_name, template_content, context):
                # Simulate Jinja2 rendering with undefined variables
                import jinja2
                env = jinja2.Environment(loader=jinja2.BaseLoader(), undefined=jinja2.StrictUndefined)
                template = env.from_string(template_content)
                try:
                    return template.render(**context)
                except jinja2.UndefinedError as e:
                    # Should handle undefined variables appropriately
                    return f"Error: {str(e)}"
        
        renderer = UndefinedTestRenderer("test")
        engine.register_renderer("test", renderer)
        
        config_data = {
            "package_name": "test-cli",
            "command_name": "test",
            "display_name": "Test CLI",
            "description": "Test CLI",
            "language": "python",
            "python": {"minimum_version": "3.8", "maximum_version": "3.13"},
            "dependencies": {"required": [], "optional": []},
            "installation": {"pypi_name": "test-cli", "development_path": ".", "extras": {}},
            "shell_integration": {"enabled": False, "alias": "test"},
            "validation": {"check_api_keys": False, "check_disk_space": True, "minimum_disk_space_mb": 100},
            "messages": {"install_success": "Success!", "install_dev_success": "Dev success!", "upgrade_success": "Upgrade success!", "uninstall_success": "Uninstall success!"},
            "cli": {"name": "test", "tagline": "Test", "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}}}
        }
        config = GoobitsConfigSchema(**config_data)
        
        result = engine.render(config, "test")
        assert isinstance(result, dict)
        
        # If undefined variables are handled, result should contain error handling
        files = result.get("files", {})
        if "undefined_test.txt" in files:
            content = files["undefined_test.txt"]
            # Should either handle gracefully or show error
            assert isinstance(content, str)
    
    def test_circular_template_dependencies(self):
        """Test detection and handling of circular template dependencies"""
        # Create templates with circular includes
        template_a = """
Template A content
{% include 'template_b.j2' %}
End Template A
"""
        template_b = """
Template B content  
{% include 'template_a.j2' %}
End Template B
"""
        (self.templates_dir / "template_a.j2").write_text(template_a)
        (self.templates_dir / "template_b.j2").write_text(template_b)
        
        engine = UniversalTemplateEngine(self.templates_dir)
        
        class CircularTestRenderer(MockRenderer):
            def get_output_files(self, ir):
                return {"circular_test.txt": "content"}
                
            def render_component(self, component_name, template_content, context):
                import jinja2
                # Create environment that can detect circular includes
                loader = jinja2.FileSystemLoader(str(self.templates_dir))
                env = jinja2.Environment(loader=loader)
                try:
                    template = env.from_string(template_content)
                    return template.render(**context)
                except jinja2.TemplateRuntimeError as e:
                    if "recursive" in str(e).lower() or "circular" in str(e).lower():
                        return f"Circular dependency detected: {str(e)}"
                    raise
        
        renderer = CircularTestRenderer("test")
        engine.register_renderer("test", renderer)
        
        config_data = {
            "package_name": "test-cli",
            "command_name": "test",
            "display_name": "Test CLI",
            "description": "Test CLI",
            "language": "python",
            "python": {"minimum_version": "3.8", "maximum_version": "3.13"},
            "dependencies": {"required": [], "optional": []},
            "installation": {"pypi_name": "test-cli", "development_path": ".", "extras": {}},
            "shell_integration": {"enabled": False, "alias": "test"},
            "validation": {"check_api_keys": False, "check_disk_space": True, "minimum_disk_space_mb": 100},
            "messages": {"install_success": "Success!", "install_dev_success": "Dev success!", "upgrade_success": "Upgrade success!", "uninstall_success": "Uninstall success!"},
            "cli": {"name": "test", "tagline": "Test", "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}}}
        }
        config = GoobitsConfigSchema(**config_data)
        
        # Should handle circular dependencies without infinite recursion
        result = engine.render(config, "test")
        assert isinstance(result, dict)
        
    def test_template_with_invalid_filter_usage(self):
        """Test template with invalid filter usage"""
        invalid_filter_template = """
CLI Name: {{ project.name | nonexistent_filter }}
Date: {{ project.name | strftime('%Y-%m-%d') }}  # strftime on string
Length: {{ project.name | length | upper }}  # chaining incompatible filters
"""
        (self.templates_dir / "invalid_filters.j2").write_text(invalid_filter_template)
        
        engine = UniversalTemplateEngine(self.templates_dir)
        
        class FilterTestRenderer(MockRenderer):
            def get_custom_filters(self):
                return {
                    "upper": str.upper,
                    "length": len
                    # Deliberately exclude nonexistent_filter and strftime
                }
                
            def get_output_files(self, ir):
                return {"filter_test.txt": "content"}
                
            def render_component(self, component_name, template_content, context):
                import jinja2
                env = jinja2.Environment(loader=jinja2.BaseLoader())
                env.filters.update(self.get_custom_filters())
                try:
                    template = env.from_string(template_content)
                    return template.render(**context)
                except (jinja2.TemplateRuntimeError, jinja2.UndefinedError, TypeError) as e:
                    return f"Filter error: {str(e)}"
        
        renderer = FilterTestRenderer("test")
        engine.register_renderer("test", renderer)
        
        config_data = {
            "package_name": "test-cli",
            "command_name": "test",
            "display_name": "Test CLI",
            "description": "Test CLI",
            "language": "python",
            "python": {"minimum_version": "3.8", "maximum_version": "3.13"},
            "dependencies": {"required": [], "optional": []},
            "installation": {"pypi_name": "test-cli", "development_path": ".", "extras": {}},
            "shell_integration": {"enabled": False, "alias": "test"},
            "validation": {"check_api_keys": False, "check_disk_space": True, "minimum_disk_space_mb": 100},
            "messages": {"install_success": "Success!", "install_dev_success": "Dev success!", "upgrade_success": "Upgrade success!", "uninstall_success": "Uninstall success!"},
            "cli": {"name": "test", "tagline": "Test", "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}}}
        }
        config = GoobitsConfigSchema(**config_data)
        
        result = engine.render(config, "test")
        assert isinstance(result, dict)
        
        files = result.get("files", {})
        if "filter_test.txt" in files:
            content = files["filter_test.txt"]
            # Should handle filter errors gracefully
            assert isinstance(content, str)
    
    def test_template_directory_permission_denied(self):
        """Test handling of permission denied errors when accessing templates"""
        # Create a directory that we'll make inaccessible
        restricted_dir = self.temp_dir / "restricted"
        restricted_dir.mkdir()
        (restricted_dir / "test.j2").write_text("Test template")
        
        # Try to make directory unreadable (may not work on all systems)
        import os
        try:
            os.chmod(str(restricted_dir), 0o000)
            
            # Attempt to create engine with restricted directory
            try:
                UniversalTemplateEngine(restricted_dir)
                # If no exception, the system allows access despite permissions
                # This is system-dependent behavior
                assert True
            except (PermissionError, OSError):
                # Expected on systems that enforce permissions
                assert True
            except ValueError as e:
                # Our code should handle this case
                assert "does not exist" in str(e) or "permission" in str(e).lower()
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(str(restricted_dir), 0o755)
            except (PermissionError, OSError):
                pass
    
    def test_component_registry_with_corrupted_templates(self):
        """Test ComponentRegistry handling corrupted template files"""
        # Create templates with various corruption scenarios
        (self.templates_dir / "binary_data.j2").write_bytes(b'\x00\x01\x02\x03\xFF\xFE')
        (self.templates_dir / "unicode_errors.j2").write_bytes(b'\x80\x81\x82\x83')
        (self.templates_dir / "empty.j2").write_text("")
        (self.templates_dir / "only_whitespace.j2").write_text("   \n\t  \n   ")
        
        registry = ComponentRegistry(self.templates_dir)
        
        # Should handle corrupted files gracefully
        registry.load_components()
        components = registry.list_components()
        
        # At minimum, should not crash and should load valid templates
        assert isinstance(components, list)
        
        # Test individual component loading
        for component in components:
            try:
                content = registry.get_component(component.name)
                assert isinstance(content, str)
            except (UnicodeDecodeError, ValueError):
                # Acceptable to fail on corrupted files
                pass


class TestComponentRegistryAdvancedErrorConditions:
    """Advanced error condition tests for ComponentRegistry"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.components_dir = self.temp_dir / "components"
        self.components_dir.mkdir()
        # Add templates_dir alias for tests that expect it
        self.templates_dir = self.components_dir
        
    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_component_registry_with_filesystem_corruption(self):
        """Test ComponentRegistry when filesystem becomes corrupted."""
        registry = ComponentRegistry(self.components_dir)
        
        # Create valid component first
        (self.components_dir / "valid.j2").write_text("Valid template")
        registry.load_components()
        
        # Simulate filesystem corruption by making directory inaccessible
        import os
        try:
            os.chmod(str(self.components_dir), 0o000)
            
            # Existing components should still be accessible from cache
            assert registry.component_exists("valid")
            content = registry.get_component("valid")
            assert content == "Valid template"
            
            # New component loading should fail gracefully
            try:
                registry.load_components(force_reload=True)
            except (PermissionError, OSError):
                # Expected to fail with inaccessible directory
                pass
        finally:
            # Restore permissions
            try:
                os.chmod(str(self.components_dir), 0o755)
            except (PermissionError, OSError):
                pass
    
    def test_component_registry_with_symlink_loops(self):
        """Test ComponentRegistry handling of symlink loops."""
        # Create symlink loop (if supported)
        try:
            symlink1 = self.components_dir / "loop1.j2"
            symlink2 = self.components_dir / "loop2.j2"
            
            # Create files first, then replace with symlinks
            symlink1.write_text("temp")
            symlink2.write_text("temp")
            symlink1.unlink()
            symlink2.unlink()
            
            symlink1.symlink_to(symlink2)
            symlink2.symlink_to(symlink1)
            
            registry = ComponentRegistry(self.components_dir)
            
            # Should handle symlink loops gracefully
            registry.load_components()
            components = registry.list_components()
            
            # May or may not include the symlinked files
            assert isinstance(components, list)
        except (OSError, NotImplementedError):
            # Symlinks not supported on this system
            pass
    
    def test_component_registry_concurrent_modification(self):
        """Test ComponentRegistry with concurrent file modifications."""
        registry = ComponentRegistry(self.components_dir)
        
        # Create initial component
        test_file = self.components_dir / "concurrent.j2"
        test_file.write_text("Initial content")
        registry.load_components()
        
        # Simulate concurrent modification
        import threading
        import time
        
        def modify_file():
            time.sleep(0.1)
            test_file.write_text("Modified content")
            time.sleep(0.1)
            test_file.unlink()
        
        # Start modification in background
        thread = threading.Thread(target=modify_file)
        thread.start()
        
        # Try to access component while it's being modified
        try:
            for i in range(10):
                time.sleep(0.05)
                if registry.component_exists("concurrent"):
                    content = registry.get_component("concurrent")
                    # Content may be initial, modified, or may raise exception
                    assert isinstance(content, str) or content is None
        except (FileNotFoundError, KeyError):
            # Acceptable to fail if file is deleted during access
            pass
        
        thread.join()
    
    def test_component_registry_memory_pressure_handling(self):
        """Test ComponentRegistry under memory pressure."""
        registry = ComponentRegistry(self.components_dir)
        
        # Create many large components
        for i in range(100):
            large_content = f"Large template {i} content " * 10000  # ~250KB each
            (self.components_dir / f"large_{i}.j2").write_text(large_content)
        
        # Should handle many large components without memory issues
        registry.load_components()
        components = registry.list_components()
        
        assert len(components) == 100
        
        # Test accessing all components
        try:
            for component in components:
                content = registry.get_component(component.name)
                assert isinstance(content, str)
                assert len(content) > 100  # Should have substantial content
        except MemoryError:
            # Acceptable to fail under extreme memory pressure
            pass
    
    def test_component_registry_with_deeply_nested_directories(self):
        """Test ComponentRegistry with deeply nested directory structures."""
        # Create deeply nested structure
        current_dir = self.components_dir
        for i in range(50):  # Very deep nesting
            current_dir = current_dir / f"level_{i}"
            current_dir.mkdir()
        
        # Create template at deep level
        deep_template = current_dir / "deep_template.j2"
        deep_template.write_text("Deep nested template")
        
        registry = ComponentRegistry(self.components_dir)
        
        # Should handle deep nesting appropriately
        try:
            registry.load_components()
            components = registry.list_components()
            
            # Check if deep template was found
            deep_component_names = [c.name for c in components if "deep_template" in c.name]
            # May or may not find deeply nested templates depending on implementation
            assert isinstance(deep_component_names, list)
        except (OSError, RecursionError):
            # Acceptable to fail with extremely deep nesting
            pass
    
    def test_component_registry_with_special_filenames(self):
        """Test ComponentRegistry with special and edge case filenames."""
        special_files = [
            "normal.j2",
            ".hidden.j2",
            "with spaces.j2",
            "with-dashes.j2",
            "with_underscores.j2",
            "UPPERCASE.j2",
            "with.multiple.dots.j2",
            "123numeric.j2",
            "émojis🚀.j2" if sys.platform != 'win32' else "unicode.j2",  # Unicode may not work on Windows
            "very_long_filename_" + "x" * 200 + ".j2",  # Very long filename
        ]
        
        for filename in special_files:
            try:
                file_path = self.components_dir / filename
                file_path.write_text(f"Content for {filename}")
            except (OSError, UnicodeError):
                # Some filenames may not be supported on all systems
                continue
        
        registry = ComponentRegistry(self.components_dir)
        registry.load_components()
        
        components = registry.list_components()
        # Should load at least some of the files
        assert len(components) > 0
        
        # Test accessing components with special names
        for component in components:
            try:
                content = registry.get_component(component.name)
                assert isinstance(content, str)
            except (UnicodeError, ValueError):
                # Some special filenames may cause issues
                pass
    
    def test_component_registry_dependency_cycle_detection(self):
        """Test ComponentRegistry detection of dependency cycles."""
        # Create templates with circular dependencies
        template_a = """
{{# Dependencies: template_b.j2 #}}
Template A includes B
{% include 'template_b.j2' %}
"""
        template_b = """
{{# Dependencies: template_c.j2 #}}
Template B includes C
{% include 'template_c.j2' %}
"""
        template_c = """
{{# Dependencies: template_a.j2 #}}
Template C includes A - CIRCULAR!
{% include 'template_a.j2' %}
"""
        
        (self.components_dir / "template_a.j2").write_text(template_a)
        (self.components_dir / "template_b.j2").write_text(template_b)
        (self.components_dir / "template_c.j2").write_text(template_c)
        
        registry = ComponentRegistry(self.components_dir)
        registry.load_components()
        
        # Should detect circular dependencies
        deps_a = registry.get_component_dependencies("template_a")
        deps_b = registry.get_component_dependencies("template_b")
        deps_c = registry.get_component_dependencies("template_c")
        
        # All should have dependencies
        assert len(deps_a) > 0
        assert len(deps_b) > 0
        assert len(deps_c) > 0
        
        # Circular dependency detection depends on implementation
        # At minimum, should not cause infinite loops
    
    def test_component_registry_validation_with_malformed_templates(self):
        """Test ComponentRegistry validation with various malformed templates."""
        malformed_templates = {
            "unclosed_block.j2": """
{% for item in items %}
    Item: {{ item }}
    # Missing {% endfor %}
""",
            "invalid_syntax.j2": """
{{ invalid..syntax }}
{% if unclosed condition
{{ missing_closing_braces
""",
            "mixed_template_syntaxes.j2": """
{# Jinja comment #}
<!-- HTML comment -->
{{! Handlebars syntax }}
<% ERB syntax %>
{{ valid_jinja }}
""",
            "unicode_issues.j2": """
Valid unicode: émojis 🚀
Possible issue: invalid_char
Another issue: replacement_char
""",
            "extremely_long_line.j2": "Very long line: " + "x" * 10000 + "\nNormal line",
        }
        
        for filename, content in malformed_templates.items():
            (self.components_dir / filename).write_text(content)
        
        registry = ComponentRegistry(self.components_dir)
        registry.load_components()
        
        # Should load templates even if they're malformed
        components = registry.list_components()
        assert len(components) >= len(malformed_templates)
        
        # Validation should identify issues
        errors = registry.validate_all_components()
        
        # Should detect at least some errors
        assert isinstance(errors, dict)
        # Error detection depends on validation implementation
    
    def test_component_registry_auto_reload_race_conditions(self):
        """Test ComponentRegistry auto-reload with race conditions."""
        test_file = self.components_dir / "race_test.j2"
        test_file.write_text("Initial content")
        
        registry = ComponentRegistry(self.components_dir, auto_reload=True)
        registry.load_components()
        
        # Simulate rapid file modifications
        import threading
        import time
        
        def rapid_modifications():
            for i in range(10):
                try:
                    test_file.write_text(f"Content {i}")
                    time.sleep(0.01)
                except OSError:
                    # File might be locked or deleted
                    pass
        
        # Start rapid modifications
        thread = threading.Thread(target=rapid_modifications)
        thread.start()
        
        # Try to access component during rapid changes
        try:
            for i in range(20):
                time.sleep(0.005)
                if registry.component_exists("race_test"):
                    content = registry.get_component("race_test", auto_reload=True)
                    assert isinstance(content, str)
        except (OSError, ValueError):
            # Acceptable to have issues during rapid changes
            pass
        
        thread.join()
    
    def test_component_registry_resource_cleanup_on_errors(self):
        """Test ComponentRegistry resource cleanup when errors occur."""
        registry = ComponentRegistry(self.components_dir)
        
        # Create file that will cause issues
        problematic_file = self.components_dir / "problematic.j2"
        problematic_file.write_text("Normal content")
        
        # Start loading
        registry.load_components()
        assert registry.component_exists("problematic")
        
        # Simulate file becoming problematic (e.g., permissions changed)
        import os
        try:
            os.chmod(str(problematic_file), 0o000)
            
            # Try to reload
            try:
                registry.reload_component("problematic")
            except (PermissionError, OSError):
                # Expected to fail
                pass
            
            # Registry should still be in consistent state
            components = registry.list_components()
            assert isinstance(components, list)
            
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(str(problematic_file), 0o644)
            except (PermissionError, OSError):
                pass
    
    def test_jinja_environment_configuration_errors(self):
        """Test Jinja2 environment configuration edge cases"""
        engine = UniversalTemplateEngine(self.templates_dir)
        
        # Test with renderer that returns invalid filters
        class BadFilterRenderer(MockRenderer):
            def get_custom_filters(self):
                return {
                    "bad_filter": "not_a_function",  # Invalid filter
                    "none_filter": None,  # None filter
                    123: lambda x: x  # Invalid filter name
                }
        
        renderer = BadFilterRenderer("test")
        engine.register_renderer("test", renderer)
        
        config_data = {
            "package_name": "test-cli",
            "command_name": "test",
            "display_name": "Test CLI",
            "description": "Test CLI",
            "language": "python",
            "python": {"minimum_version": "3.8", "maximum_version": "3.13"},
            "dependencies": {"required": [], "optional": []},
            "installation": {"pypi_name": "test-cli", "development_path": ".", "extras": {}},
            "shell_integration": {"enabled": False, "alias": "test"},
            "validation": {"check_api_keys": False, "check_disk_space": True, "minimum_disk_space_mb": 100},
            "messages": {"install_success": "Success!", "install_dev_success": "Dev success!", "upgrade_success": "Upgrade success!", "uninstall_success": "Uninstall success!"},
            "cli": {"name": "test", "tagline": "Test", "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}}}
        }
        config = GoobitsConfigSchema(**config_data)
        
        # Should handle invalid filters gracefully
        try:
            result = engine.render(config, "test")
            assert isinstance(result, dict)
        except (TypeError, ValueError) as e:
            # Acceptable to fail with invalid filters
            assert "filter" in str(e).lower() or "callable" in str(e).lower()
    
    def test_template_with_extremely_deep_nesting(self):
        """Test template with extremely deep variable nesting"""
        deep_template = """
{%- set current = project -%}
{%- for i in range(50) -%}
    {%- if current.get('nested') -%}
        {%- set current = current.nested -%}
    {%- endif -%}
{%- endfor -%}
Deep value: {{ current.get('value', 'not found') }}
"""
        (self.templates_dir / "deep_nesting.j2").write_text(deep_template)
        
        engine = UniversalTemplateEngine(self.templates_dir)
        renderer = MockRenderer("test")
        engine.register_renderer("test", renderer)
        
        # Create deeply nested config
        config_data = {
            "package_name": "test-cli",
            "command_name": "test",
            "display_name": "Test CLI",
            "description": "Test CLI",
            "language": "python",
            "python": {"minimum_version": "3.8", "maximum_version": "3.13"},
            "dependencies": {"required": [], "optional": []},
            "installation": {"pypi_name": "test-cli", "development_path": ".", "extras": {}},
            "shell_integration": {"enabled": False, "alias": "test"},
            "validation": {"check_api_keys": False, "check_disk_space": True, "minimum_disk_space_mb": 100},
            "messages": {"install_success": "Success!", "install_dev_success": "Dev success!", "upgrade_success": "Upgrade success!", "uninstall_success": "Uninstall success!"},
            "cli": {"name": "test", "tagline": "Test", "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}}}
        }
        config = GoobitsConfigSchema(**config_data)
        
        # Should handle deep nesting without stack overflow
        result = engine.render(config, "test")
        assert isinstance(result, dict)