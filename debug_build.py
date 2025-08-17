#!/usr/bin/env python3
"""Debug script to test universal template generation"""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from goobits_cli.generators.python import PythonGenerator
from goobits_cli.main import load_goobits_config

try:
    # Load the config
    config_path = Path("goobits.yaml")
    config = load_goobits_config(config_path)
    print(f"✅ Config loaded: {config.package_name}")
    
    # Create generator with universal templates
    generator = PythonGenerator(use_universal_templates=True)
    print(f"✅ Generator created: universal_templates={generator.use_universal_templates}")
    
    # Try to generate
    print("🔄 Generating CLI...")
    result = generator.generate(config, "goobits.yaml", "2.0.0-beta.4")
    print(f"✅ Generation completed, result length: {len(result)}")
    
    # Check if version function is in the result
    if "get_version()" in result:
        print("✅ get_version() function call found in generated code")
    else:
        print("❌ get_version() function call NOT found")
        
    if "version=get_version()" in result:
        print("✅ Dynamic version call found")
    else:
        print("❌ Dynamic version call NOT found")
        
    # Check for legacy fallback indicators
    if "Auto-generated from" in result and len(result) < 1000:
        print("⚠️  Appears to be using legacy fallback (short output)")
    else:
        print("✅ Appears to be using full universal template system")
        
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()