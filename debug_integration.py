#!/usr/bin/env python3
"""
Debug the actual integration test for Python only.
"""

import sys
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tests.integration.test_cross_language import EndToEndIntegrationTester


def main():
    """Run the actual integration test for Python only."""
    print("🔍 Debug Actual Integration Test - Python Only")
    print("=" * 60)
    
    tester = EndToEndIntegrationTester()
    
    try:
        # Test just Python
        results = []
        language = "python"
        
        # Use the same workflow as the actual test
        from tests.integration.test_cross_language import CLIExecutionResult
        import time
        
        result = CLIExecutionResult("e2e_integration", language)
        start_time = time.time()
        
        try:
            # Step 1: Create test configuration
            config = tester.create_comprehensive_test_config(language, "e2e_test")
            print("✅ Configuration created")
            
            # Step 2: Generate CLI code
            generator = tester._get_generator(language)
            print(f"✅ Generator created (use_universal_templates={generator.use_universal_templates})")
            
            all_files = generator.generate_all_files(config, f"e2e_test_{language}.yaml", "1.0.0")
            
            if not all_files:
                result.error_message = f"No files generated for {language}"
                result.success = False
                print("❌ No files generated")
                return
            
            print(f"✅ Generated {len(all_files)} files")
            
            # Step 3: Create temporary directory for CLI
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix=f"e2e_test_{language}_")
            tester.temp_dirs.append(temp_dir)
            print(f"✅ Temp directory: {temp_dir}")
            
            # Step 4: Write generated files
            executable_files = all_files.pop('__executable__', [])
            for filename, content in all_files.items():
                file_path = Path(temp_dir) / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                
                # Make executable if needed
                if filename in executable_files or filename.startswith('bin/') or filename == 'setup.sh':
                    file_path.chmod(0o755)
            
            result.warnings.append(f"Generated {len(all_files)} files in {temp_dir}")
            print(f"✅ Files written")
            
            # Step 5: Create hook implementations
            hooks = tester.create_hook_implementations(temp_dir, language)
            for hook_file, hook_content in hooks.items():
                hook_path = Path(temp_dir) / hook_file
                hook_path.parent.mkdir(parents=True, exist_ok=True)
                hook_path.write_text(hook_content)
            
            result.warnings.append(f"Created {len(hooks)} hook files")
            print(f"✅ Created {len(hooks)} hook files")
            
            # Debug: List all files
            print("\n📁 All files in temp directory:")
            for file_path in Path(temp_dir).rglob("*"):
                if file_path.is_file():
                    print(f"   {file_path.relative_to(temp_dir)}")
            
            # Step 6: Test CLI installation and execution
            execution_result = tester._test_language_specific_integration(language, temp_dir, all_files, config)
            
            print(f"\n🧪 Execution result:")
            print(f"   Success: {execution_result['success']}")
            print(f"   Return code: {execution_result['return_code']}")  
            print(f"   Hook executed: {execution_result['hook_executed']}")
            print(f"   Installation success: {execution_result['installation_success']}")
            print(f"   Warnings: {execution_result['warnings']}")
            print(f"   Error message: {execution_result['error_message']}")
            print(f"   Stdout: {execution_result['stdout'][:200]}...")
            print(f"   Stderr: {execution_result['stderr'][:200]}...")
            
            result.success = execution_result["success"]
            result.hook_executed = execution_result.get("hook_executed", False)
            
        except Exception as e:
            result.error_message = f"End-to-end integration failed for {language}: {str(e)}"
            result.success = False
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        results.append(result)
        
        # Summary
        print(f"\n📊 Result Summary:")
        print(f"   Success: {result.success}")
        print(f"   Hook executed: {result.hook_executed}")
        print(f"   Execution time: {result.execution_time_ms:.1f}ms")
        print(f"   Warnings: {len(result.warnings)}")
        
        if result.success and result.hook_executed:
            print("✅ TEST PASSED: Hook integration working!")
        elif result.success:
            print("⚠️  TEST PARTIAL: CLI works but hooks not executed")
        else:
            print("❌ TEST FAILED")
            
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()