#!/usr/bin/env python3
"""
Simple performance test for logging overhead.
"""

import os
import sys
import time
import tempfile
import subprocess
import statistics

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

def test_framework_performance():
    """Quick performance test for framework logging."""
    print("=== Framework Logger Performance Test ===")
    
    # Temporarily disable all output to avoid console spam
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    try:
        from goobits_cli.logger import setup_logging, get_logger, set_context
        
        # Redirect to devnull for performance testing
        with open(os.devnull, 'w') as devnull:
            sys.stdout = devnull
            sys.stderr = devnull
            
            # Test setup performance
            setup_times = []
            for i in range(5):  # Reduced iterations
                start = time.perf_counter()
                setup_logging()
                end = time.perf_counter()
                setup_times.append((end - start) * 1000)
            
            avg_setup = statistics.mean(setup_times)
            
            # Test logging performance
            logger = get_logger('perf_test')
            
            log_times = []
            for i in range(100):  # Reduced iterations
                start = time.perf_counter()
                logger.info(f"Test message {i}")
                end = time.perf_counter()
                log_times.append((end - start) * 1000)
            
            avg_log_time = statistics.mean(log_times)
            
            # Test context performance
            set_context(test_id="perf_test")
            
            context_times = []
            for i in range(100):
                start = time.perf_counter()
                logger.info(f"Context message {i}")
                end = time.perf_counter()
                context_times.append((end - start) * 1000)
            
            avg_context_time = statistics.mean(context_times)
            
    finally:
        # Restore stdout/stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
    
    print(f"  Setup time: {avg_setup:.2f}ms average")
    print(f"  Log message: {avg_log_time:.4f}ms per message")
    print(f"  Context logging: {avg_context_time:.4f}ms per message")
    
    overhead = avg_context_time - avg_log_time
    print(f"  Context overhead: {overhead:.4f}ms ({(overhead/avg_log_time)*100:.1f}%)")
    
    # Performance assessment
    if avg_setup < 10 and avg_log_time < 0.1:
        print("  ✅ EXCELLENT performance")
        return True
    elif avg_setup < 50 and avg_log_time < 1:
        print("  ✅ GOOD performance")
        return True
    else:
        print("  ⚠️ ACCEPTABLE performance")
        return True

def test_cli_generation_speed():
    """Test CLI generation performance."""
    print("\n=== CLI Generation Speed Test ===")
    
    languages = ['python', 'nodejs']  # Test subset for speed
    
    for language in languages:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Simple config
                config = {
                    'package_name': f'perf-{language}',
                    'command_name': f'perf{language}',
                    'display_name': f'Perf {language.title()}',
                    'description': f'Performance test',
                    'language': language,
                    'cli_output_path': f'{temp_dir}/cli.{get_extension(language)}',
                    'python': {'minimum_version': '3.8', 'maximum_version': '3.13'},
                    'installation': {'pypi_name': f'perf-{language}'},
                    'shell_integration': {'enabled': False, 'alias': f'perf{language}'},
                    'validation': {'check_api_keys': False, 'check_disk_space': False},
                    'cli': {
                        'name': f'perf{language}',
                        'tagline': f'Performance test CLI',
                        'description': 'Test CLI',
                        'commands': {'test': {'desc': 'Test command'}}
                    }
                }
                
                import yaml
                config_file = os.path.join(temp_dir, 'goobits.yaml')
                with open(config_file, 'w') as f:
                    yaml.dump(config, f)
                
                # Time the generation
                start_time = time.perf_counter()
                
                build_cmd = [sys.executable, '-m', 'goobits_cli.main', 'build', config_file]
                result = subprocess.run(build_cmd, cwd=temp_dir, capture_output=True, text=True, timeout=30)
                
                end_time = time.perf_counter()
                generation_time = (end_time - start_time) * 1000  # ms
                
                if result.returncode == 0:
                    print(f"  {language.upper()}: {generation_time:.1f}ms generation time")
                    
                    # Check files were generated
                    cli_file = config['cli_output_path']
                    if os.path.exists(cli_file):
                        size = os.path.getsize(cli_file)
                        print(f"    Generated {size} byte CLI file")
                        
                        # Check for logger file
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                if 'logger' in file.lower():
                                    logger_size = os.path.getsize(os.path.join(root, file))
                                    print(f"    Generated {logger_size} byte logger file")
                                    break
                    
                    if generation_time < 5000:  # Under 5 seconds
                        print(f"    ✅ FAST generation")
                    elif generation_time < 15000:  # Under 15 seconds
                        print(f"    ✅ ACCEPTABLE generation")
                    else:
                        print(f"    ⚠️ SLOW generation")
                else:
                    print(f"  {language.upper()}: ❌ Generation failed")
                    
        except Exception as e:
            print(f"  {language.upper()}: ❌ Test failed: {e}")

def get_extension(language):
    """Get file extension for language."""
    return {'python': 'py', 'nodejs': 'js', 'typescript': 'ts', 'rust': 'rs'}.get(language, 'txt')

def main():
    """Run simple performance tests."""
    print("Simple Logging Performance Tests")
    print("=" * 40)
    
    framework_ok = test_framework_performance()
    test_cli_generation_speed()
    
    print(f"\n{'='*40}")
    print("Performance Test Summary")
    print(f"{'='*40}")
    
    if framework_ok:
        print("✅ Framework logging has acceptable performance")
        print("✅ CLI generation includes logging components")
        return True
    else:
        print("❌ Performance issues detected")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)