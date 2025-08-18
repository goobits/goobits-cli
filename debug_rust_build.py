#!/usr/bin/env python3

import sys
import traceback
from pathlib import Path

# Add the source path
sys.path.insert(0, '/workspace/src')

from goobits_cli.main import load_goobits_config
from goobits_cli.generators.rust import RustGenerator

def test_rust_generation():
    try:
        print("Loading configuration...")
        config_path = Path('/workspace/test_rust_cli.yaml')
        config = load_goobits_config(config_path)
        print(f"✅ Config loaded: {config.language}")
        print(f"✅ CLI exists: {config.cli is not None}")
        
        if config.cli and hasattr(config.cli, 'commands'):
            print(f"✅ Commands: {list(config.cli.commands.keys())}")
        
        print("\nCreating Rust generator...")
        generator = RustGenerator(use_universal_templates=True)
        print("✅ Generator created")
        
        print("\nGenerating all files...")
        all_files = generator.generate_all_files(config, config_path.name, "1.0.0")
        print(f"✅ Generated {len(all_files)} files")
        
        print("\nGenerated files:")
        for file_path, content in all_files.items():
            print(f"  📄 {file_path}: {len(content)} characters")
            if file_path.endswith('.rs'):
                print(f"      First 200 chars: {content[:200]}")
        
        # Test compilation by writing to temp directory
        output_dir = Path('/workspace/test_rust_output')
        output_dir.mkdir(exist_ok=True)
        
        print(f"\nWriting files to {output_dir}...")
        for file_path, content in all_files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            print(f"  ✅ Wrote {full_path}")
        
        print("\n🎉 Success! Files generated and written.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_rust_generation()