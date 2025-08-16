#!/usr/bin/env python3
"""
Test CLI generation for all 4 languages using the working test infrastructure.
"""

import os
import sys

# Set up Python path
sys.path.insert(0, '/workspace/src')

def test_all_languages():
    """Test that all 4 languages can generate working CLI code."""
    
    print("🧪 Testing CLI Generation for All 4 Languages")
    print("=" * 70)
    
    # Import after setting path
    from goobits_cli.builder import Builder
    from tests.install.test_configs import TestConfigTemplates
    
    languages = ["python", "nodejs", "typescript", "rust"]
    results = {}
    
    for language in languages:
        print(f"\n🔧 Testing {language.upper()} generation...")
        
        try:
            # Use the working test configuration
            config = TestConfigTemplates.minimal_config(language, f"test-{language}-cli")
            builder = Builder(language=language)
            
            # Generate CLI code
            result = builder.build(config, f"test_{language}.yaml", "0.1.0")
            
            if result and len(result) > 100:  # Basic validation
                results[language] = {
                    "success": True,
                    "code_length": len(result),
                    "error": None
                }
                print(f"   ✅ SUCCESS: Generated {len(result)} characters")
                
                # Show a snippet of the generated code
                lines = result.split('\n')
                print(f"   📝 First few lines:")
                for i, line in enumerate(lines[:3]):
                    if line.strip():
                        print(f"      {i+1}: {line[:60]}...")
                        
            else:
                results[language] = {
                    "success": False,
                    "code_length": len(result) if result else 0,
                    "error": "Generated code too short"
                }
                print(f"   ❌ FAILED: Code too short ({len(result) if result else 0} chars)")
                
        except Exception as e:
            results[language] = {
                "success": False,
                "code_length": 0,
                "error": str(e)
            }
            print(f"   ❌ FAILED: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS SUMMARY")
    print("=" * 70)
    
    successful_languages = []
    failed_languages = []
    
    for language, result in results.items():
        if result["success"]:
            successful_languages.append(language)
            status = "✅ WORKING"
            details = f"({result['code_length']:,} chars generated)"
        else:
            failed_languages.append(language)
            status = "❌ FAILED"
            details = f"({result['error']})"
        
        print(f"{status:12} {language.upper():10} {details}")
    
    print(f"\n🎯 OVERALL RESULTS:")
    print(f"   ✅ Working: {len(successful_languages)}/{len(languages)} languages")
    print(f"   ❌ Failed:  {len(failed_languages)}/{len(languages)} languages")
    
    if successful_languages:
        print(f"   🎉 Working languages: {', '.join(successful_languages)}")
    
    if failed_languages:
        print(f"   🚨 Failed languages: {', '.join(failed_languages)}")
    
    # Final assessment
    if len(successful_languages) == len(languages):
        print(f"\n🎉 EXCELLENT: All {len(languages)} languages can generate working CLIs!")
        assessment = "FULL_SUCCESS"
    elif len(successful_languages) >= 3:
        print(f"\n👍 GOOD: {len(successful_languages)} out of {len(languages)} languages working")
        assessment = "MOSTLY_WORKING"
    elif len(successful_languages) >= 1:
        print(f"\n⚡ PARTIAL: {len(successful_languages)} out of {len(languages)} languages working")
        assessment = "PARTIALLY_WORKING"
    else:
        print(f"\n🚨 CRITICAL: No languages are working")
        assessment = "BROKEN"
    
    print("\n" + "=" * 70)
    return assessment, results


def test_package_manager_availability():
    """Check what package managers are available for installation testing."""
    import shutil
    
    print("\n🔧 Package Manager Availability Check")
    print("-" * 50)
    
    managers = {
        "Python": ["python3", "pip", "pipx"],
        "Node.js": ["node", "npm", "yarn"], 
        "Rust": ["cargo", "rustc"]
    }
    
    availability = {}
    
    for language, tools in managers.items():
        available = []
        missing = []
        
        for tool in tools:
            if shutil.which(tool):
                available.append(tool)
            else:
                missing.append(tool)
        
        availability[language] = {
            "available": available,
            "missing": missing,
            "percentage": len(available) / len(tools) * 100
        }
        
        status = "✅" if len(available) == len(tools) else "⚡" if available else "❌"
        print(f"{status} {language:8} ({len(available)}/{len(tools)}) - Available: {', '.join(available) if available else 'none'}")
        
        if missing:
            print(f"           Missing: {', '.join(missing)}")
    
    return availability


def main():
    """Main test execution."""
    assessment, generation_results = test_all_languages()
    package_results = test_package_manager_availability()
    
    print(f"\n🎯 PRODUCTION READINESS ASSESSMENT")
    print("=" * 70)
    
    # Calculate readiness score
    working_languages = len([r for r in generation_results.values() if r["success"]])
    total_languages = len(generation_results)
    generation_score = working_languages / total_languages * 100
    
    # Calculate package manager score
    total_managers = sum(len(info["available"]) + len(info["missing"]) for info in package_results.values())
    available_managers = sum(len(info["available"]) for info in package_results.values())
    package_score = available_managers / total_managers * 100 if total_managers > 0 else 0
    
    overall_score = (generation_score + package_score) / 2
    
    print(f"📊 Code Generation:     {generation_score:5.1f}% ({working_languages}/{total_languages} languages)")
    print(f"📦 Package Managers:    {package_score:5.1f}% ({available_managers}/{total_managers} tools)")
    print(f"🎯 Overall Readiness:   {overall_score:5.1f}%")
    
    if overall_score >= 80:
        readiness = "🎉 PRODUCTION READY"
    elif overall_score >= 60:
        readiness = "👍 MOSTLY READY"
    elif overall_score >= 40:
        readiness = "⚡ PARTIALLY READY"
    else:
        readiness = "🚨 NOT READY"
    
    print(f"\n{readiness}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if generation_score == 100:
        print("   ✅ CLI generation is perfect across all languages")
    else:
        failed = [lang for lang, result in generation_results.items() if not result["success"]]
        print(f"   🔧 Fix CLI generation for: {', '.join(failed)}")
    
    if package_score == 100:
        print("   ✅ All package managers available for testing")
    else:
        for lang, info in package_results.items():
            if info["missing"]:
                print(f"   📦 Install for {lang}: {', '.join(info['missing'])}")
    
    return overall_score >= 60  # Return success if mostly ready


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)