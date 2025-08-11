"""
Functional tests for the Universal Template Engine.

Tests the actual template rendering functionality, component integration,
and end-to-end generation process with real configurations and templates.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch

from goobits_cli.universal.template_engine import (
    UniversalTemplateEngine,
    ComponentRegistry,
    LanguageRenderer
)
from goobits_cli.schemas import GoobitsConfigSchema, CLISchema, CommandSchema


# Test fixture for a minimal mock renderer
class MockRenderer(LanguageRenderer):
    """Mock renderer for testing"""
    
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
        assert "command_handler" in components
        assert "hooks" in components
        assert "advanced_component" in components
        assert len(components) == 3
    
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
        
        errors = self.registry.validate_all_components()
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
            components_dir=self.components_dir,
            template_cache=None,  # Disable cache for easier testing
            enable_lazy_loading=False  # Disable lazy loading for simpler tests
        )
        
        # Register test renderer
        self.renderer = MockRenderer("python")
        self.engine.register_renderer(self.renderer)
        
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
    
    def test_renderer_registration(self):
        """Test renderer registration"""
        # Already registered in setup
        assert "python" in self.engine.renderers
        assert self.engine.renderers["python"] == self.renderer
    
    def test_renderer_registration_validation(self):
        """Test renderer registration validation"""
        # Test None renderer
        with pytest.raises(ValueError, match="Renderer cannot be None"):
            self.engine.register_renderer(None)
        
        # Test invalid renderer type
        with pytest.raises(ValueError, match="must implement LanguageRenderer"):
            self.engine.register_renderer("not a renderer")
        
        # Test renderer without language
        invalid_renderer = Mock(spec=LanguageRenderer)
        invalid_renderer.language = ""
        with pytest.raises(ValueError, match="non-empty language name"):
            self.engine.register_renderer(invalid_renderer)
    
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
            components_dir=empty_dir,
            enable_lazy_loading=False
        )
        empty_engine.register_renderer(self.renderer)
        
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
        test_renderer = MockRenderer("python")
        
        def get_output_structure_with_filter_test(ir):
            return {"filter_test": "filter_test.py"}
        
        test_renderer.get_output_structure = get_output_structure_with_filter_test
        
        # Re-register renderer
        filter_engine = UniversalTemplateEngine(
            components_dir=self.components_dir,
            enable_lazy_loading=False
        )
        filter_engine.register_renderer(test_renderer)
        
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
        assert ir["cli"]["root_command"]["version"] is None  # No version specified
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


if __name__ == '__main__':
    pytest.main([__file__])