#!/usr/bin/env python3
"""
Simple Demonstration of the Installation Test System

This script shows the basic functionality without heavy dependencies.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from tests.integration.package_manager_utils import (
    validate_installation_environment,
    PackageManagerRegistry,
)
from tests.integration.test_configs import TestConfigTemplates, TestScenarioRunner


def main():
    print("🚀 Installation Test System - Simple Demo")
    print("=" * 60)

    # 1. Environment Validation
    print("📋 Step 1: Environment Validation")
    env_info = validate_installation_environment()

    print(f"   Python Version: {env_info['python']['version']}")

    nodejs_version = env_info["nodejs"].get("version")
    if nodejs_version:
        print(f"   Node.js Version: {nodejs_version}")
    else:
        print("   Node.js: Not available")

    rust_version = env_info["rust"].get("version")
    if rust_version:
        print(f"   Rust Version: {rust_version}")
    else:
        print("   Rust: Not available")

    print("\n   📦 Package Manager Availability:")
    available_managers = env_info["available_managers"]
    for manager, is_available in available_managers.items():
        status = "✅" if is_available else "❌"
        print(f"     {status} {manager}")

    print()

    # 2. Test Configuration Generation
    print("📋 Step 2: Test Configuration Generation")

    languages = ["python", "nodejs", "typescript", "rust"]
    scenarios = ["minimal", "complex", "dependency_heavy", "edge_case"]

    successful_configs = 0
    total_configs = 0

    for language in languages:
        for scenario in scenarios:
            total_configs += 1
            try:
                config = TestConfigTemplates.get_template_for_scenario(
                    scenario, language
                )
                print(f"   ✅ {language}/{scenario}: {config.package_name}")
                successful_configs += 1
            except Exception as e:
                print(f"   ❌ {language}/{scenario}: {str(e)[:60]}...")

    print(
        f"\n   Generated {successful_configs}/{total_configs} configurations successfully"
    )
    print()

    # 3. Test Matrix Generation
    print("📋 Step 3: Test Matrix Generation")

    full_matrix = TestScenarioRunner.get_test_matrix()
    critical_matrix = TestScenarioRunner.get_critical_test_matrix()

    print(f"   Full test matrix: {len(full_matrix)} test cases")
    print(f"   Critical test matrix: {len(critical_matrix)} test cases")

    print("\n   Sample critical test cases:")
    for i, test_case in enumerate(critical_matrix[:6]):
        print(f"     {i+1}. {test_case['language']}/{test_case['scenario']}")

    print()

    # 4. Package Manager Capabilities
    print("📋 Step 4: Package Manager Capabilities")

    capabilities = {
        "pip": ["Install packages", "Editable installs", "Uninstall packages"],
        "npm": ["Install dependencies", "Global linking", "Script running"],
        "cargo": ["Build Rust projects", "Install binaries", "Dependency management"],
        "yarn": ["Package management", "Global installs", "Workspace support"],
        "pipx": ["Isolated app installs", "Virtual environments", "CLI management"],
    }

    for manager, features in capabilities.items():
        manager_class = PackageManagerRegistry.get_manager(manager)
        is_available = manager_class.is_available()
        status = "✅" if is_available else "❌"

        print(f"   {status} {manager}:")
        if is_available:
            for feature in features[:2]:  # Show only first 2 features
                print(f"     - {feature}")
            if len(features) > 2:
                print(f"     - ... and {len(features)-2} more")
        else:
            print("     - Not available (install with package manager)")

    print()

    # 5. Language Support Matrix
    print("📋 Step 5: Language Support Matrix")

    language_managers = {
        "python": ["pip", "pipx"],
        "nodejs": ["npm", "yarn"],
        "typescript": ["npm", "yarn"],
        "rust": ["cargo"],
    }

    for language, managers in language_managers.items():
        available_for_lang = sum(
            1 for m in managers if available_managers.get(m, False)
        )
        total_for_lang = len(managers)

        if available_for_lang == total_for_lang:
            status = "✅ Full"
        elif available_for_lang > 0:
            status = "⚡ Partial"
        else:
            status = "❌ None"

        print(
            f"   {status} {language}: {available_for_lang}/{total_for_lang} package managers"
        )

        for manager in managers:
            manager_status = "✓" if available_managers.get(manager, False) else "✗"
            print(f"     {manager_status} {manager}")

    print()

    # 6. Testing Readiness Assessment
    print("📋 Step 6: Testing Readiness Assessment")

    available_count = sum(available_managers.values())
    total_managers = len(available_managers)
    readiness_score = available_count / total_managers

    print(
        f"   Package Manager Availability: {available_count}/{total_managers} ({readiness_score:.1%})"
    )

    if readiness_score >= 0.8:
        print("   🎉 EXCELLENT: Ready for comprehensive testing!")
        recommendation = "Run full test suite with all languages and scenarios"
    elif readiness_score >= 0.6:
        print("   👍 GOOD: Ready for substantial testing")
        recommendation = "Run tests for available package managers"
    elif readiness_score >= 0.4:
        print("   ⚡ MODERATE: Limited testing possible")
        recommendation = "Install additional package managers for better coverage"
    else:
        print("   ⚠️  LIMITED: Minimal testing possible")
        recommendation = "Install package managers before running tests"

    print(f"   💡 Recommendation: {recommendation}")
    print()

    # 7. Next Steps
    print("📋 Step 7: Next Steps")
    print("   🧪 To run installation tests:")
    print("     cd src/tests/integration")

    if available_managers.get("pip", False):
        print(
            "     python3 -c \"from test_installation_workflows import *; print('Python tests ready')\""
        )

    if available_managers.get("npm", False):
        print(
            "     python3 -c \"from package_manager_utils import NpmManager; print('Node.js tests ready')\""
        )

    print("\n   📊 To run test infrastructure validation:")
    print("     python3 test_infrastructure_validation.py")

    print("\n   📈 To run comprehensive test suite:")
    print("     python3 test_runner.py --languages python nodejs")

    print()
    print("=" * 60)
    print("✅ Simple Demo Complete!")

    return {
        "available_managers": available_count,
        "total_managers": total_managers,
        "readiness_score": readiness_score,
        "successful_configs": successful_configs,
        "total_configs": total_configs,
    }


if __name__ == "__main__":
    results = main()

    # Exit with status code based on readiness
    if results["readiness_score"] >= 0.5:
        sys.exit(0)  # Good to go
    else:
        sys.exit(1)  # Need more setup
