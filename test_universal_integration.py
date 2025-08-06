#!/usr/bin/env python3
"""
Quick integration test for Universal Template System
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from goobits_cli.generators.python import PythonGenerator
from goobits_cli.generators.nodejs import NodeJSGenerator
from goobits_cli.generators.typescript import TypeScriptGenerator
from goobits_cli.generators.rust import RustGenerator
from goobits_cli.schemas import GoobitsConfigSchema


def test_generator_initialization():
    """Test that all generators can be initialized with universal templates flag."""
    print("Testing generator initialization...")
    
    generators = {
        "python": PythonGenerator,
        "nodejs": NodeJSGenerator,
        "typescript": TypeScriptGenerator,
        "rust": RustGenerator,
    }
    
    for name, GeneratorClass in generators.items():
        try:
            # Test legacy mode
            legacy_gen = GeneratorClass(use_universal_templates=False)
            assert not legacy_gen.use_universal_templates
            
            # Test universal mode
            universal_gen = GeneratorClass(use_universal_templates=True)
            assert universal_gen.use_universal_templates
            
            print(f"  ✅ {name} generator: OK")
            
        except Exception as e:
            print(f"  ❌ {name} generator: {e}")
            return False
    
    return True


def test_basic_generation():
    """Test basic generation with a simple config."""
    print("\nTesting basic generation...")
    
    # Create a simple test config
    config_data = {
        "package_name": "test-cli",
        "command_name": "testcli",
        "description": "A test CLI application",
        "language": "python",
        "cli": {
            "name": "testcli",
            "tagline": "Test CLI",
            "description": "A test command-line interface",
            "version": "1.0.0",
            "commands": {
                "hello": {
                    "desc": "Say hello",
                    "args": [
                        {"name": "name", "desc": "Name to greet", "required": True}
                    ]
                }
            }
        }
    }
    
    try:
        config = GoobitsConfigSchema(**config_data)
        
        # Test legacy generation
        legacy_gen = PythonGenerator(use_universal_templates=False)
        legacy_result = legacy_gen.generate(config, "test.yaml", "1.0.0")
        
        assert isinstance(legacy_result, str)
        assert len(legacy_result) > 0
        print("  ✅ Legacy generation: OK")
        
        # Test universal generation (may fall back to legacy)
        universal_gen = PythonGenerator(use_universal_templates=True)
        universal_result = universal_gen.generate(config, "test.yaml", "1.0.0")
        
        assert isinstance(universal_result, str)
        assert len(universal_result) > 0
        print("  ✅ Universal generation: OK")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_generation():
    """Test multi-file generation."""
    print("\nTesting multi-file generation...")
    
    config_data = {
        "package_name": "test-cli",
        "command_name": "testcli",
        "description": "A test CLI application",
        "language": "python",
        "cli": {
            "name": "testcli",
            "tagline": "Test CLI",
            "description": "A test command-line interface",
            "version": "1.0.0",
            "commands": {
                "hello": {
                    "desc": "Say hello"
                }
            }
        }
    }
    
    try:
        config = GoobitsConfigSchema(**config_data)
        
        # Test legacy multi-file generation
        legacy_gen = PythonGenerator(use_universal_templates=False)
        legacy_files = legacy_gen.generate_all_files(config, "test.yaml", "1.0.0")
        
        assert isinstance(legacy_files, dict)
        assert len(legacy_files) > 0
        print(f"  ✅ Legacy multi-file: {len(legacy_files)} files")
        
        # Test universal multi-file generation (may fall back)
        universal_gen = PythonGenerator(use_universal_templates=True)
        universal_files = universal_gen.generate_all_files(config, "test.yaml", "1.0.0")
        
        assert isinstance(universal_files, dict)
        print(f"  ✅ Universal multi-file: {len(universal_files)} files")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Multi-file generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_builder_integration():
    """Test that builder.py integration works."""
    print("\nTesting builder integration...")
    
    try:
        from goobits_cli.builder import Builder
        
        # Test legacy builder
        legacy_builder = Builder(use_universal_templates=False)
        assert not legacy_builder.generator.use_universal_templates
        print("  ✅ Legacy builder: OK")
        
        # Test universal builder
        universal_builder = Builder(use_universal_templates=True)
        assert universal_builder.generator.use_universal_templates
        print("  ✅ Universal builder: OK")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Builder integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests."""
    print("🧪 Universal Template System Integration Test")
    print("=" * 50)
    
    tests = [
        test_generator_initialization,
        test_basic_generation,
        test_file_generation,
        test_builder_integration,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Universal Template System integration successful.")
        return 0
    else:
        print("⚠️  Some tests failed. Review issues above.")
        return 1


if __name__ == "__main__":
    exit(main())