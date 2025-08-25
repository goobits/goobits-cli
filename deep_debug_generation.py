#!/usr/bin/env python3
"""
Deep debug to trace the exact generation flow and identify the disconnect.
"""

import tempfile
from pathlib import Path
from src.goobits_cli.generators.python import PythonGenerator
from src.goobits_cli.schemas import GoobitsConfigSchema

def create_test_config():
    return GoobitsConfigSchema(
        package_name="deep_debug_cli",
        command_name="deep-debug",
        display_name="Deep Debug CLI",
        description="CLI for deep debugging",
        version="1.0.0",
        language="python",
        cli={
            "name": "deep-debug",
            "description": "Deep debug CLI",
            "tagline": "CLI for deep debugging",
            "options": [],
            "commands": {}
        },
        features={
            "interactive_mode": {
                "enabled": True,
                "repl": True,
                "smart_completion": True
            }
        },
        installation={
            "pypi_name": "deep-debug-cli",
            "development_path": "."
        }
    )

def main():
    print("🔍 Deep Debug: Tracing Generation Flow...")
    
    config = create_test_config()
    generator = PythonGenerator()
    
    # Step 1: Check what the renderer expects to generate
    print("\n1️⃣ Python Renderer Output Structure:")
    if hasattr(generator, 'python_renderer'):
        ir = generator.universal_engine._build_intermediate_representation(config, "debug.yaml")
        output_structure = generator.python_renderer.get_output_structure(ir)
        
        print("   Output Structure Requested:")
        for component, path in output_structure.items():
            has_template = generator.universal_engine.component_registry.has_component(component)
            status = "✅" if has_template else "❌"
            print(f"     {status} {component} -> {path}")
            
        print(f"\n   Features in IR:")
        features = ir.get("features", {})
        interactive = features.get("interactive_mode", {})
        for key, value in interactive.items():
            print(f"     {key}: {value}")
    
    # Step 2: Test actual generation to see what Universal Engine does
    print("\n2️⃣ Universal Template Engine Generation:")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Call the Universal Engine directly
            generated_files = generator.universal_engine.generate_cli(
                config=config,
                language="python", 
                output_dir=temp_path,
                config_filename="debug.yaml"
            )
            
            print(f"   Universal Engine Reports: {len(generated_files)} files")
            print("   Files Actually Generated:")
            for path, content in generated_files.items():
                rel_path = Path(path).relative_to(temp_path) if temp_path in Path(path).parents else Path(path)
                print(f"     ✅ {rel_path} ({len(content)} chars)")
                
    except Exception as e:
        print(f"   ❌ Universal Engine failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: Test Python Generator's wrapper
    print("\n3️⃣ Python Generator Wrapper:")
    
    try:
        result = generator.generate_all_files(config, "debug.yaml")
        
        print(f"   Python Generator Reports: {len(result)} files")
        print("   Files Returned by Generator:")
        for path, content in result.items():
            print(f"     ✅ {path} ({len(content)} chars)")
            
    except Exception as e:
        print(f"   ❌ Python Generator failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Deep Debug Complete!")

if __name__ == "__main__":
    main()