#!/usr/bin/env python3
"""
Analyze template syntax issues and missing components.
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

def main():
    print("🔧 Analyzing template syntax issues and missing components")
    
    # Create a simple test configuration with more fields
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
    
    print("✅ Created test configuration")
    
    # Test Rust renderer
    print("\n🦀 Testing Rust Renderer...")
    rust_renderer = RustRenderer()
    
    # Create intermediate representation
    engine = UniversalTemplateEngine()
    ir = engine._build_intermediate_representation(config)
    print(f"✅ Created IR with keys: {list(ir.keys())}")
    
    # Test template context
    context = rust_renderer.get_template_context(ir)
    print(f"✅ Created context with keys: {list(context.keys())}")
    
    # Check for missing tagline in CLI
    if 'cli' in ir and 'tagline' in ir['cli']:
        print(f"✅ CLI tagline found: {ir['cli']['tagline']}")
    else:
        print("❌ CLI tagline missing from IR")
        print(f"   CLI keys: {list(ir['cli'].keys()) if 'cli' in ir else 'No CLI'}")
    
    # Test output structure
    output_structure = rust_renderer.get_output_structure(ir)
    print(f"\n📋 Expected output structure: {list(output_structure.keys())}")
    
    # Check which components exist
    registry = engine.component_registry
    registry.load_components()
    
    print(f"\n🔍 Checking component availability:")
    for component_name in output_structure.keys():
        exists = registry.has_component(component_name)
        print(f"  - {component_name}: {'✅' if exists else '❌'}")
        
        if exists:
            try:
                content = registry.get_component(component_name)
                print(f"    Template length: {len(content)} chars")
                
                # Check for template syntax issues
                if '{{{{ ' in content or ' }}}}' in content:
                    print(f"    ⚠️  Found escaped template syntax (likely error)")
                
                # Look for incomplete Jinja blocks
                open_blocks = content.count('{{')
                close_blocks = content.count('}}')
                if open_blocks != close_blocks:
                    print(f"    ⚠️  Unmatched template brackets: {open_blocks} open, {close_blocks} close")
                
                # Check for Rust-specific syntax issues in template
                if component_name in ['hook_system', 'command_handler']:
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if 'fn on_' in line and line.count('}}') > 1:
                            print(f"    ⚠️  Line {i}: Multiple template closures: {line.strip()}")
                        if 'pub fn' in line and '{{' in line and '}}' in line and line.count('}}') >= 2:
                            print(f"    ⚠️  Line {i}: Suspicious template nesting: {line.strip()}")
                
            except Exception as e:
                print(f"    ❌ Error reading component: {e}")
    
    # Test individual component rendering
    print(f"\n🧪 Testing individual component rendering:")
    
    for component_name in ['command_handler', 'hook_system']:
        if registry.has_component(component_name):
            try:
                template_content = registry.get_component(component_name)
                rendered_content = rust_renderer.render_component(
                    component_name, template_content, context
                )
                
                print(f"\n  ✅ {component_name} rendered successfully ({len(rendered_content)} chars)")
                
                # Check for template variables left unresolved
                if '{{' in rendered_content or '}}' in rendered_content:
                    lines = rendered_content.split('\n')
                    problem_lines = []
                    for i, line in enumerate(lines, 1):
                        if '{{' in line or '}}' in line:
                            problem_lines.append(f"Line {i}: {line.strip()}")
                    
                    print(f"    ⚠️  Unresolved template variables in {component_name}:")
                    for line in problem_lines[:5]:  # Show first 5 issues
                        print(f"      {line}")
                    if len(problem_lines) > 5:
                        print(f"      ... and {len(problem_lines) - 5} more")
                
                # Check for Rust syntax issues
                if component_name == 'hook_system':
                    if 'pub fn on_' in rendered_content:
                        # Look for function signature issues
                        lines = rendered_content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if 'pub fn on_' in line:
                                # Check if function has proper signature
                                if 'Result<' not in line and '->' not in line:
                                    if i < len(lines) - 1:
                                        next_line = lines[i].strip()
                                        if not next_line.startswith('fn ') and '-> Result<' not in next_line:
                                            print(f"    ⚠️  Line {i}: Function may be missing return type: {line.strip()}")
                
            except Exception as e:
                print(f"  ❌ Error rendering {component_name}: {e}")
                import traceback
                traceback.print_exc()
    
    print("\n✅ Analysis completed")

if __name__ == "__main__":
    main()