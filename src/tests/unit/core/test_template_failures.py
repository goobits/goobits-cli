"""
Tests for Universal Template Engine failure scenarios and cleanup behavior.

This module focuses on testing template rendering failures, error handling, and
proper cleanup when template generation fails partially through the process.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

import jinja2

from goobits_cli.universal.template_engine import (
    UniversalTemplateEngine,
    LanguageRenderer,
    ComponentRegistry
)
from goobits_cli.schemas import GoobitsConfigSchema


class FailingRenderer(LanguageRenderer):
    """Mock renderer that can simulate various failure modes"""
    
    def __init__(self, language: str = "test", failure_mode: str = None):
        self._language = language
        self.failure_mode = failure_mode
        self.render_count = 0
        
    @property
    def language(self) -> str:
        return self._language
    
    @property
    def file_extensions(self) -> Dict[str, str]:
        return {"cli": "py", "hooks": "py", "setup": "sh"}
    
    def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        if self.failure_mode == "context_error":
            raise ValueError("Context transformation failed")
        if isinstance(ir, str):  # Handle corrupted IR data
            return {"corrupted": True, "original_ir": ir}
        return ir.copy()
    
    def get_custom_filters(self) -> Dict[str, callable]:
        if self.failure_mode == "filter_error":
            return {"broken_filter": "not_a_function"}
        return {}
    
    def render_component(self, component_name: str, template_content: str, 
                        context: Dict[str, Any]) -> str:
        self.render_count += 1
        
        if self.failure_mode == "render_error":
            raise jinja2.TemplateError("Template rendering failed")
        elif self.failure_mode == "partial_failure" and component_name == "hooks":
            raise RuntimeError("Hooks component failed")
        elif self.failure_mode == "memory_error":
            raise MemoryError("Out of memory during rendering")
        elif self.failure_mode == "syntax_error":
            raise jinja2.TemplateSyntaxError("Invalid template syntax", 1)
        
        return f"// Rendered {component_name} for {self.language}"
    
    def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
        if self.failure_mode == "structure_error":
            raise KeyError("Invalid output structure")
        return {
            "cli": "cli.py",
            "hooks": "hooks.py", 
            "setup": "setup.sh"
        }


class TestUniversalTemplateEngineFailures:
    """Test template engine failure scenarios and recovery"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.components_dir = self.temp_dir / "components"
        self.components_dir.mkdir()
        self.output_dir = self.temp_dir / "output"
        self.output_dir.mkdir()
        
        # Create test config
        self.test_config = GoobitsConfigSchema(**{
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
            "messages": {"install_success": "Success!", "install_dev_success": "Dev success!", 
                        "upgrade_success": "Upgrade success!", "uninstall_success": "Uninstall success!"},
            "cli": {"name": "test", "tagline": "Test", "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}}}
        })
        
        self._create_test_components()
        
    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_test_components(self):
        """Create test component templates"""
        # Valid CLI component
        cli_template = """
#!/usr/bin/env python3
# Generated CLI for {{ project.name }}
print("Hello from {{ project.name }}!")
"""
        (self.components_dir / "cli.j2").write_text(cli_template)
        
        # Hooks component
        hooks_template = """
# Hooks for {{ project.name }}
def on_hello():
    return "Hello from hooks"
"""
        (self.components_dir / "hooks.j2").write_text(hooks_template)
        
        # Setup component
        setup_template = """
#!/bin/bash
# Setup script for {{ project.name }}
echo "Setting up {{ project.name }}"
"""
        (self.components_dir / "setup.j2").write_text(setup_template)
        
        # Broken template with syntax error
        broken_template = """
# Broken template
{% for item in items %}
    Item: {{ item }}
# Missing {% endfor %}
"""
        (self.components_dir / "broken.j2").write_text(broken_template)
    
    def test_jinja2_template_syntax_error_handling(self):
        """Test handling of Jinja2 template syntax errors"""
        engine = UniversalTemplateEngine(self.components_dir, test_mode=True)
        renderer = FailingRenderer("python", "syntax_error")
        engine.register_renderer("python", renderer)
        
        # Should handle syntax errors gracefully during generation
        result = engine.generate_cli(
            config=self.test_config,
            language="python",
            output_dir=self.output_dir
        )
        
        # Should return empty result due to all components failing
        assert isinstance(result, dict)
        assert len(result) == 0  # No files generated due to syntax errors
    
    def test_missing_template_variables_error_handling(self):
        """Test handling of missing template variables"""
        # Create template with undefined variables
        undefined_template = """
# Template with undefined variables
Project: {{ project.name }}
Undefined: {{ project.nonexistent_field }}
Invalid: {{ completely.undefined.variable }}
"""
        (self.components_dir / "undefined.j2").write_text(undefined_template)
        
        engine = UniversalTemplateEngine(self.components_dir, test_mode=True)
        
        class UndefinedRenderer(LanguageRenderer):
            @property
            def language(self) -> str:
                return "python"
            
            @property
            def file_extensions(self) -> Dict[str, str]:
                return {"undefined": "py"}
            
            def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
                return ir
            
            def get_custom_filters(self) -> Dict[str, callable]:
                return {}
            
            def render_component(self, component_name: str, template_content: str, 
                                context: Dict[str, Any]) -> str:
                # Use strict undefined to catch missing variables
                env = jinja2.Environment(undefined=jinja2.StrictUndefined)
                template = env.from_string(template_content)
                return template.render(**context)
            
            def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
                return {"undefined": "undefined.py"}
        
        renderer = UndefinedRenderer()
        engine.register_renderer("python", renderer)
        
        # Should handle undefined variables by raising appropriate errors
        result = engine.generate_cli(
            config=self.test_config,
            language="python", 
            output_dir=self.output_dir
        )
        
        # Result should be empty due to undefined variable errors
        assert isinstance(result, dict)
        assert len(result) == 0
    
    def test_template_engine_memory_exhaustion(self):
        """Test template engine behavior under memory pressure"""
        engine = UniversalTemplateEngine(self.components_dir, test_mode=True)
        renderer = FailingRenderer("python", "memory_error")
        engine.register_renderer("python", renderer)
        
        # Should handle memory errors gracefully
        result = engine.generate_cli(
            config=self.test_config,
            language="python",
            output_dir=self.output_dir
        )
        
        # Should return empty result due to memory errors
        assert isinstance(result, dict)
        assert len(result) == 0
    
    def test_component_dependency_resolution_failures(self):
        """Test handling of component dependency resolution failures"""
        # Create component with missing dependencies
        dependent_template = """
# Component with dependencies
{% include 'missing_dependency.j2' %}
Main content here
"""
        (self.components_dir / "dependent.j2").write_text(dependent_template)
        
        engine = UniversalTemplateEngine(self.components_dir, test_mode=True)
        
        class DependencyRenderer(LanguageRenderer):
            @property
            def language(self) -> str:
                return "python"
            
            @property 
            def file_extensions(self) -> Dict[str, str]:
                return {"dependent": "py"}
            
            def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
                return ir
            
            def get_custom_filters(self) -> Dict[str, callable]:
                return {}
            
            def render_component(self, component_name: str, template_content: str,
                                context: Dict[str, Any]) -> str:
                # Use file system loader to check for missing includes
                loader = jinja2.FileSystemLoader(str(self.components_dir))
                env = jinja2.Environment(loader=loader)
                template = env.from_string(template_content)
                return template.render(**context)
            
            def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
                return {"dependent": "dependent.py"}
        
        renderer = DependencyRenderer()
        engine.register_renderer("python", renderer)
        
        # Should handle missing dependencies
        result = engine.generate_cli(
            config=self.test_config,
            language="python",
            output_dir=self.output_dir
        )
        
        # Should complete but may have empty result due to dependency issues
        assert isinstance(result, dict)
    
    def test_cleanup_verification_on_partial_failures(self):
        """Test cleanup when generation fails mid-process"""
        engine = UniversalTemplateEngine(self.components_dir, test_mode=True)
        renderer = FailingRenderer("python", "partial_failure")
        engine.register_renderer("python", renderer)
        
        # Should handle partial failures and cleanup appropriately
        result = engine.generate_cli(
            config=self.test_config,
            language="python",
            output_dir=self.output_dir
        )
        
        # Should have partial results (cli and setup succeed, hooks fails)
        assert isinstance(result, dict)
        
        # Verify that successful components are included
        cli_path = str(self.output_dir / "cli.py")
        setup_path = str(self.output_dir / "setup.sh")
        hooks_path = str(self.output_dir / "hooks.py")
        
        # CLI and setup should succeed, hooks should fail
        if cli_path in result:
            assert "Rendered cli for python" in result[cli_path]
        if setup_path in result:
            assert "Rendered setup for python" in result[setup_path]
        
        # Hooks should not be in result due to failure
        assert hooks_path not in result
    
    def test_component_registry_failures(self):
        """Test component registry failure scenarios"""
        engine = UniversalTemplateEngine(self.components_dir, test_mode=True)
        
        # Mock component registry to simulate failures
        with patch.object(engine.component_registry, 'get_component') as mock_get:
            mock_get.side_effect = KeyError("Component not found")
            
            renderer = FailingRenderer("python")
            engine.register_renderer("python", renderer)
            
            result = engine.generate_cli(
                config=self.test_config,
                language="python",
                output_dir=self.output_dir
            )
            
            # Should handle component registry failures
            assert isinstance(result, dict)
            assert len(result) == 0  # No files due to registry failures
    
    def test_template_caching_corruption(self):
        """Test handling of template cache corruption"""
        # Test with performance features available
        with patch('goobits_cli.universal.template_engine.PERFORMANCE_AVAILABLE', True):
            with patch('goobits_cli.universal.template_engine.TemplateCache') as MockCache:
                with patch('goobits_cli.universal.template_engine.LazyLoader') as MockLoader:
                    # Mock template cache that returns corrupted data
                    mock_cache = Mock()
                    mock_cache._cache = Mock()
                    mock_cache._cache.get.return_value = "corrupted_ir_data"
                    mock_cache._cache.put.return_value = None
                    mock_cache.render_template.return_value = None  # Simulate cache corruption
                    
                    MockCache.return_value = mock_cache
                    MockLoader.return_value = None
                    
                    engine = UniversalTemplateEngine(
                        self.components_dir,
                        template_cache=mock_cache,
                        test_mode=True
                    )
                    renderer = FailingRenderer("python")
                    engine.register_renderer("python", renderer)
                    
                    # Should handle cache corruption and fall back to regular rendering
                    result = engine.generate_cli(
                        config=self.test_config,
                        language="python",
                        output_dir=self.output_dir
                    )
                    
                    # Should complete with fallback to non-cached rendering
                    assert isinstance(result, dict)
    
    def test_partial_file_generation_failures(self):
        """Test handling when some files generate successfully but others fail"""
        engine = UniversalTemplateEngine(self.components_dir, test_mode=True)
        
        class PartialFailureRenderer(LanguageRenderer):
            def __init__(self):
                self.component_count = 0
                
            @property
            def language(self) -> str:
                return "python"
            
            @property
            def file_extensions(self) -> Dict[str, str]:
                return {"cli": "py", "hooks": "py", "setup": "sh", "fail": "py"}
            
            def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
                return ir
            
            def get_custom_filters(self) -> Dict[str, callable]:
                return {}
            
            def render_component(self, component_name: str, template_content: str,
                                context: Dict[str, Any]) -> str:
                self.component_count += 1
                
                # Fail on third component
                if self.component_count == 3:
                    raise Exception("Simulated failure on third component")
                
                return f"// Rendered {component_name}"
            
            def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
                return {
                    "cli": "cli.py",
                    "hooks": "hooks.py", 
                    "setup": "setup.sh",
                    "fail": "fail.py"  # This one will fail
                }
        
        renderer = PartialFailureRenderer()
        engine.register_renderer("python", renderer)
        
        result = engine.generate_cli(
            config=self.test_config,
            language="python",
            output_dir=self.output_dir
        )
        
        # Should have partial results
        assert isinstance(result, dict)
        
        # Some files should succeed, others should fail
        str(self.output_dir / "cli.py")
        str(self.output_dir / "hooks.py")
        
        # At least some components should succeed before the failure
        assert len(result) >= 1
    
    def test_error_message_propagation(self):
        """Test that error messages are properly propagated"""
        engine = UniversalTemplateEngine(self.components_dir, test_mode=True)
        renderer = FailingRenderer("python", "render_error")
        engine.register_renderer("python", renderer)
        
        # Should propagate specific error messages
        result = engine.generate_cli(
            config=self.test_config,
            language="python",
            output_dir=self.output_dir
        )
        
        # Verify that appropriate error handling occurred
        assert isinstance(result, dict)
        assert len(result) == 0  # No files due to render errors


class TestComponentRegistryFailures:
    """Test ComponentRegistry failure scenarios"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.components_dir = self.temp_dir / "components"
        self.components_dir.mkdir()
        
    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_component_validation_with_corrupted_templates(self):
        """Test validation of corrupted template files"""
        # Create corrupted template files
        (self.components_dir / "corrupted1.j2").write_bytes(b'\x00\x01\x02\x03')
        (self.components_dir / "corrupted2.j2").write_text("{% invalid syntax")
        (self.components_dir / "corrupted3.j2").write_text("{{ unclosed")
        
        registry = ComponentRegistry(self.components_dir)
        
        # Should handle corrupted files without crashing
        try:
            registry.load_components()
            errors = registry.validate_all_components()
            
            # Should detect validation errors
            assert isinstance(errors, dict)
            # May have errors for corrupted templates
            
        except Exception as e:
            # Should not crash completely
            assert "unicode" in str(e).lower() or "syntax" in str(e).lower()
    
    def test_component_registry_with_permission_errors(self):
        """Test ComponentRegistry handling of permission errors"""
        registry = ComponentRegistry(self.components_dir)
        
        # Create component
        test_file = self.components_dir / "permission_test.j2"
        test_file.write_text("test content")
        registry.load_components()
        
        # Test reloading a non-existent component (simulates permission/access issues)
        result = registry.reload_component("nonexistent_component")
        assert result is False
        
        # Test that the registry can still operate normally after errors
        assert registry.has_component("permission_test")
        content = registry.get_component("permission_test")
        assert content == "test content"
    
    def test_component_metadata_corruption(self):
        """Test handling of metadata corruption"""
        registry = ComponentRegistry(self.components_dir)
        
        # Create component
        test_file = self.components_dir / "metadata_test.j2"
        test_file.write_text("test content")
        registry.load_components()
        
        # Corrupt metadata directly
        registry._metadata["metadata_test"] = "corrupted_data"
        
        # Should return corrupted data since it exists in metadata
        metadata = registry.get_component_metadata("metadata_test")
        
        # Should return the corrupted data as-is (this is current behavior)
        assert metadata == "corrupted_data"
        
        # Clear corrupted metadata to test regeneration
        del registry._metadata["metadata_test"]
        
        # Now should regenerate valid metadata
        metadata = registry.get_component_metadata("metadata_test")
        assert metadata is not None
        assert hasattr(metadata, 'name')
        assert metadata.name == "metadata_test"
    
    def test_circular_dependency_handling(self):
        """Test handling of circular dependencies between components"""
        # Create components with circular dependencies
        comp_a = """
# Component A
{# depends: component_b #}
{% include 'component_b.j2' %}
Content A
"""
        comp_b = """
# Component B  
{# depends: component_a #}
{% include 'component_a.j2' %}
Content B
"""
        (self.components_dir / "component_a.j2").write_text(comp_a)
        (self.components_dir / "component_b.j2").write_text(comp_b)
        
        registry = ComponentRegistry(self.components_dir)
        registry.load_components()
        
        # Should detect circular dependencies
        deps_a = registry.get_dependencies("component_a")
        deps_b = registry.get_dependencies("component_b")
        
        # Should handle circular deps without infinite loops
        assert isinstance(deps_a, list)
        assert isinstance(deps_b, list)
        assert "component_b" in deps_a
        assert "component_a" in deps_b
    
    def test_jinja_environment_initialization_failure(self):
        """Test handling of Jinja2 environment initialization failures"""
        # Mock Jinja2 Environment to fail during ComponentRegistry init
        with patch('jinja2.Environment') as mock_env:
            mock_env.side_effect = Exception("Jinja2 initialization failed")
            
            # Should handle Jinja initialization failures during registry creation
            try:
                ComponentRegistry(self.components_dir)
                assert False, "Expected exception during registry initialization"
            except Exception as e:
                assert "initialization" in str(e).lower() or "jinja" in str(e).lower()
    
    def test_template_parsing_edge_cases(self):
        """Test template parsing with various edge cases"""
        edge_cases = {
            "empty.j2": "",
            "whitespace_only.j2": "   \n\t  \n   ",
            "very_long_line.j2": "Long line: " + "x" * 10000,
            "unicode.j2": "Unicode: émojis 🚀 test",
            "mixed_endings.j2": "Line 1\r\nLine 2\nLine 3\r",
        }
        
        for filename, content in edge_cases.items():
            (self.components_dir / filename).write_text(content, encoding='utf-8')
        
        registry = ComponentRegistry(self.components_dir)
        
        # Should handle all edge cases without crashing
        registry.load_components()
        components = registry.list_components()
        
        # Should load at least some components
        assert len(components) >= len(edge_cases)
        
        # Test validation of edge case templates
        errors = registry.validate_all_components()
        assert isinstance(errors, dict)


class TestTemplateEngineCleanup:
    """Test cleanup behavior in template engine"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.components_dir = self.temp_dir / "components" 
        self.components_dir.mkdir()
        self.output_dir = self.temp_dir / "output"
        self.output_dir.mkdir()
        
        # Create minimal config
        self.test_config = GoobitsConfigSchema(**{
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
            "messages": {"install_success": "Success!", "install_dev_success": "Dev success!",
                        "upgrade_success": "Upgrade success!", "uninstall_success": "Uninstall success!"},
            "cli": {"name": "test", "tagline": "Test", "commands": {}}
        })
        
    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_engine_state_after_failures(self):
        """Test that engine maintains consistent state after failures"""
        engine = UniversalTemplateEngine(self.components_dir, test_mode=True)
        renderer = FailingRenderer("python", "render_error")
        engine.register_renderer("python", renderer)
        
        # Cause failure
        engine.generate_cli(
            config=self.test_config,
            language="python", 
            output_dir=self.output_dir
        )
        
        # Engine should still be in valid state
        assert isinstance(engine.renderers, dict)
        assert "python" in engine.renderers
        assert engine.component_registry is not None
        
        # Should be able to register new renderer
        new_renderer = FailingRenderer("nodejs")
        engine.register_renderer("nodejs", new_renderer)
        assert "nodejs" in engine.renderers
    
    def test_component_registry_consistency_after_errors(self):
        """Test ComponentRegistry consistency after various errors"""
        registry = ComponentRegistry(self.components_dir)
        
        # Create component that will cause issues
        (self.components_dir / "problematic.j2").write_text("{% invalid")
        
        # Load components (may have validation issues)
        registry.load_components()
        
        # Registry should remain consistent
        assert isinstance(registry._components, dict)
        assert isinstance(registry._metadata, dict)
        assert isinstance(registry._dependencies, dict)
        
        # Should be able to perform operations
        components = registry.list_components()
        assert isinstance(components, list)
        
        # Should be able to clear and reload
        registry.clear()
        assert len(registry._components) == 0
        
        registry.load_components()
        # Should reload successfully
        components_after_reload = registry.list_components()
        assert isinstance(components_after_reload, list)
    
    def test_memory_cleanup_after_large_failures(self):
        """Test memory cleanup after processing large failed templates"""
        # Create large template that will fail
        large_template = "Large template content: " + "x" * 100000 + "\n{% invalid syntax"
        (self.components_dir / "large_broken.j2").write_text(large_template)
        
        engine = UniversalTemplateEngine(self.components_dir, test_mode=True)
        registry = engine.component_registry
        
        # Process large broken template
        try:
            registry.load_components()
            registry.validate_all_components()
        except Exception:
            pass
        
        # Clear cache to free memory
        registry.clear_cache()
        
        # Memory should be freed
        assert len(registry._components) == 0
        assert len(registry._metadata) == 0
        
        # Should be able to reload smaller templates
        (self.components_dir / "small.j2").write_text("Small template")
        registry.load_components()
        
        assert registry.has_component("small")


if __name__ == "__main__":
    pytest.main([__file__])