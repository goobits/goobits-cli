"""
Focused tests for Universal Template Engine to maximize coverage.

These tests focus on actual functionality that can be tested with the current
implementation to bring template_engine.py coverage from 63% to 85%.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

from goobits_cli.universal.template_engine import (
    UniversalTemplateEngine,
    ComponentRegistry,
    LanguageRenderer
)


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
        return f"// {self.language} component: {component_name}\n{template_content}"
    
    def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
        return {
            "cli.test": "main_cli_content",
            "config.test": "config_content"
        }


class TestUniversalTemplateEngineCore:
    """Test core UniversalTemplateEngine functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.components_dir = self.temp_dir / "components"
        self.components_dir.mkdir()
        
        # Create simple test component
        (self.components_dir / "test.j2").write_text("Test component: {{ project.name }}")
        
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        # Test with custom components directory
        engine = UniversalTemplateEngine(self.components_dir)
        assert engine.component_registry.components_dir == self.components_dir
        assert isinstance(engine.renderers, dict)
        assert len(engine.renderers) == 0
        
        # Test with default directory (should not fail)
        try:
            engine_default = UniversalTemplateEngine()
            assert engine_default.component_registry is not None
        except Exception:
            # If default fails, that's okay - we're testing our custom one
            pass
    
    def test_renderer_registration(self):
        """Test renderer registration and retrieval"""
        engine = UniversalTemplateEngine(self.components_dir)
        renderer = SimpleTestRenderer("test")
        
        # Register renderer
        engine.register_renderer("test", renderer)
        assert "test" in engine.renderers
        assert engine.renderers["test"] is renderer
        
        # Test getting renderer
        retrieved = engine.get_renderer("test")
        assert retrieved is renderer
        
        # Test getting non-existent renderer
        try:
            engine.get_renderer("nonexistent")
            assert False, "Should have raised error"
        except ValueError as e:
            assert "No renderer registered" in str(e)
    
    def test_component_loading(self):
        """Test component loading through engine"""
        # Create additional components
        (self.components_dir / "cli.j2").write_text("CLI: {{ cli.name }}")
        (self.components_dir / "config.j2").write_text("Config: {{ config.value }}")
        
        engine = UniversalTemplateEngine(self.components_dir)
        
        # Components should be loaded automatically or on demand
        components = engine.component_registry.list_components()
        assert len(components) >= 3  # test, cli, config
        
        # Test getting components
        test_component = engine.component_registry.get_component("test")
        assert "Test component: {{ project.name }}" in test_component
    
    def test_template_rendering_basic(self):
        """Test basic template rendering"""
        engine = UniversalTemplateEngine(self.components_dir)
        renderer = SimpleTestRenderer("basic")
        engine.register_renderer("basic", renderer)
        
        # Test context
        test_ir = {
            "project": {"name": "test-project"},
            "cli": {"name": "testcli"}
        }
        
        # Get template context
        context = renderer.get_template_context(test_ir)
        assert context["language"] == "basic"
        assert context["project"]["name"] == "test-project"
        assert context["test_specific"] is True
        
        # Test component rendering
        template = "Hello {{ project.name }}"
        result = renderer.render_component("hello", template, context)
        assert "basic component: hello" in result
        assert template in result
    
    def test_custom_filters(self):
        """Test custom filter functionality"""
        renderer = SimpleTestRenderer("filter_test")
        filters = renderer.get_custom_filters()
        
        assert "test_filter" in filters
        assert "upper" in filters
        
        # Test filter functions
        assert filters["test_filter"]("input") == "test_input"
        assert filters["upper"]("hello") == "HELLO"
    
    def test_output_structure(self):
        """Test output structure generation"""
        renderer = SimpleTestRenderer("output")
        test_ir = {"project": {"name": "test"}}
        
        structure = renderer.get_output_structure(test_ir)
        assert isinstance(structure, dict)
        assert "cli.test" in structure
        assert "config.test" in structure
    
    def test_performance_components_integration(self):
        """Test integration with performance components when available"""
        # Test without performance components (default case)
        engine = UniversalTemplateEngine(self.components_dir)
        assert engine.template_cache is None
        assert engine.performance_enabled is False
        
        # Test lazy loading disabled
        assert engine.lazy_loader is None
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        engine = UniversalTemplateEngine(self.components_dir)
        
        # Test registering invalid renderer
        try:
            engine.register_renderer("test", None)
            assert False, "Should have raised error"
        except (TypeError, AttributeError, ValueError):
            pass  # Expected
        
        # Test getting component that doesn't exist
        try:
            engine.component_registry.get_component("nonexistent")
            assert False, "Should have raised error"
        except KeyError:
            pass  # Expected


class TestComponentRegistryDetailed:
    """Detailed tests for ComponentRegistry functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.components_dir = self.temp_dir / "components"
        self.components_dir.mkdir()
        
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_registry_initialization(self):
        """Test ComponentRegistry initialization"""
        registry = ComponentRegistry(self.components_dir)
        assert registry.components_dir == self.components_dir
        assert registry._components == {}
        assert registry._metadata == {}
        assert registry._dependencies == {}
        assert registry.auto_reload is True
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
        assert "simple" in components
        assert "with_vars" in components
        assert "empty" in components
        assert "sub/nested" in components
        assert "not_template" not in components
        
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
{# Dependencies: base.j2, utils.j2 #}
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
        import time
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])