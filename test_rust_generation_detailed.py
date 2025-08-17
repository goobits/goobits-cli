#!/usr/bin/env python3
"""
Test script to generate Rust CLI and examine the output and errors in detail.
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
    
    # Test Universal Template Engine
    print("\n🏗️  Testing Universal Template Engine...")
    try:
        engine = UniversalTemplateEngine()
        rust_renderer = RustRenderer()
        engine.register_renderer("rust", rust_renderer)
        
        # Test CLI generation
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            print(f"Output directory: {output_dir}")
            
            print("\n🚀 Generating CLI files...")
            try:
                generated_files = engine.generate_cli(config, "rust", output_dir)
                print(f"✅ Generated {len(generated_files)} files:")
                
                # Write files to disk for testing
                for file_path, content in generated_files.items():
                    file_obj = Path(file_path)
                    file_obj.parent.mkdir(parents=True, exist_ok=True)
                    file_obj.write_text(content)
                    
                    print(f"\n📄 File: {file_path}")
                    print(f"   Length: {len(content)} chars")
                    
                    # Show first 20 lines for debugging
                    lines = content.split('\n')
                    print("   First 20 lines:")
                    for i, line in enumerate(lines[:20], 1):
                        print(f"   {i:2d}: {line}")
                    
                    if file_path.endswith('.rs'):
                        # Check for template issues
                        if '{{' in content or '}}' in content:
                            print(f"   ⚠️  Unresolved template variables in {file_path}")
                            # Find lines with template variables
                            for i, line in enumerate(lines, 1):
                                if '{{' in line or '}}' in line:
                                    print(f"     Line {i}: {line.strip()}")
                        
                        # Check for syntax issues
                        syntax_issues = []
                        for i, line in enumerate(lines, 1):
                            if 'fn on_' in line and not line.strip().endswith('{'):
                                syntax_issues.append(f"Line {i}: Function definition might be incomplete: {line.strip()}")
                            if '&ArgMatches' in line and 'Result<' not in line:
                                syntax_issues.append(f"Line {i}: Function missing return type: {line.strip()}")
                            if line.strip().startswith('mod ') and not line.strip().endswith(';'):
                                syntax_issues.append(f"Line {i}: Module declaration missing semicolon: {line.strip()}")
                        
                        if syntax_issues:
                            print(f"   ⚠️  Potential syntax issues in {file_path}:")
                            for issue in syntax_issues:
                                print(f"     {issue}")
                
                # Test Rust compilation if cargo is available
                try:
                    print(f"\n🔨 Testing Rust compilation...")
                    # Create Cargo.toml manually since it's missing
                    cargo_toml = """[package]
name = "test-cli"
version = "1.0.0"
edition = "2021"

[[bin]]
name = "test-cli"
path = "src/main.rs"

[dependencies]
clap = { version = "4.0", features = ["derive"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
anyhow = "1.0"
thiserror = "1.0"
tokio = { version = "1.0", features = ["full"] }
"""
                    (output_dir / "Cargo.toml").write_text(cargo_toml)
                    
                    # Run cargo check
                    import subprocess
                    result = subprocess.run(
                        ["cargo", "check"],
                        cwd=output_dir,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        print("   ✅ Rust compilation check passed!")
                    else:
                        print("   ❌ Rust compilation errors:")
                        print(f"   STDOUT: {result.stdout}")
                        print(f"   STDERR: {result.stderr}")
                    
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    print("   ⚠️  Cargo not available, skipping compilation test")
                except Exception as e:
                    print(f"   ⚠️  Compilation test failed: {e}")
                
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