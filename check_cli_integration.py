#!/usr/bin/env python3
"""
Check CLI integration with logger module.
"""

import os
import sys
import tempfile
import subprocess
import yaml

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

def check_main_cli_content():
    """Check what the main CLI file contains and why it doesn't use logger."""
    print("=== Checking Main CLI Content ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {
            'package_name': 'test-cli-logger',
            'command_name': 'testcli',
            'display_name': 'Test CLI Logger',
            'description': 'Test CLI logger integration',
            'language': 'python',
            'cli_output_path': f'{temp_dir}/cli.py',
            
            'python': {'minimum_version': '3.8', 'maximum_version': '3.13'},
            'installation': {'pypi_name': 'test-cli-logger'},
            'shell_integration': {'enabled': False, 'alias': 'testcli'},
            'validation': {'check_api_keys': False, 'check_disk_space': False},
            
            'cli': {
                'name': 'testcli',
                'tagline': 'Test CLI logger integration',
                'description': 'Test CLI with logger integration',
                'commands': {
                    'hello': {
                        'desc': 'Say hello with logging',
                        'args': [{'name': 'name', 'desc': 'Name to greet', 'type': 'string', 'required': True}],
                        'options': [{'name': 'verbose', 'short': 'v', 'desc': 'Enable verbose logging', 'type': 'flag'}]
                    }
                }
            }
        }
        
        config_file = os.path.join(temp_dir, 'goobits.yaml')
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        # Generate CLI
        build_cmd = [sys.executable, '-m', 'goobits_cli.main', 'build', config_file]
        result = subprocess.run(build_cmd, cwd=temp_dir, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Build failed: {result.stderr}")
            return
        
        # Read main CLI file
        cli_file = os.path.join(temp_dir, 'cli.py')
        with open(cli_file, 'r') as f:
            cli_content = f.read()
        
        print(f"Main CLI file size: {len(cli_content)} chars")
        
        # Read logger file
        logger_file = os.path.join(temp_dir, 'src/test_cli_logger/logger.py')
        if os.path.exists(logger_file):
            with open(logger_file, 'r') as f:
                logger_content = f.read()
            
            print(f"Logger file size: {len(logger_content)} chars")
            print("✅ Logger file exists with full functionality")
        else:
            print("❌ Logger file does NOT exist")
            return
        
        # Analyze CLI content for logger integration
        print("\n=== CLI Integration Analysis ===")
        
        # Check for logger imports
        import_checks = [
            ('from .logger import', 'Relative import from logger module'),
            ('import logger', 'Direct logger import'),
            ('from src.test_cli_logger.logger import', 'Absolute import from logger'),
            ('from test_cli_logger.logger import', 'Package import from logger')
        ]
        
        found_imports = []
        for import_stmt, description in import_checks:
            if import_stmt in cli_content:
                found_imports.append(description)
                print(f"  ✅ Found: {description}")
        
        if not found_imports:
            print("  ❌ NO logger imports found")
        
        # Check for logger usage
        usage_checks = [
            ('setup_logging()', 'Logger setup call'),
            ('get_logger(', 'Logger instance creation'),
            ('logger.info(', 'Logger usage'),
            ('logger.debug(', 'Debug logging'),
            ('logger.warning(', 'Warning logging'),
            ('logger.error(', 'Error logging'),
        ]
        
        found_usage = []
        for usage_stmt, description in usage_checks:
            if usage_stmt in cli_content:
                found_usage.append(description)
                print(f"  ✅ Found: {description}")
        
        if not found_usage:
            print("  ❌ NO logger usage found")
        
        # Show the structure of the CLI file
        print(f"\n=== CLI File Structure Analysis ===")
        lines = cli_content.split('\n')
        
        # Find import section
        import_section = []
        in_imports = False
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                in_imports = True
                import_section.append(f"{i+1}: {line}")
            elif in_imports and not line.strip().startswith(('import ', 'from ', '#')):
                if line.strip():  # Non-empty line that's not an import
                    break
                    
        print("Import section:")
        for imp_line in import_section[:10]:  # Show first 10 imports
            print(f"  {imp_line}")
        if len(import_section) > 10:
            print(f"  ... and {len(import_section) - 10} more imports")
        
        # Check if CLI has its own logging implementation
        if 'def setup_cli_logging():' in cli_content:
            print("\n✅ CLI has its own embedded logging implementation")
            # Find the function
            for i, line in enumerate(lines):
                if 'def setup_cli_logging():' in line:
                    print(f"  Found at line {i+1}")
                    # Show a few lines around it
                    start = max(0, i-2)
                    end = min(len(lines), i+10)
                    print("  Context:")
                    for j in range(start, end):
                        marker = "    >>>" if j == i else "       "
                        print(f"{marker} {j+1}: {lines[j]}")
                    break
        else:
            print("\n❌ CLI does NOT have embedded logging implementation")
        
        # Check what template was used
        if "Generated by: goobits-cli" in cli_content:
            print("\n✅ Generated by Goobits CLI framework")
            
            # Check template indicators
            template_indicators = [
                ("Universal Template System", "universal template"),
                ("cli_template.py.j2", "legacy template"),
                ("AUTO-GENERATED FILE", "template file"),
            ]
            
            for indicator, description in template_indicators:
                if indicator in cli_content:
                    print(f"  ✅ Uses {description}")
                    
        print(f"\n=== Summary ===")
        print(f"Logger file exists: ✅ YES ({len(logger_content)} chars)")
        print(f"CLI imports logger: {'✅ YES' if found_imports else '❌ NO'}")
        print(f"CLI uses logger: {'✅ YES' if found_usage else '❌ NO'}")
        
        if not found_imports and not found_usage:
            print("\n🚨 ISSUE IDENTIFIED:")
            print("   The logger module is generated correctly, but the CLI file")
            print("   is not importing or using it. This suggests a template integration issue.")

def main():
    check_main_cli_content()

if __name__ == "__main__":
    main()