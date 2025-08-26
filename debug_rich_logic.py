#!/usr/bin/env python3
"""Debug the rich formatting logic step by step."""

import sys
sys.path.insert(0, '/workspace/src')

from goobits_cli.universal.template_engine import UniversalTemplateEngine
from goobits_cli.schemas import GoobitsConfigSchema
import yaml

def debug_rich_formatting_logic(config_file):
    print(f"\n=== Debugging Rich Formatting Logic for {config_file} ===")
    
    # Load and parse config
    with open(config_file, 'r') as f:
        config_data = yaml.safe_load(f)
    
    config = GoobitsConfigSchema.model_validate(config_data)
    cli_config = config_data.get('cli', {})
    
    print(f"CLI config: {cli_config}")
    print(f"Commands: {cli_config.get('commands', {})}")
    print(f"Number of commands: {len(cli_config.get('commands', {}))}")
    print(f"Colors setting: {cli_config.get('colors', 'default=True')}")
    
    # Create template engine and manually call the method
    engine = UniversalTemplateEngine()
    
    # Call the internal method directly  
    result = engine._needs_rich_formatting(cli_config, config_data)
    print(f"_needs_rich_formatting result: {result}")
    
    # Step through the logic
    commands = cli_config.get('commands', {})
    print(f"\nStep-by-step analysis:")
    print(f"1. Number of commands: {len(commands)}")
    
    if len(commands) <= 2:
        print("2. Commands <= 2, checking for complex features...")
        for cmd_name, cmd in commands.items():
            cmd_dict = cmd if isinstance(cmd, dict) else {}
            desc = cmd_dict.get('desc', cmd_dict.get('description', ''))
            options = cmd_dict.get('options', [])
            
            print(f"   Command '{cmd_name}':")
            print(f"     Description: '{desc}'")
            print(f"     Options count: {len(options)}")
            print(f"     Options: {options}")
            
            # Check rich markup
            rich_markers = ['[bold]', '[italic]', '[green]', '[red]', '[yellow]', '[blue]', '[dim]', '[bright]', 'table', 'progress', 'spinner']
            has_rich_markup = any(marker in str(desc).lower() for marker in rich_markers)
            print(f"     Has rich markup: {has_rich_markup}")
            
            if len(options) > 5:
                print(f"     Options > 5: True (would trigger rich)")
    
    # Check colors setting
    colors_setting = cli_config.get('colors', True)
    print(f"3. Colors setting: {colors_setting}")
    if colors_setting == False:
        print("   Colors explicitly disabled -> return False")
    
    print(f"4. Final check: len(commands) > 2 = {len(commands) > 2}")
    
    return result

# Test both
minimal_result = debug_rich_formatting_logic('/workspace/examples/basic-demos/minimal-python-example.yaml')
complex_result = debug_rich_formatting_logic('/workspace/examples/basic-demos/python-example.yaml')