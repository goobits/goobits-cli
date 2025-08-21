#!/usr/bin/env python3
"""
Debug script to test each language individually.
"""
import sys
sys.path.insert(0, '/workspace/src')

from tests.integration.test_cross_language import EndToEndIntegrationTester

def main():
    print("🔍 Testing each language individually...")
    
    tester = EndToEndIntegrationTester()
    
    for language in ["python"]:  # Start with just Python
        print(f"\n🚀 Testing {language.upper()}")
        print("=" * 50)
        
        try:
            # Call the exact same method as the test
            results = tester.test_end_to_end_integration_workflow()
            
            for result in results:
                if result.language == language:
                    print(f"Language: {result.language}")
                    print(f"Success: {result.success}")
                    print(f"Hook executed: {result.hook_executed}")
                    print(f"Return code: {result.return_code}")
                    print(f"Error message: {result.error_message}")
                    print(f"Warnings: {result.warnings}")
                    if result.stdout:
                        print(f"STDOUT: '{result.stdout[:200]}...'")
                    if result.stderr:
                        print(f"STDERR: '{result.stderr[:200]}...'")
                    break
            else:
                print(f"❌ No results found for {language}")
                
        except Exception as e:
            print(f"❌ Exception testing {language}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()