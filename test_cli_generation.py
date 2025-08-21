#!/usr/bin/env python3
"""
Test actual CLI generation and execution to trace runtime issues
"""
import sys
import traceback
import tempfile
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_full_cli_generation():
    """Test full CLI generation pipeline"""
    print("=== Testing Full CLI Generation ===")
    
    try:
        from goobits_cli.schemas import GoobitsConfigSchema, CLISchema, CommandSchema
        from goobits_cli.universal.template_engine import UniversalTemplateEngine
        from goobits_cli.universal.renderers.python_renderer import PythonRenderer
        
        # Create test config
        config = GoobitsConfigSchema(
            package_name="test-cli",
            command_name="test",
            display_name="Test CLI", 
            description="A test CLI",
            cli=CLISchema(
                name="test",
                tagline="Test CLI tagline",
                description="Test CLI",
                commands={"hello": CommandSchema(desc="Say hello")}
            )
        )
        
        # Set up universal engine
        engine = UniversalTemplateEngine()
        renderer = PythonRenderer()
        engine.register_renderer("python", renderer)
        
        # Generate CLI files
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            print(f"Generating files to: {output_dir}")
            generated_files = engine.generate_cli(
                config, "python", output_dir, 
                consolidate=False, config_filename="test.yaml"
            )
            
            print(f"Generated {len(generated_files)} files:")
            for file_path, content in generated_files.items():
                print(f"  - {file_path} ({len(content)} chars)")
                
                # Save files to disk for inspection
                file_obj = Path(file_path)
                if file_obj.is_absolute():
                    # Create directory structure
                    file_obj.parent.mkdir(parents=True, exist_ok=True)
                    file_obj.write_text(content)
                    print(f"    Saved to: {file_obj}")
                    
            return generated_files, output_dir
            
    except Exception as e:
        print(f"❌ CLI generation failed: {e}")
        traceback.print_exc()
        return None, None

def test_cli_execution():
    """Test executing the generated CLI"""
    print("\n=== Testing CLI Execution ===")
    
    generated_files, output_dir = test_full_cli_generation()
    if not generated_files:
        print("❌ No files to test")
        return
        
    # Find the main CLI file
    main_cli_file = None
    for file_path in generated_files.keys():
        if "cli.py" in file_path:
            main_cli_file = Path(file_path)
            break
            
    if not main_cli_file or not main_cli_file.exists():
        print("❌ Main CLI file not found")
        return
        
    print(f"Testing CLI file: {main_cli_file}")
    
    # Test basic syntax by importing
    try:
        # Add the directory to Python path for import
        cli_dir = main_cli_file.parent
        original_sys_path = sys.path.copy()
        sys.path.insert(0, str(cli_dir))
        
        # Try to import the CLI module
        module_name = main_cli_file.stem
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, main_cli_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print("✅ CLI module imported successfully")
            
            # Test if main function exists
            if hasattr(module, 'main'):
                print("✅ Main function found")
            else:
                print("❌ Main function not found")
                
        # Restore sys.path
        sys.path[:] = original_sys_path
        
    except Exception as e:
        print(f"❌ CLI import failed: {e}")
        traceback.print_exc()
        
    # Test CLI execution with subprocess
    try:
        print("Testing CLI with --help...")
        result = subprocess.run([
            sys.executable, str(main_cli_file), "--help"
        ], capture_output=True, text=True, timeout=10)
        
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
            
        if result.returncode == 0:
            print("✅ CLI --help executed successfully")
        else:
            print("❌ CLI --help failed")
            
    except subprocess.TimeoutExpired:
        print("❌ CLI execution timed out")
    except Exception as e:
        print(f"❌ CLI execution failed: {e}")

def test_argument_parsing():
    """Test argument parsing issues"""
    print("\n=== Testing Argument Parsing Issues ===")
    
    # Create config with various argument types
    try:
        from goobits_cli.schemas import GoobitsConfigSchema, CLISchema, CommandSchema, ArgumentSchema, OptionSchema
        
        config = GoobitsConfigSchema(
            package_name="test-args",
            command_name="testargs",
            display_name="Test Args CLI",
            description="Test argument parsing",
            cli=CLISchema(
                name="testargs",
                tagline="Test argument parsing",
                description="Test CLI for argument parsing",
                commands={
                    "process": CommandSchema(
                        desc="Process some data",
                        args=[
                            ArgumentSchema(name="input_file", desc="Input file path", required=True),
                            ArgumentSchema(name="output_file", desc="Output file path", required=False)
                        ],
                        options=[
                            OptionSchema(name="verbose", short="v", type="flag", desc="Verbose output"),
                            OptionSchema(name="format", short="f", type="str", desc="Output format", default="json"),
                            OptionSchema(name="count", short="c", type="int", desc="Number of items", default=10)
                        ]
                    )
                }
            )
        )
        
        from goobits_cli.universal.template_engine import UniversalTemplateEngine
        from goobits_cli.universal.renderers.python_renderer import PythonRenderer
        
        engine = UniversalTemplateEngine()
        renderer = PythonRenderer()
        engine.register_renderer("python", renderer)
        
        # Generate the CLI
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            generated_files = engine.generate_cli(
                config, "python", output_dir, 
                consolidate=False, config_filename="test-args.yaml"
            )
            
            # Find and examine the generated CLI
            for file_path, content in generated_files.items():
                if "cli.py" in file_path:
                    print(f"Generated CLI content (first 1000 chars):")
                    print(content[:1000])
                    print("...")
                    
                    # Check for specific patterns that might cause issues
                    issues = []
                    if "@click.argument(" not in content:
                        issues.append("No click.argument decorators found")
                    if "@click.option(" not in content:
                        issues.append("No click.option decorators found")
                    if "def process(" not in content:
                        issues.append("Process command function not found")
                        
                    if issues:
                        print("❌ Potential issues found:")
                        for issue in issues:
                            print(f"  - {issue}")
                    else:
                        print("✅ Basic CLI structure looks correct")
                        
                    break
                    
    except Exception as e:
        print(f"❌ Argument parsing test failed: {e}")
        traceback.print_exc()

def test_subcommand_structure():
    """Test subcommand generation"""
    print("\n=== Testing Subcommand Structure ===")
    
    try:
        from goobits_cli.schemas import GoobitsConfigSchema, CLISchema, CommandSchema
        
        # Create config with nested subcommands
        config = GoobitsConfigSchema(
            package_name="test-sub",
            command_name="testsub",
            display_name="Test Subcommands CLI",
            description="Test subcommand generation",
            cli=CLISchema(
                name="testsub",
                tagline="Test subcommands",
                description="Test CLI for subcommands",
                commands={
                    "database": CommandSchema(
                        desc="Database operations",
                        subcommands={
                            "migrate": CommandSchema(desc="Run database migrations"),
                            "seed": CommandSchema(desc="Seed database with sample data"),
                            "backup": CommandSchema(desc="Create database backup")
                        }
                    ),
                    "user": CommandSchema(
                        desc="User management",
                        subcommands={
                            "create": CommandSchema(desc="Create new user"),
                            "delete": CommandSchema(desc="Delete user"),
                            "list": CommandSchema(desc="List all users")
                        }
                    )
                }
            )
        )
        
        from goobits_cli.universal.template_engine import UniversalTemplateEngine
        from goobits_cli.universal.renderers.python_renderer import PythonRenderer
        
        engine = UniversalTemplateEngine()
        renderer = PythonRenderer()
        engine.register_renderer("python", renderer)
        
        # Generate and examine IR
        ir = engine.create_intermediate_representation(config, "test-sub.yaml")
        print("IR CLI structure:")
        print(f"Root command subcommands: {len(ir['cli']['root_command']['subcommands'])}")
        for cmd in ir['cli']['root_command']['subcommands']:
            print(f"  - {cmd['name']}: {len(cmd.get('subcommands', []))} subcommands")
            
        # Generate CLI
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            generated_files = engine.generate_cli(
                config, "python", output_dir, 
                consolidate=False, config_filename="test-sub.yaml"
            )
            
            for file_path, content in generated_files.items():
                if "cli.py" in file_path:
                    # Check for subcommand patterns
                    if "@main.group(" in content or ".add_command(" in content:
                        print("✅ Subcommand structure detected")
                    else:
                        print("❌ No subcommand structure found")
                        
                    # Count command definitions
                    cmd_count = content.count("def ")
                    print(f"Found {cmd_count} function definitions")
                    break
                    
    except Exception as e:
        print(f"❌ Subcommand test failed: {e}")
        traceback.print_exc()

def main():
    """Run all CLI generation tests"""
    print("🔍 Python CLI Generation Runtime Issues Analysis")
    print("=" * 60)
    
    test_full_cli_generation()
    test_cli_execution()
    test_argument_parsing()
    test_subcommand_structure()
    
    print("\n" + "=" * 60)
    print("🏁 CLI generation analysis complete")

if __name__ == "__main__":
    main()