#!/usr/bin/env python3
"""
Debug script to trace Python CLI generation runtime issues
"""
import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_js_string_filter():
    """Test the js_string filter implementation"""
    print("=== Testing js_string filter ===")
    try:
        from goobits_cli.universal.renderers.python_renderer import PythonRenderer
        renderer = PythonRenderer()
        filters = renderer.get_custom_filters()
        js_string_filter = filters.get('js_string')
        
        if js_string_filter:
            # Test various inputs
            test_cases = [
                "simple string",
                "string with 'quotes'",
                'string with "double quotes"',
                "string with\nnewlines",
                None,
                "",
                123,
            ]
            
            for test_case in test_cases:
                try:
                    result = js_string_filter(test_case)
                    print(f"✅ js_string({test_case!r}) = {result!r}")
                except Exception as e:
                    print(f"❌ js_string({test_case!r}) failed: {e}")
        else:
            print("❌ js_string filter not found")
            
    except Exception as e:
        print(f"❌ Failed to test js_string filter: {e}")
        traceback.print_exc()

def test_universal_engine_creation():
    """Test Universal Template Engine initialization"""
    print("\n=== Testing Universal Template Engine ===")
    try:
        from goobits_cli.universal.template_engine import UniversalTemplateEngine
        engine = UniversalTemplateEngine()
        print("✅ Universal Template Engine created successfully")
        
        # Test renderer registration
        from goobits_cli.universal.renderers.python_renderer import PythonRenderer
        renderer = PythonRenderer()
        engine.register_renderer("python", renderer)
        print("✅ Python renderer registered successfully")
        
        return engine, renderer
        
    except Exception as e:
        print(f"❌ Failed to create Universal Template Engine: {e}")
        traceback.print_exc()
        return None, None

def test_minimal_config_processing():
    """Test processing a minimal configuration"""
    print("\n=== Testing Minimal Config Processing ===")
    try:
        from goobits_cli.schemas import GoobitsConfigSchema, CLISchema, CommandSchema
        
        # Create minimal config
        minimal_config = GoobitsConfigSchema(
            package_name="test-cli",
            command_name="test",
            display_name="Test CLI",
            description="A test CLI",
            cli=CLISchema(
                name="test",
                tagline="Test CLI tagline",  # Required field
                description="Test CLI",
                commands={"hello": CommandSchema(desc="Say hello")}
            )
        )
        
        print("✅ Minimal config created successfully")
        return minimal_config
        
    except Exception as e:
        print(f"❌ Failed to create minimal config: {e}")
        traceback.print_exc()
        return None

def test_ir_generation():
    """Test Intermediate Representation generation"""
    print("\n=== Testing IR Generation ===")
    engine, renderer = test_universal_engine_creation()
    config = test_minimal_config_processing()
    
    if not engine or not config:
        print("❌ Prerequisites failed")
        return None
        
    try:
        ir = engine.create_intermediate_representation(config, "test.yaml")
        print("✅ IR generated successfully")
        print(f"IR keys: {list(ir.keys())}")
        
        # Check specific IR structure
        if 'project' in ir:
            print(f"Project data: {ir['project']}")
        if 'cli' in ir:
            print(f"CLI commands: {ir['cli'].get('commands', {}).keys()}")
            
        return ir
        
    except Exception as e:
        print(f"❌ Failed to generate IR: {e}")
        traceback.print_exc()
        return None

def test_template_context():
    """Test template context generation"""
    print("\n=== Testing Template Context ===")
    engine, renderer = test_universal_engine_creation()
    ir = test_ir_generation()
    
    if not renderer or not ir:
        print("❌ Prerequisites failed")
        return None
        
    try:
        context = renderer.get_template_context(ir)
        print("✅ Template context generated successfully")
        print(f"Context keys: {list(context.keys())}")
        
        # Check for problematic fields
        for key in ['project', 'cli', 'installation', 'metadata']:
            if key in context:
                print(f"{key}: {type(context[key])}")
                if isinstance(context[key], dict):
                    print(f"  {key} keys: {list(context[key].keys())}")
                    
        return context
        
    except Exception as e:
        print(f"❌ Failed to generate template context: {e}")
        traceback.print_exc()
        return None

def test_component_rendering():
    """Test rendering a simple component"""
    print("\n=== Testing Component Rendering ===")
    engine, renderer = test_universal_engine_creation()
    context = test_template_context()
    
    if not renderer or not context:
        print("❌ Prerequisites failed")
        return
        
    try:
        # Simple test template
        test_template = """
# Test template for {{ language }}
# Project: {{ project.name }}
# Command: {{ project.command_name }}
"""
        
        result = renderer.render_component("test", test_template, context)
        print("✅ Component rendered successfully")
        print("Rendered content:")
        print(result)
        
    except Exception as e:
        print(f"❌ Failed to render component: {e}")
        traceback.print_exc()

def test_component_with_js_string():
    """Test rendering a component using js_string filter"""
    print("\n=== Testing Component with js_string Filter ===")
    engine, renderer = test_universal_engine_creation()
    context = test_template_context()
    
    if not renderer or not context:
        print("❌ Prerequisites failed")
        return
        
    try:
        # Template that uses js_string filter
        test_template = """
# Test template using js_string filter
description = "{{ project.description | js_string }}"
name = "{{ project.name | js_string }}"
"""
        
        result = renderer.render_component("test_js_string", test_template, context)
        print("✅ Component with js_string rendered successfully")
        print("Rendered content:")
        print(result)
        
    except Exception as e:
        print(f"❌ Failed to render component with js_string: {e}")
        traceback.print_exc()

def main():
    """Run all tests"""
    print("🔍 Python CLI Generation Runtime Debug Analysis")
    print("=" * 60)
    
    test_js_string_filter()
    test_universal_engine_creation()
    test_minimal_config_processing()
    test_ir_generation()
    test_template_context()
    test_component_rendering()
    test_component_with_js_string()
    
    print("\n" + "=" * 60)
    print("🏁 Debug analysis complete")

if __name__ == "__main__":
    main()