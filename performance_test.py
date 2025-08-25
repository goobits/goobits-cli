#!/usr/bin/env python3
"""
Performance test for logging implementation overhead.
"""

import os
import sys
import time
import tempfile
import subprocess
import statistics
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

def performance_test_framework_logger():
    """Test performance overhead of framework logging."""
    print("=== Framework Logger Performance Test ===")
    
    try:
        from goobits_cli.logger import setup_logging, get_logger, set_context, clear_context
        
        # Test setup time
        setup_times = []
        for i in range(10):
            start_time = time.perf_counter()
            setup_logging()
            end_time = time.perf_counter()
            setup_times.append((end_time - start_time) * 1000)  # Convert to ms
        
        avg_setup_time = statistics.mean(setup_times)
        
        # Test logging performance
        logger = get_logger('performance_test')
        
        # Test without context
        message_times = []
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            for i in range(1000):
                start_time = time.perf_counter()
                logger.info(f"Performance test message {i}")
                end_time = time.perf_counter()
                message_times.append((end_time - start_time) * 1000)  # Convert to ms
        
        avg_message_time = statistics.mean(message_times)
        
        # Test with context
        set_context(test_id='perf_001', iteration=0)
        context_message_times = []
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            for i in range(1000):
                start_time = time.perf_counter()
                logger.info(f"Context performance test message {i}")
                end_time = time.perf_counter()
                context_message_times.append((end_time - start_time) * 1000)
        
        avg_context_message_time = statistics.mean(context_message_times)
        
        # Test context operations
        context_times = []
        for i in range(1000):
            start_time = time.perf_counter()
            set_context(iteration=i, batch='performance_test')
            end_time = time.perf_counter()
            context_times.append((end_time - start_time) * 1000)
        
        avg_context_time = statistics.mean(context_times)
        
        print(f"  Setup time: {avg_setup_time:.3f}ms average")
        print(f"  Message logging: {avg_message_time:.6f}ms per message")
        print(f"  Context message logging: {avg_context_message_time:.6f}ms per message")
        print(f"  Context operations: {avg_context_time:.6f}ms per operation")
        
        # Calculate overhead
        context_overhead = avg_context_message_time - avg_message_time
        print(f"  Context overhead: {context_overhead:.6f}ms per message ({(context_overhead/avg_message_time)*100:.1f}%)")
        
        return {
            'success': True,
            'setup_time_ms': avg_setup_time,
            'message_time_ms': avg_message_time,
            'context_message_time_ms': avg_context_message_time,
            'context_operation_time_ms': avg_context_time,
            'context_overhead_percent': (context_overhead/avg_message_time)*100
        }
        
    except Exception as e:
        print(f"  ✗ Performance test failed: {e}")
        return {'success': False, 'error': str(e)}

def performance_test_generated_cli_startup():
    """Test startup performance of generated CLIs with logging."""
    print("\n=== Generated CLI Startup Performance Test ===")
    
    languages = ['python', 'nodejs', 'typescript', 'rust']
    results = {}
    
    for language in languages:
        print(f"\n--- {language.upper()} CLI Startup ---")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create minimal configuration
                config = {
                    'package_name': f'perf-test-{language}',
                    'command_name': f'perf{language}',
                    'display_name': f'Performance Test {language.title()}',
                    'description': f'Performance test {language} CLI',
                    'language': language,
                    'cli_output_path': f'{temp_dir}/cli.{get_extension(language)}',
                    
                    'python': {'minimum_version': '3.8', 'maximum_version': '3.13'},
                    'installation': {'pypi_name': f'perf-test-{language}'},
                    'shell_integration': {'enabled': False, 'alias': f'perf{language}'},
                    'validation': {'check_api_keys': False, 'check_disk_space': False},
                    
                    'cli': {
                        'name': f'perf{language}',
                        'tagline': f'Performance test {language} CLI',
                        'description': 'Performance test CLI',
                        'commands': {
                            'test': {
                                'desc': 'Test command',
                                'args': [{'name': 'message', 'desc': 'Test message', 'type': 'string'}]
                            }
                        }
                    }
                }
                
                import yaml
                config_file = os.path.join(temp_dir, 'goobits.yaml')
                with open(config_file, 'w') as f:
                    yaml.dump(config, f)
                
                # Generate CLI
                build_cmd = [sys.executable, '-m', 'goobits_cli.main', 'build', config_file]
                build_result = subprocess.run(build_cmd, cwd=temp_dir, capture_output=True, text=True, timeout=30)
                
                if build_result.returncode != 0:
                    print(f"  ✗ Build failed: {build_result.stderr}")
                    results[language] = {'success': False, 'error': 'Build failed'}
                    continue
                
                print(f"  ✓ Build successful")
                
                # Test startup time (help command)
                cli_file = get_cli_executable_path(temp_dir, language)
                if not cli_file:
                    print(f"  ✗ CLI executable not found")
                    results[language] = {'success': False, 'error': 'CLI not found'}
                    continue
                
                # Measure startup times
                startup_times = []
                for i in range(5):  # 5 runs for average
                    start_time = time.perf_counter()
                    
                    if language == 'python':
                        result = subprocess.run([sys.executable, cli_file, '--help'], 
                                              capture_output=True, text=True, timeout=10)
                    elif language in ['nodejs', 'typescript']:
                        # Check if we have node
                        node_check = subprocess.run(['node', '--version'], capture_output=True)
                        if node_check.returncode != 0:
                            print(f"  ⚠ Node.js not available, skipping {language}")
                            break
                        result = subprocess.run(['node', cli_file, '--help'], 
                                              capture_output=True, text=True, timeout=10)
                    elif language == 'rust':
                        # Rust would need compilation first, skip for now
                        print(f"  ⚠ Rust CLI execution requires compilation, skipping")
                        break
                    
                    end_time = time.perf_counter()
                    
                    if result.returncode == 0 or "help" in result.stdout.lower():
                        startup_times.append((end_time - start_time) * 1000)  # ms
                    else:
                        print(f"  ⚠ CLI execution failed: {result.stderr}")
                        break
                
                if startup_times:
                    avg_startup_time = statistics.mean(startup_times)
                    min_startup_time = min(startup_times)
                    max_startup_time = max(startup_times)
                    
                    print(f"  ✓ Startup time: {avg_startup_time:.1f}ms average ({min_startup_time:.1f}-{max_startup_time:.1f}ms range)")
                    
                    results[language] = {
                        'success': True,
                        'avg_startup_ms': avg_startup_time,
                        'min_startup_ms': min_startup_time,
                        'max_startup_ms': max_startup_time
                    }
                else:
                    print(f"  ✗ No successful startup measurements")
                    results[language] = {'success': False, 'error': 'No measurements'}
                
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            results[language] = {'success': False, 'error': str(e)}
    
    return results

def get_extension(language):
    """Get file extension for language."""
    return {'python': 'py', 'nodejs': 'js', 'typescript': 'ts', 'rust': 'rs'}.get(language, 'txt')

def get_cli_executable_path(temp_dir, language):
    """Get the CLI executable path for a language."""
    if language == 'python':
        # Look for main CLI file
        cli_path = os.path.join(temp_dir, 'cli.py')
        if os.path.exists(cli_path):
            return cli_path
    elif language in ['nodejs', 'typescript']:
        # Look for CLI file
        for filename in ['cli.js', 'cli.ts', 'index.js']:
            cli_path = os.path.join(temp_dir, filename)
            if os.path.exists(cli_path):
                return cli_path
    elif language == 'rust':
        # Look for main.rs or built binary
        main_path = os.path.join(temp_dir, 'src', 'main.rs')
        if os.path.exists(main_path):
            return main_path
    
    return None

def main():
    """Run performance tests for logging implementation."""
    print("Logging Implementation Performance Tests")
    print("=" * 50)
    
    # Framework logger performance
    framework_results = performance_test_framework_logger()
    
    # Generated CLI startup performance
    cli_results = performance_test_generated_cli_startup()
    
    # Summary
    print(f"\n{'='*50}")
    print("PERFORMANCE TEST RESULTS")
    print(f"{'='*50}")
    
    print("\n--- Framework Logger Performance ---")
    if framework_results['success']:
        print(f"Setup time: {framework_results['setup_time_ms']:.3f}ms")
        print(f"Message logging: {framework_results['message_time_ms']:.6f}ms per message")
        print(f"Context overhead: {framework_results['context_overhead_percent']:.1f}%")
        
        # Performance assessment
        if framework_results['setup_time_ms'] < 10:
            print("✅ Setup time: EXCELLENT (<10ms)")
        elif framework_results['setup_time_ms'] < 50:
            print("✅ Setup time: GOOD (<50ms)")
        else:
            print("⚠️ Setup time: SLOW (>50ms)")
        
        if framework_results['message_time_ms'] < 0.1:
            print("✅ Message logging: EXCELLENT (<0.1ms)")
        elif framework_results['message_time_ms'] < 1:
            print("✅ Message logging: GOOD (<1ms)")
        else:
            print("⚠️ Message logging: SLOW (>1ms)")
    else:
        print("❌ Framework performance test FAILED")
    
    print("\n--- Generated CLI Startup Performance ---")
    successful_languages = 0
    total_languages = len(cli_results)
    
    for language, result in cli_results.items():
        if result.get('success'):
            successful_languages += 1
            startup_time = result['avg_startup_ms']
            print(f"{language.upper()}: {startup_time:.1f}ms average")
            
            if startup_time < 100:
                print("  ✅ EXCELLENT (<100ms)")
            elif startup_time < 500:
                print("  ✅ GOOD (<500ms)")
            elif startup_time < 1000:
                print("  ⚠️ ACCEPTABLE (<1s)")
            else:
                print("  ❌ SLOW (>1s)")
        else:
            error = result.get('error', 'Unknown error')
            print(f"{language.upper()}: ❌ FAILED ({error})")
    
    # Overall assessment
    print(f"\n--- Overall Performance Assessment ---")
    print(f"Framework logger: {'✅ PASSED' if framework_results['success'] else '❌ FAILED'}")
    print(f"Generated CLIs: {successful_languages}/{total_languages} tested successfully")
    
    if (framework_results['success'] and 
        framework_results['setup_time_ms'] < 50 and 
        framework_results['message_time_ms'] < 1 and
        successful_languages >= 1):
        print("\n🎉 PERFORMANCE TESTS: ✅ PASSED")
        print("   Logging implementation has acceptable performance overhead")
        return True
    else:
        print("\n💥 PERFORMANCE TESTS: ❌ FAILED") 
        print("   Performance issues detected")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)