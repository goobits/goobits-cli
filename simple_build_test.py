#!/usr/bin/env python3
"""
Simple test to verify that CLI generation works for all 4 languages.
This test uses the actual Builder like the real CLI does.
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from goobits_cli.builder import Builder
from goobits_cli.schemas import GoobitsConfigSchema


def test_language_generation(language: str) -> bool:
    """Test that we can generate code for a specific language."""
    print(f"  Testing {language} generation...")
    
    try:
        # Create minimal config using the working test config format
        config_data = {
            "package_name": f"test-{language}",
            "command_name": f"test-{language}",
            "display_name": f"Test {language.title()} CLI",
            "description": f"Test CLI for {language}",
            "language": language,
            "version": "0.1.0",
            "author": "Test Author",
            "email": "test@example.com",
            "license": "MIT",
            "homepage": "https://github.com/test/test-cli",
            "repository": "https://github.com/test/test-cli",
            "keywords": ["test", language],
            "installation": {
                "pypi_name": f"test-{language}",
                "development_path": "."
            },
            "python": {
                "minimum_version": "3.8",
                "maximum_version": "3.13"
            },
            "dependencies": {
                "required": [],
                "optional": []
            },
            "shell_integration": {
                "enabled": False,
                "alias": f"test-{language}"
            },
            "validation": {
                "check_api_keys": False,
                "check_disk_space": False,
                "minimum_disk_space_mb": 1
            },
            "messages": {
                "install_success": "Installation completed successfully!",
                "install_dev_success": "Development installation completed successfully!",
                "upgrade_success": "Upgrade completed successfully!",
                "uninstall_success": "Uninstall completed successfully!"
            },
            "cli": {
                "name": f"Test{language.title()}CLI",
                "version": "0.1.0",
                "tagline": f"Test {language} CLI",
                "commands": {
                    "hello": {
                        "desc": "Say hello"
                    }
                }
            }
        }
        
        # Create configuration schema
        config = GoobitsConfigSchema(**config_data)
        
        # Create builder with specific language
        builder = Builder(language=language)
        
        # Generate CLI code
        cli_code = builder.build(config, "test_config.yaml", config.version)
        
        if cli_code and len(cli_code) > 100:  # Basic validation
            print(f"    ✅ {language} generation successful ({len(cli_code)} characters)")
            return True
        else:
            print(f"    ❌ {language} generation failed - code too short")
            return False
            
    except Exception as e:
        print(f"    ❌ {language} generation failed: {e}")
        return False


def main():
    """Test CLI generation for all languages."""
    print("🧪 Testing CLI Generation for All Languages")
    print("=" * 60)
    
    languages = ["python", "nodejs", "typescript", "rust"]
    results = {}
    
    for language in languages:
        results[language] = test_language_generation(language)
    
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    
    successful = 0
    for language, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {language.upper()}")
        if success:
            successful += 1
    
    print(f"\n🎯 OVERALL: {successful}/{len(languages)} languages passed")
    
    if successful == len(languages):
        print("🎉 SUCCESS: All languages can generate CLI code!")
        return True
    elif successful > 0:
        print("⚡ PARTIAL: Some languages working")
        return False
    else:
        print("🚨 FAILURE: No languages working")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)