#!/usr/bin/env python3
"""Debug what features are actually being passed to the template."""

import sys
sys.path.insert(0, '/workspace/src')

from goobits_cli.universal.template_engine import UniversalTemplateEngine
from goobits_cli.schemas import GoobitsConfigSchema
import yaml

def test_template_context(config_file):
    print(f"\n=== Testing Template Context for {config_file} ===")
    
    # Load config
    with open(config_file, 'r') as f:
        config_data = yaml.safe_load(f)
    config = GoobitsConfigSchema.model_validate(config_data)
    
    # Create engine and get IR
    engine = UniversalTemplateEngine()
    
    # Create IR (includes feature_requirements)
    ir = engine.create_intermediate_representation(config, config_file)
    print("IR feature_requirements:", ir.get('feature_requirements'))
    
    # Get Python renderer
    from goobits_cli.universal.renderers.python_renderer import PythonRenderer
    renderer = PythonRenderer()
    
    # Get template context 
    context = renderer.get_template_context(ir)
    print("Template context feature_requirements:", context.get('feature_requirements'))
    
    # Check if rich_interface is False specifically
    fr = context.get('feature_requirements', {})
    print(f"rich_interface in context: {fr.get('rich_interface')}")
    
    return context

# Test minimal
minimal_context = test_template_context('/workspace/examples/basic-demos/minimal-python-example.yaml')

# Test complex  
complex_context = test_template_context('/workspace/examples/basic-demos/python-example.yaml')