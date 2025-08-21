#!/usr/bin/env python3
"""
Detailed analysis of generated CLI files to find specific issues
"""
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def examine_generated_cli():
    """Examine generated CLI in detail"""
    print("=== Detailed CLI Generation Analysis ===")
    
    try:
        from goobits_cli.schemas import GoobitsConfigSchema, CLISchema, CommandSchema, ArgumentSchema, OptionSchema
        from goobits_cli.universal.template_engine import UniversalTemplateEngine
        from goobits_cli.universal.renderers.python_renderer import PythonRenderer
        
        # Create comprehensive test config
        config = GoobitsConfigSchema(
            package_name="test-cli",
            command_name="mycli",
            display_name="My Test CLI",
            description="A comprehensive test CLI",
            cli=CLISchema(
                name="mycli",
                tagline="A powerful test CLI tool",
                description="Test CLI with comprehensive features",
                commands={
                    "hello": CommandSchema(
                        desc="Say hello to someone",
                        args=[
                            ArgumentSchema(name="name", desc="Person to greet", required=True)
                        ],
                        options=[
                            OptionSchema(name="greeting", short="g", type="str", desc="Greeting to use", default="Hello"),
                            OptionSchema(name="loud", short="l", type="flag", desc="Use loud greeting")
                        ]
                    ),
                    "process": CommandSchema(
                        desc="Process data files",
                        args=[
                            ArgumentSchema(name="input_file", desc="Input file path", required=True),
                            ArgumentSchema(name="output_file", desc="Output file path", required=False)
                        ],
                        options=[
                            OptionSchema(name="format", short="f", type="str", desc="Output format", default="json"),
                            OptionSchema(name="verbose", short="v", type="flag", desc="Verbose mode")
                        ]
                    ),
                    "config": CommandSchema(
                        desc="Configuration management",
                        subcommands={
                            "get": CommandSchema(desc="Get configuration value"),
                            "set": CommandSchema(desc="Set configuration value"),
                            "list": CommandSchema(desc="List all configuration")
                        }
                    )
                }
            )
        )
        
        # Set up universal engine
        engine = UniversalTemplateEngine()
        renderer = PythonRenderer()
        engine.register_renderer("python", renderer)
        
        # First, check the IR
        print("\n--- Examining Intermediate Representation ---")
        ir = engine.create_intermediate_representation(config, "test.yaml")
        
        print(f"CLI commands in IR: {list(ir['cli']['commands'].keys())}")
        print(f"Root subcommands: {len(ir['cli']['root_command']['subcommands'])}")
        
        for cmd in ir['cli']['root_command']['subcommands']:
            print(f"Command: {cmd['name']}")
            print(f"  Description: {cmd.get('description', 'N/A')}")
            print(f"  Arguments: {len(cmd.get('arguments', []))}")
            print(f"  Options: {len(cmd.get('options', []))}")
            print(f"  Subcommands: {len(cmd.get('subcommands', []))}")
            if cmd.get('subcommands'):
                for subcmd in cmd['subcommands']:
                    print(f"    - {subcmd['name']}: {subcmd.get('description', 'N/A')}")
        
        # Generate CLI and examine the results
        print("\n--- Generating CLI Files ---")
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            generated_files = engine.generate_cli(
                config, "python", output_dir, 
                consolidate=False, config_filename="test.yaml"
            )
            
            print(f"Generated {len(generated_files)} files")
            
            # Examine each file
            for file_path, content in generated_files.items():
                print(f"\n--- File: {file_path} ---")
                print(f"Size: {len(content)} characters")
                
                if file_path.endswith("cli.py"):
                    print("\n--- CLI Structure Analysis ---")
                    
                    # Check for decorators and function definitions
                    decorators = {
                        "@click.command": content.count("@click.command"),
                        "@click.group": content.count("@click.group"),
                        "@click.argument": content.count("@click.argument"),
                        "@click.option": content.count("@click.option"),
                        "@main.command": content.count("@main.command"),
                        "@main.group": content.count("@main.group"),
                    }
                    
                    print("Decorator counts:")
                    for decorator, count in decorators.items():
                        if count > 0:
                            print(f"  {decorator}: {count}")
                    
                    # Look for function definitions
                    import re
                    func_defs = re.findall(r'def (\w+)\(', content)
                    print(f"\nFunction definitions found: {len(func_defs)}")
                    for func in func_defs:
                        print(f"  - {func}")
                    
                    # Check for specific command patterns
                    command_patterns = {
                        "hello command": "def hello(" in content,
                        "process command": "def process(" in content,
                        "config command": "def config(" in content,
                        "subcommand group": "@main.group" in content or ".add_command" in content,
                        "click decorators": "@click." in content,
                        "rich-click": "rich_click" in content,
                    }
                    
                    print("\nCommand patterns found:")
                    for pattern, found in command_patterns.items():
                        status = "✅" if found else "❌"
                        print(f"  {status} {pattern}")
                    
                    # Look for potential issues
                    issues = []
                    if "@click.argument(" not in content and "ArgumentSchema" in str(config.model_dump()):
                        issues.append("Arguments defined in config but no @click.argument found")
                    if "@click.option(" not in content and "OptionSchema" in str(config.model_dump()):
                        issues.append("Options defined in config but no @click.option found")
                    if "subcommands" in str(config.model_dump()) and "@main.group" not in content:
                        issues.append("Subcommands defined but no @main.group found")
                    
                    if issues:
                        print("\n❌ Potential issues:")
                        for issue in issues:
                            print(f"  - {issue}")
                    else:
                        print("\n✅ No obvious issues detected")
                    
                    # Show a sample of the generated content
                    print(f"\n--- Sample Content (first 500 chars) ---")
                    print(content[:500])
                    print("...")
                    
                    # Show command section
                    if "@main.command" in content:
                        start_idx = content.find("@main.command")
                        if start_idx != -1:
                            sample = content[start_idx:start_idx+800]
                            print(f"\n--- Command Definition Sample ---")
                            print(sample)
                            print("...")
                    
                elif file_path.endswith("pyproject.toml"):
                    print("--- pyproject.toml Content ---")
                    print(content[:300])
                    print("...")
                
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

def test_template_context_issues():
    """Test template context and identify issues"""
    print("\n=== Template Context Analysis ===")
    
    try:
        from goobits_cli.schemas import GoobitsConfigSchema, CLISchema, CommandSchema, ArgumentSchema, OptionSchema
        from goobits_cli.universal.template_engine import UniversalTemplateEngine
        from goobits_cli.universal.renderers.python_renderer import PythonRenderer
        
        config = GoobitsConfigSchema(
            package_name="test-context",
            command_name="testctx",
            display_name="Test Context CLI",
            description="Test template context",
            cli=CLISchema(
                name="testctx",
                tagline="Test context",
                description="Test CLI",
                commands={
                    "test": CommandSchema(
                        desc="Test command",
                        args=[ArgumentSchema(name="arg1", desc="Test argument", required=True)],
                        options=[OptionSchema(name="opt1", short="o", type="str", desc="Test option")]
                    )
                }
            )
        )
        
        engine = UniversalTemplateEngine()
        renderer = PythonRenderer()
        engine.register_renderer("python", renderer)
        
        # Generate IR and context
        ir = engine.create_intermediate_representation(config, "test.yaml")
        context = renderer.get_template_context(ir)
        
        print("Template context analysis:")
        print(f"Context keys: {list(context.keys())}")
        
        # Examine CLI structure in context
        cli_context = context.get('cli', {})
        print(f"\nCLI context keys: {list(cli_context.keys())}")
        
        root_cmd = cli_context.get('root_command', {})
        print(f"Root command keys: {list(root_cmd.keys())}")
        print(f"Root subcommands: {len(root_cmd.get('subcommands', []))}")
        
        commands = cli_context.get('commands', {})
        print(f"Commands: {list(commands.keys())}")
        
        for cmd_name, cmd_data in commands.items():
            print(f"\nCommand '{cmd_name}':")
            print(f"  Type: {type(cmd_data)}")
            if isinstance(cmd_data, dict):
                print(f"  Keys: {list(cmd_data.keys())}")
                print(f"  Arguments: {len(cmd_data.get('arguments', []))}")
                print(f"  Options: {len(cmd_data.get('options', []))}")
                
                # Check argument structure
                for i, arg in enumerate(cmd_data.get('arguments', [])):
                    print(f"    Arg {i}: {arg.get('name')} ({arg.get('type', 'unknown')})")
                    
                # Check option structure  
                for i, opt in enumerate(cmd_data.get('options', [])):
                    print(f"    Opt {i}: {opt.get('name')} ({opt.get('type', 'unknown')})")
        
        # Test filter functionality
        print(f"\nTesting custom filters:")
        filters = renderer.get_custom_filters()
        print(f"Available filters: {list(filters.keys())}")
        
        # Test specific filters
        test_cases = {
            'snake_case': ['hello-world', 'CamelCase', 'mixed_case-string'],
            'python_type': ['str', 'int', 'flag', 'boolean'],
            'click_option': [{'name': 'test', 'type': 'str', 'description': 'Test option'}]
        }
        
        for filter_name, test_inputs in test_cases.items():
            if filter_name in filters:
                filter_func = filters[filter_name]
                print(f"\nTesting {filter_name} filter:")
                for test_input in test_inputs:
                    try:
                        result = filter_func(test_input)
                        print(f"  {test_input} -> {result}")
                    except Exception as e:
                        print(f"  {test_input} -> ERROR: {e}")
        
    except Exception as e:
        print(f"❌ Template context analysis failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run detailed analysis"""
    print("🔍 Detailed Python CLI Generation Analysis")
    print("=" * 60)
    
    examine_generated_cli()
    test_template_context_issues()
    
    print("\n" + "=" * 60)
    print("🏁 Detailed analysis complete")

if __name__ == "__main__":
    main()