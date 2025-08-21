#!/usr/bin/env python3
"""Test the intermediate representation generation."""
from goobits_cli.universal.template_engine import UniversalTemplateEngine
from goobits_cli.schemas import GoobitsConfigSchema

# Create test config
config_data = {
    'package_name': 'test_cli',
    'command_name': 'test_cli',
    'display_name': 'Test CLI',
    'description': 'Test CLI',
    'cli': {
        'name': 'test_cli',
        'tagline': 'Test',
        'commands': {
            'hello': {
                'desc': 'Say hello',
                'args': [
                    {'name': 'name', 'desc': 'Name', 'required': True}
                ],
                'options': [
                    {'name': 'greeting', 'desc': 'Greeting', 'default': 'Hello'}
                ]
            }
        }
    }
}

config = GoobitsConfigSchema(**config_data)

# Create IR
engine = UniversalTemplateEngine()
ir = engine.create_intermediate_representation(config, 'test.yaml')

# Check command hierarchy
if 'cli' in ir and 'command_hierarchy' in ir['cli']:
    hierarchy = ir['cli']['command_hierarchy']
    print("Command hierarchy:")
    print(f"  Groups: {len(hierarchy.get('groups', []))}")
    print(f"  Leaves: {len(hierarchy.get('leaves', []))}")
    print(f"  Flat commands: {len(hierarchy.get('flat_commands', []))}")
    
    if hierarchy.get('flat_commands'):
        print("\nFlat commands:")
        for cmd in hierarchy['flat_commands']:
            print(f"  - {cmd['name']}: click_decorator={cmd.get('click_decorator', 'NONE')}")
            print(f"    path: {cmd.get('path', [])}")
            print(f"    is_group: {cmd.get('is_group', False)}")
            print(f"    hook_name: {cmd.get('hook_name', 'NONE')}")
else:
    print("No command hierarchy found in IR!")
    print(f"IR keys: {list(ir.keys())}")
    if 'cli' in ir:
        print(f"CLI keys: {list(ir['cli'].keys())}")