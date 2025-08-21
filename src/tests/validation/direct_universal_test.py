#!/usr/bin/env python3
"""
Direct test of Universal Template System to verify functionality
"""

import sys
import yaml
from pathlib import Path
from pydantic import ValidationError

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from goobits_cli.schemas import GoobitsConfigSchema
from goobits_cli.universal.template_engine import UniversalTemplateEngine
from goobits_cli.universal.renderers.python_renderer import PythonRenderer
from goobits_cli.universal.renderers.nodejs_renderer import NodeJSRenderer  
from goobits_cli.universal.renderers.typescript_renderer import TypeScriptRenderer

def test_universal_templates():
    """Test the Universal Template System with all languages"""
    
    # Load test configuration
    config_path = Path("test_universal_validation.yaml")
    assert config_path.exists(), f"Error: {config_path} not found"
        
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    
    try:
        config = GoobitsConfigSchema(**data)
    except ValidationError as e:
        assert False, f"Config validation error: {e}"
    
    print(f"✅ Loaded configuration: {config.display_name}")
    
    # Create universal template engine
    engine = UniversalTemplateEngine()
    
    # Test each language
    languages = [
        ("python", PythonRenderer()),
        ("nodejs", NodeJSRenderer()),
        ("typescript", TypeScriptRenderer())
    ]
    
    all_tests_passed = True
    
    for language_name, renderer in languages:
        print(f"\n🧪 Testing {language_name} renderer...")
        
        try:
            # Register renderer
            engine.register_renderer(language_name, renderer)
            
            # Test configuration with this language  
            test_config = config.model_copy()
            test_config.language = language_name
            
            # Generate CLI files
            output_dir = Path(f"test_universal_{language_name}_output")
            output_dir.mkdir(exist_ok=True)
            
            generated_files = engine.generate_cli(test_config, language_name, output_dir)
            
            print(f"✅ Generated {len(generated_files)} files for {language_name}")
            for file_path, content in generated_files.items():
                print(f"   📄 {file_path} ({len(content):,} chars)")
                
                # Write the file for inspection
                file_path_obj = Path(file_path)
                file_path_obj.parent.mkdir(parents=True, exist_ok=True)
                file_path_obj.write_text(content)
            
        except Exception as e:
            print(f"❌ Error testing {language_name}: {e}")
            import traceback
            traceback.print_exc()
            all_tests_passed = False
    
    assert all_tests_passed, "Some universal template tests failed"

if __name__ == "__main__":
    print("🚀 Testing Universal Template System directly...\n")
    
    try:
        test_universal_templates()
        print("\n🎉 All universal template tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ {e}")
        sys.exit(1)