#!/usr/bin/env python3
"""Debug script to analyze feature requirements detection."""

import sys
sys.path.insert(0, '/workspace/src')

from goobits_cli.universal.template_engine import UniversalTemplateEngine
from goobits_cli.schemas import GoobitsConfigSchema
import yaml

def test_feature_detection(config_file):
    print(f"\n=== Testing {config_file} ===")
    
    # Load and parse config
    with open(config_file, 'r') as f:
        config_data = yaml.safe_load(f)
    
    config = GoobitsConfigSchema.model_validate(config_data)
    
    # Create template engine and analyze features
    engine = UniversalTemplateEngine()
    features = engine.analyze_feature_requirements(config, config_file)
    
    print("Detected features:")
    for feature, enabled in features.items():
        status = "✓" if enabled else "✗"
        print(f"  {status} {feature}: {enabled}")
    
    # Show specific CLI config
    cli_config = config_data.get('cli', {})
    print(f"\nCLI config analysis:")
    print(f"  Commands: {len(cli_config.get('commands', {}))}")
    print(f"  Colors setting: {cli_config.get('colors', 'not specified')}")
    
    return features

# Test both configurations
simple_features = test_feature_detection('/workspace/examples/basic-demos/minimal-python-example.yaml')
complex_features = test_feature_detection('/workspace/examples/basic-demos/python-example.yaml')

# Compare
print(f"\n=== Comparison ===")
print(f"Simple rich_interface: {simple_features['rich_interface']}")
print(f"Complex rich_interface: {complex_features['rich_interface']}")