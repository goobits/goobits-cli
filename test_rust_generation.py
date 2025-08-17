#!/usr/bin/env python3
"""
Test script to generate Rust CLI and examine the output and errors.
"""

import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from goobits_cli.schemas import GoobitsConfigSchema, CLISchema, CommandSchema
from goobits_cli.universal.template_engine import UniversalTemplateEngine
from goobits_cli.universal.renderers.rust_renderer import RustRenderer
from goobits_cli.universal.component_registry import ComponentRegistry

def main():
    print("🔧 Testing Rust CLI generation with Universal Template System")
    
    # Create a simple test configuration
    cli_config = CLISchema(
        name="test-cli",
        tagline="A test CLI for debugging",
        description="Testing universal templates",
        version="1.0.0",
        commands={
            "hello": CommandSchema(
                desc="Say hello",
                args=[],
                options=[]
            )
        }
    )
    
    config = GoobitsConfigSchema(
        package_name="test-cli",
        command_name="test-cli",
        display_name="Test CLI",
        description="A test CLI",
        cli=cli_config
    )
    
    print(f"✅ Created test configuration")
    
    # Test component registry
    print("\n🔍 Testing Component Registry...")
    registry = ComponentRegistry()
    print(f"Components directory: {registry.components_dir}")
    print(f"Components directory exists: {registry.components_dir.exists()}")
    
    # List available components
    available_components = registry.list_components()
    print(f"Available components: {available_components}")
    
    # Test each component
    for component_name in available_components:
        try:
            component_exists = registry.has_component(component_name)
            print(f"  - {component_name}: {'✅' if component_exists else '❌'}")
            if component_exists:
                template_content = registry.get_component(component_name)
                print(f"    Template length: {len(template_content)} chars")
        except Exception as e:
            print(f"    Error loading {component_name}: {e}")
    
    # Test Rust renderer
    print("\n🦀 Testing Rust Renderer...")
    try:
        rust_renderer = RustRenderer()
        print("✅ Rust renderer created")
        
        # Test template context generation
        ir = {"project": {"name": "test"}, "cli": {"commands": {}}}
        context = rust_renderer.get_template_context(ir)
        print(f"✅ Template context generated: {list(context.keys())}")
        
    except Exception as e:
        print(f"❌ Rust renderer error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Universal Template Engine
    print("\n🏗️  Testing Universal Template Engine...")
    try:
        engine = UniversalTemplateEngine()
        print("✅ Universal template engine created")
        
        # Register Rust renderer
        engine.register_renderer("rust", rust_renderer)
        print("✅ Rust renderer registered")
        
        # Test CLI generation
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            print(f"Output directory: {output_dir}")
            
            print("\n🚀 Generating CLI files...")
            try:
                generated_files = engine.generate_cli(config, "rust", output_dir)
                print(f"✅ Generated {len(generated_files)} files:")
                
                for file_path, content in generated_files.items():
                    print(f"  - {file_path} ({len(content)} chars)")
                    
                    # Show content of small files
                    if len(content) < 1000:
                        print(f"    Content preview:\n{content[:200]}...")
                    
                    # Check for obvious syntax errors in Rust files
                    if file_path.endswith('.rs'):
                        if 'fn on_' in content and '{{' in content:
                            print(f"    ⚠️  Template variables not replaced in {file_path}")
                        if 'use clap::' in content and 'anyhow::' in content:
                            print(f"    ✅ Rust imports look correct in {file_path}")
                
            except Exception as e:
                print(f"❌ CLI generation failed: {e}")
                import traceback
                traceback.print_exc()
    
    except Exception as e:
        print(f"❌ Universal template engine error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test completed")

if __name__ == "__main__":
    main()