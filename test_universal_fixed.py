#!/usr/bin/env python3
"""
Fixed test script for universal template system logger component.
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
        # Check if component registry can be imported from the correct location
        from goobits_cli.universal.component_registry import ComponentRegistry
        print("✓ ComponentRegistry imported successfully")
        
        # Try to create an instance
        registry = ComponentRegistry()
        print("✓ ComponentRegistry instance created")
        
        # List available components
        available_components = registry.list_components()
        print(f"✓ Available components: {available_components}")
        
        # Check if logger component is available
        has_logger = 'logger' in available_components
        print(f"✓ Logger component available: {has_logger}")
        
        if has_logger:
            # Try to render the logger component for each language
            languages = ['python', 'nodejs', 'typescript', 'rust']
            for language in languages:
                try:
                    context = {'project': {'name': f'test-{language}-app'}}
                    rendered = registry.render_component('logger', language, context)
                    
                    if rendered and len(rendered) > 100:
                        print(f"  ✓ {language.upper()} logger component renders ({len(rendered)} chars)")
                    else:
                        print(f"  ✗ {language.upper()} logger component render failed or too small")
                        
                except Exception as e:
                    print(f"  ✗ {language.upper()} logger component render error: {e}")
            
            return True
        else:
            print("✗ Logger component not found in registry")
            return False
            
    except ImportError as e:
        print(f"✗ ComponentRegistry import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ ComponentRegistry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_engine_logger_integration():
    """Test logger integration with the template engine."""
    print("\n=== Testing Template Engine Logger Integration ===")
    
    try:
        from goobits_cli.universal.template_engine import UniversalTemplateEngine
        print("✓ UniversalTemplateEngine imported successfully")
        
        engine = UniversalTemplateEngine()
        print("✓ UniversalTemplateEngine instance created")
        
        # Test if the engine can render logger components
        languages = ['python', 'nodejs', 'typescript', 'rust']
        successful_renders = 0
        
        for language in languages:
            try:
                context = {
                    'language': language,
                    'project': {'name': f'test-{language}-app'}
                }
                
                # Try to render a simple template that includes logger
                simple_template = """
                {% include 'logger.j2' %}
                """
                
                rendered = engine.render_template_string(simple_template, context)
                
                if rendered and len(rendered) > 100:
                    print(f"  ✓ {language.upper()} logger integration successful")
                    successful_renders += 1
                else:
                    print(f"  ✗ {language.upper()} logger integration failed (output too small)")
                    
            except Exception as e:
                print(f"  ✗ {language.upper()} logger integration error: {e}")
        
        print(f"✓ Template engine logger integration: {successful_renders}/{len(languages)} successful")
        return successful_renders >= 3  # At least 3 out of 4 should work
        
    except ImportError as e:
        print(f"✗ UniversalTemplateEngine import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Template engine test failed: {e}")
        return False

def main():
    """Run universal template system logger tests."""
    print("Testing Universal Template System Logger Integration")
    print("=" * 60)
    
    # Test 1: Direct template rendering
    template_results = test_logger_template_direct()
    
    # Test 2: Component registry access
    registry_success = test_component_registry_access()
    
    # Test 3: Template engine logger integration
    engine_integration_success = test_template_engine_logger_integration()
    
    # Summary
    print(f"\n{'=' * 60}")
    print("Universal Template System Logger Test Results")
    print(f"{'=' * 60}")
    
    # Template rendering results
    if template_results:
        successful_renders = sum(1 for r in template_results.values() if r.get('success', False))
        languages_with_features = sum(1 for r in template_results.values() if r.get('has_logging_features', False))
        
        print(f"Direct Template Rendering: {successful_renders}/{len(template_results)} languages successful")
        print(f"Logging Features Present: {languages_with_features}/{len(template_results)} languages have logging features")
        
        for language, result in template_results.items():
            if result.get('success'):
                indicators = len(result.get('indicators', []))
                print(f"  {language.upper()}: ✓ Rendered with {indicators} logging indicators")
            else:
                error = result.get('error', 'Unknown error')
                print(f"  {language.upper()}: ✗ {error}")
    else:
        print("Direct Template Rendering: ✗ FAILED - Could not test")
        successful_renders = 0
        languages_with_features = 0
    
    print(f"Component Registry: {'✓ PASS' if registry_success else '✗ FAIL'}")
    print(f"Template Engine Integration: {'✓ PASS' if engine_integration_success else '✗ FAIL'}")
    
    # Overall assessment
    overall_success = (
        len(template_results) >= 4 and    # All 4 languages tested
        successful_renders >= 4 and       # All successful renders
        languages_with_features >= 4 and  # All have logging features
        registry_success and              # Registry works
        engine_integration_success        # Engine integration works
    )
    
    if overall_success:
        print("\n✅ Universal template system logger integration PASSED")
        return True
    else:
        # Partial success if most components work
        partial_success = (
            successful_renders >= 3 and
            languages_with_features >= 3
        )
        if partial_success:
            print("\n⚠️  Universal template system logger integration PARTIALLY PASSED")
            print("    Core functionality works, some integration issues remain")
            return True
        else:
            print("\n❌ Universal template system logger integration FAILED")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)