#!/usr/bin/env python3
"""
Debug script for template engine command hierarchy
"""
import sys
sys.path.insert(0, 'src')

from goobits_cli.schemas import GoobitsConfigSchema
from goobits_cli.universal.template_engine import UniversalTemplateEngine
import yaml

# Load the nested demo config
with open('/tmp/nested-demo/goobits.yaml', 'r') as f:
    config_data = yaml.safe_load(f)

print("=== YAML Config ===")
print(f"CLI commands type: {type(config_data.get('cli', {}).get('commands'))}")
print(f"CLI commands: {config_data.get('cli', {}).get('commands')}")

# Create schema
try:
    config = GoobitsConfigSchema(**config_data)
    print("\n=== Schema Creation Successful ===")
    
    # Create template engine and test IR building
    engine = UniversalTemplateEngine()
    
    print("\n=== Building Intermediate Representation ===")
    ir = engine._build_intermediate_representation(config)
    
    print(f"IR commands type: {type(ir['cli']['commands'])}")
    print(f"IR commands keys: {list(ir['cli']['commands'].keys())}")
    
    # Print first few commands
    for i, (cmd_name, cmd_data) in enumerate(ir['cli']['commands'].items()):
        if i >= 3:
            break
        print(f"  {cmd_name}: {type(cmd_data)} - {cmd_data.get('subcommands', 'no subcommands')}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()