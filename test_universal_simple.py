#!/usr/bin/env python3
"""
Simplified test script for universal template system logger component.
"""

import os
import sys

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

def test_logger_template_direct():
    """Test the universal logger template directly."""
    print("=== Testing Universal Logger Template Direct Rendering ===")
    
    try:
        from jinja2 import Template
        
        # Read the universal logger template
        with open('/workspace/src/goobits_cli/universal/components/logger.j2', 'r') as f:
            template_content = f.read()
        
        template = Template(template_content)
        
        # Test each language
        languages = ['python', 'nodejs', 'typescript', 'rust']
        results = {}
        
        for language in languages:
            print(f"\nTesting {language.upper()} logger template rendering...")
            
            try:
                # Minimal context for rendering
                context = {
                    'language': language,
                    'project': {
                        'name': f'test-{language}-app'
                    }
                }
                
                rendered = template.render(**context)
                
                if rendered and len(rendered) > 100:
                    # Check for language-specific indicators
                    indicators = {
                        'python': ['import logging', 'setup_logging', 'contextvars'],
                        'nodejs': ['winston', 'AsyncLocalStorage', 'setupLogging'],
                        'typescript': ['winston', 'AsyncLocalStorage', 'LogLevel', 'export function'],
                        'rust': ['serde_json', 'setup_logging', 'thread_local', 'pub fn']
                    }
                    
                    found_indicators = []
                    for indicator in indicators.get(language, []):
                        if indicator in rendered:
                            found_indicators.append(indicator)
                    
                    results[language] = {
                        'success': True,
                        'size': len(rendered),
                        'indicators': found_indicators,
                        'has_logging_features': len(found_indicators) > 0
                    }
                    
                    print(f"  ✓ Rendered successfully ({len(rendered)} chars)")
                    print(f"  ✓ Found indicators: {found_indicators}")
                    
                else:
                    results[language] = {
                        'success': False,
                        'error': 'Template rendered but output too small or empty'
                    }
                    print(f"  ✗ Template output too small or empty")
                
            except Exception as e:
                results[language] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ✗ Rendering failed: {e}")
        
        return results
        
    except Exception as e:
        print(f"✗ Template loading failed: {e}")
        return {}

def test_component_registry_access():
    """Test accessing the component registry."""
    print("\n=== Testing Component Registry Access ===")
    
    try:
        # Check if ComponentRegistry can be imported
        from goobits_cli.universal.components.registry import ComponentRegistry
        print("✓ ComponentRegistry imported successfully")
        
        # Try to create an instance
        registry = ComponentRegistry()
        print("✓ ComponentRegistry instance created")
        
        # Check if logger component is available
        has_logger = registry.has_component('logger')
        print(f"✓ Logger component available: {has_logger}")
        
        if has_logger:
            # Try to get the logger component
            logger_component = registry.get_component('logger')
            print(f"✓ Logger component retrieved: {type(logger_component)}")
            
            return True
        else:
            print("✗ Logger component not found in registry")
            return False
            
    except ImportError as e:
        print(f"✗ ComponentRegistry import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ ComponentRegistry test failed: {e}")
        return False

def test_template_engine_import():
    """Test importing the universal template engine."""
    print("\n=== Testing Universal Template Engine Import ===")
    
    try:
        from goobits_cli.universal.template_engine import UniversalTemplateEngine
        print("✓ UniversalTemplateEngine imported successfully")
        
        engine = UniversalTemplateEngine()
        print("✓ UniversalTemplateEngine instance created")
        
        return True
        
    except ImportError as e:
        print(f"✗ UniversalTemplateEngine import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ UniversalTemplateEngine test failed: {e}")
        return False

def main():
    """Run simplified universal template system tests."""
    print("Testing Universal Template System Logger Components")
    print("=" * 60)
    
    # Test 1: Direct template rendering
    template_results = test_logger_template_direct()
    
    # Test 2: Component registry access
    registry_success = test_component_registry_access()
    
    # Test 3: Template engine import
    engine_success = test_template_engine_import()
    
    # Summary
    print(f"\n{'=' * 60}")
    print("Universal Template System Test Results")
    print(f"{'=' * 60}")
    
    # Template rendering results
    if template_results:
        successful_renders = sum(1 for r in template_results.values() if r.get('success', False))
        languages_with_features = sum(1 for r in template_results.values() if r.get('has_logging_features', False))
        
        print(f"Template Rendering: {successful_renders}/{len(template_results)} languages successful")
        print(f"Logging Features: {languages_with_features}/{len(template_results)} languages have logging features")
        
        for language, result in template_results.items():
            if result.get('success'):
                indicators = len(result.get('indicators', []))
                print(f"  {language.upper()}: ✓ Rendered with {indicators} logging indicators")
            else:
                error = result.get('error', 'Unknown error')
                print(f"  {language.upper()}: ✗ {error}")
    else:
        print("Template Rendering: ✗ FAILED - Could not test")
        successful_renders = 0
        languages_with_features = 0
    
    print(f"Component Registry: {'✓ PASS' if registry_success else '✗ FAIL'}")
    print(f"Template Engine: {'✓ PASS' if engine_success else '✗ FAIL'}")
    
    # Overall assessment
    overall_success = (
        len(template_results) >= 4 and  # All 4 languages tested
        successful_renders >= 3 and     # At least 3 successful renders
        languages_with_features >= 3 and # At least 3 with logging features
        registry_success and            # Registry works
        engine_success                  # Engine imports
    )
    
    if overall_success:
        print("\n✅ Universal template system logger components PASSED")
        return True
    else:
        print("\n❌ Universal template system logger components FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)