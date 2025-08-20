#!/usr/bin/env python3
"""
Demonstration of the Installation Test System

This script shows how the installation test infrastructure works
by running a simplified version of the tests.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from tests.install.package_manager_utils import (
    validate_installation_environment, PackageManagerRegistry
)
from tests.install.test_configs import TestConfigTemplates, TestScenarioRunner
from tests.install.test_installation_workflows import CLITestHelper

def main():
    print("🚀 Installation Test System Demo")
    print("=" * 50)
    
    # 1. Environment Validation
    print("📋 Step 1: Environment Validation")
    env_info = validate_installation_environment()
    
    print(f"   Python Version: {env_info['python']['version']}")
    print(f"   Node.js Version: {env_info['nodejs'].get('version', 'Not available')}")
    print(f"   Rust Version: {env_info['rust'].get('version', 'Not available')}")
    
    print("\n   Package Manager Availability:")
    available_managers = env_info["available_managers"]
    for manager, is_available in available_managers.items():
        status = "✅" if is_available else "❌"
        print(f"     {status} {manager}")
    
    print()
    
    # 2. Test Configuration Generation
    print("📋 Step 2: Test Configuration Generation")
    
    languages = ["python", "nodejs", "typescript", "rust"]
    scenarios = ["minimal", "complex"]
    
    for language in languages:
        for scenario in scenarios:
            try:
                config = TestConfigTemplates.get_template_for_scenario(scenario, language)
                print(f"   ✅ {language}/{scenario}: {config.package_name}")
            except Exception as e:
                print(f"   ❌ {language}/{scenario}: {e}")
    
    print()
    
    # 3. Test Matrix Generation
    print("📋 Step 3: Test Matrix Generation")
    
    full_matrix = TestScenarioRunner.get_test_matrix()
    critical_matrix = TestScenarioRunner.get_critical_test_matrix()
    
    print(f"   Full test matrix: {len(full_matrix)} test cases")
    print(f"   Critical test matrix: {len(critical_matrix)} test cases")
    
    print(f"\n   Sample test cases:")
    for i, test_case in enumerate(critical_matrix[:4]):
        print(f"     {i+1}. {test_case['language']}/{test_case['scenario']} ({test_case['test_id']})")
    
    print()
    
    # 4. CLI Generation Demo (without installation)
    print("📋 Step 4: CLI Generation Demo")
    
    import tempfile
    
    # Test Python CLI generation
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = TestConfigTemplates.minimal_config("python", "demo-python-cli")
            generated_files = CLITestHelper.generate_cli(config, temp_dir)
            
            print(f"   ✅ Python CLI generated:")
            for file_type, file_path in generated_files.items():
                file_size = Path(file_path).stat().st_size
                print(f"     - {file_type}: {file_size} bytes")
    except Exception as e:
        print(f"   ❌ Python CLI generation failed: {e}")
    
    # Test Node.js CLI generation
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = TestConfigTemplates.minimal_config("nodejs", "demo-nodejs-cli")
            generated_files = CLITestHelper.generate_cli(config, temp_dir)
            
            print(f"   ✅ Node.js CLI generated:")
            for file_type, file_path in generated_files.items():
                file_size = Path(file_path).stat().st_size
                print(f"     - {file_type}: {file_size} bytes")
    except Exception as e:
        print(f"   ❌ Node.js CLI generation failed: {e}")
    
    print()
    
    # 5. Package Manager Capability Check
    print("📋 Step 5: Package Manager Capability Check")
    
    capabilities = {
        "pip": ["Install editable packages", "List installed packages", "Uninstall packages"],
        "npm": ["Install dependencies", "Link globally", "List global packages"],
        "cargo": ["Build projects", "Install from path", "List installed binaries"],
        "yarn": ["Install dependencies", "Global add", "List global packages"],
        "pipx": ["Install isolated apps", "List installed apps", "Uninstall apps"]
    }
    
    for manager, features in capabilities.items():
        manager_class = PackageManagerRegistry.get_manager(manager)
        is_available = manager_class.is_available()
        status = "✅" if is_available else "❌"
        
        print(f"   {status} {manager}:")
        if is_available:
            for feature in features:
                print(f"     - {feature}")
        else:
            print(f"     - Not available on this system")
    
    print()
    
    # 6. Summary and Recommendations
    print("📋 Step 6: Summary and Recommendations")
    
    available_count = sum(available_managers.values())
    total_managers = len(available_managers)
    
    print(f"   Available package managers: {available_count}/{total_managers}")
    
    if available_count >= 3:
        print("   🎉 Excellent! Most package managers are available.")
        print("   💡 You can run comprehensive installation tests.")
    elif available_count >= 2:
        print("   👍 Good! Several package managers are available.")
        print("   💡 You can run tests for multiple languages.")
    else:
        print("   ⚠️  Limited package manager availability.")
        print("   💡 Consider installing additional package managers for full testing.")
    
    print("\n   To run actual installation tests:")
    print("     python test_runner.py")
    print("     python -m pytest test_installation_workflows.py -v")
    
    print()
    print("=" * 50)
    print("✅ Installation Test System Demo Complete!")


if __name__ == "__main__":
    main()