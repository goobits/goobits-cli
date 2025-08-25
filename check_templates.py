#!/usr/bin/env python3
"""
Check what templates are actually available and being used.
"""

import os
import sys
from pathlib import Path

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

def check_python_templates():
    """Check Python template structure."""
    print("=== Python Templates ===")
    
    template_dir = Path('/workspace/src/goobits_cli/templates')
    print(f"Template directory: {template_dir}")
    print(f"Exists: {template_dir.exists()}")
    
    if template_dir.exists():
        python_files = list(template_dir.glob('*.py.j2'))
        print(f"Python template files: {[f.name for f in python_files]}")
        
        # Check main CLI template
        main_template = template_dir / 'cli.py.j2'
        if main_template.exists():
            with open(main_template, 'r') as f:
                content = f.read()
            
            print(f"\nMain CLI template size: {len(content)} chars")
            
            # Check for logger references
            logger_refs = [
                'logger', 'logging', 'setup_logging', 'get_logger', 
                'contextvars', 'structured'
            ]
            
            found_refs = []
            for ref in logger_refs:
                if ref in content:
                    found_refs.append(ref)
            
            print(f"Logger references in main template: {found_refs}")
            
            # Check if logger template is included
            if 'logger.py.j2' in content or 'logger.j2' in content or 'include' in content:
                print("✓ Template includes logger components")
            else:
                print("✗ Template does NOT include logger components")
        else:
            print("Main CLI template not found")

def check_universal_templates():
    """Check universal template structure."""
    print("\n=== Universal Templates ===")
    
    universal_dir = Path('/workspace/src/goobits_cli/universal/components')
    print(f"Universal components directory: {universal_dir}")
    print(f"Exists: {universal_dir.exists()}")
    
    if universal_dir.exists():
        logger_template = universal_dir / 'logger.j2'
        print(f"Universal logger template exists: {logger_template.exists()}")
        
        if logger_template.exists():
            with open(logger_template, 'r') as f:
                content = f.read()
            
            print(f"Universal logger template size: {len(content)} chars")
            
            # Check language support
            languages = ['python', 'nodejs', 'typescript', 'rust']
            for lang in languages:
                if f"language == '{lang}'" in content:
                    print(f"  ✓ {lang.upper()} supported")
                else:
                    print(f"  ✗ {lang.upper()} not found")

def check_template_engine():
    """Check how templates are loaded and used."""
    print("\n=== Template Engine ===")
    
    try:
        from goobits_cli.builder import Builder
        print("✓ Builder imported successfully")
        
        # Check if Builder has logging integration
        builder = Builder()
        print("✓ Builder instance created")
        
        # Check available methods
        methods = [method for method in dir(builder) if not method.startswith('_')]
        print(f"Builder methods: {methods}")
        
    except Exception as e:
        print(f"✗ Builder check failed: {e}")
    
    try:
        from goobits_cli.generators.python import PythonGenerator
        print("✓ PythonGenerator imported successfully")
        
        # Check if it has logger support
        generator = PythonGenerator()
        methods = [method for method in dir(generator) if 'log' in method.lower()]
        print(f"Logger-related methods in PythonGenerator: {methods}")
        
    except Exception as e:
        print(f"✗ PythonGenerator check failed: {e}")

def check_builder_integration():
    """Check how the builder integrates logging."""
    print("\n=== Builder Integration ===")
    
    # Check the main builder file
    builder_file = Path('/workspace/src/goobits_cli/builder.py')
    if builder_file.exists():
        with open(builder_file, 'r') as f:
            content = f.read()
        
        print(f"Builder.py size: {len(content)} chars")
        
        # Check for logger integration
        if 'logger' in content.lower():
            print("✓ Builder has logger references")
            
            # Find logger-related lines
            lines = content.split('\n')
            logger_lines = [i for i, line in enumerate(lines) if 'logger' in line.lower()]
            
            print("Logger-related lines:")
            for line_num in logger_lines[:5]:  # Show first 5 matches
                print(f"  {line_num + 1}: {lines[line_num].strip()}")
        else:
            print("✗ Builder has no logger references")
    else:
        print("Builder.py not found")

def main():
    """Check template availability and usage."""
    print("Checking Goobits CLI Template Structure")
    print("=" * 50)
    
    check_python_templates()
    check_universal_templates() 
    check_template_engine()
    check_builder_integration()

if __name__ == "__main__":
    main()