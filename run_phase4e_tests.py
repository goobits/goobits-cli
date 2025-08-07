#!/usr/bin/env python3
"""
Simplified Phase 4E Integration Test Runner

This script runs basic integration tests to validate Phase 4 features.
"""

import sys
import time
import subprocess
import tempfile
import shutil
from pathlib import Path
import yaml
from rich.console import Console

console = Console()

def create_test_config(language: str, test_dir: Path) -> Path:
    """Create a simple test configuration for a language"""
    config = {
        "package_name": f"phase4e-test-{language}",
        "command_name": f"test-{language}",
        "display_name": f"Phase 4E Test CLI for {language}",
        "description": f"Phase 4E test CLI for {language}",
        "language": language,
        
        # Required fields
        "python": {
            "minimum_version": "3.8"
        },
        "dependencies": {
            "required": [],
            "optional": []
        },
        "installation": {
            "pypi_name": f"phase4e-test-{language}",
            "development_path": str(test_dir)
        },
        "shell_integration": {
            "enabled": False,
            "alias": f"test-{language}"
        },
        "validation": {
            "check_api_keys": False
        },
        "messages": {
            "install_success": "CLI installed successfully!"
        },
        
        "cli": {
            "name": f"test-{language}",
            "version": "2.0.0",
            "tagline": "Phase 4E test CLI",
            "description": "Test CLI for Phase 4E integration testing",
            "commands": {
                "hello": {
                    "desc": "Say hello",
                    "args": [
                        {"name": "name", "desc": "Name to greet", "required": True}
                    ]
                },
                "test": {
                    "desc": "Run tests",
                    "options": [
                        {"name": "verbose", "type": "flag", "desc": "Verbose output"}
                    ]
                }
            }
        }
    }
    
    config_file = test_dir / "goobits.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return config_file

def test_cli_generation(language: str) -> bool:
    """Test CLI generation for a specific language"""
    console.print(f"[cyan]Testing {language} CLI generation...[/cyan]")
    
    test_dir = Path(tempfile.mkdtemp(prefix=f"test_{language}_"))
    
    try:
        # Create test configuration
        config_file = create_test_config(language, test_dir)
        
        # Build CLI using goobits
        start_time = time.time()
        result = subprocess.run([
            sys.executable, "-m", "goobits_cli.main", "build",
            str(config_file), "--output-dir", str(test_dir)
        ], capture_output=True, text=True, timeout=60)
        
        build_time = (time.time() - start_time) * 1000
        
        if result.returncode == 0:
            console.print(f"✅ {language} CLI generated successfully in {build_time:.1f}ms")
            
            # Check if expected files were created
            if language == "python":
                expected_file = test_dir / "generated_cli.py"
            elif language == "nodejs":
                expected_file = test_dir / "cli.js"
            elif language == "typescript":
                expected_file = test_dir / "cli.ts"
            elif language == "rust":
                expected_file = test_dir / "src" / "main.rs"
            
            if expected_file.exists():
                console.print(f"  ✅ Expected file {expected_file.name} created")
                return True
            else:
                console.print(f"  ❌ Expected file {expected_file.name} not found")
                return False
        else:
            console.print(f"❌ {language} CLI generation failed:")
            console.print(f"  stdout: {result.stdout}")
            console.print(f"  stderr: {result.stderr}")
            return False
    
    except Exception as e:
        console.print(f"❌ {language} CLI generation failed with exception: {e}")
        return False
    
    finally:
        # Cleanup
        if test_dir.exists():
            shutil.rmtree(test_dir, ignore_errors=True)

def test_cli_execution(language: str) -> bool:
    """Test that generated CLI can execute basic commands"""
    console.print(f"[cyan]Testing {language} CLI execution...[/cyan]")
    
    test_dir = Path(tempfile.mkdtemp(prefix=f"exec_{language}_"))
    
    try:
        # Create and build CLI
        config_file = create_test_config(language, test_dir)
        result = subprocess.run([
            sys.executable, "-m", "goobits_cli.main", "build",
            str(config_file), "--output-dir", str(test_dir)
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            console.print(f"❌ Failed to build CLI for execution test")
            return False
        
        # Test CLI execution
        if language == "python":
            cmd = [sys.executable, str(test_dir / "generated_cli.py"), "--help"]
        elif language == "nodejs":
            cmd = ["node", str(test_dir / "cli.js"), "--help"]
        elif language == "typescript":
            cmd = ["node", str(test_dir / "cli.js"), "--help"]
        elif language == "rust":
            # Compile first
            compile_result = subprocess.run(
                ["cargo", "build"], cwd=test_dir, capture_output=True
            )
            if compile_result.returncode != 0:
                console.print(f"❌ Rust compilation failed")
                return False
            cmd = [str(test_dir / "target" / "debug" / f"test-{language}"), "--help"]
        
        # Execute CLI
        start_time = time.time()
        exec_result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        exec_time = (time.time() - start_time) * 1000
        
        if exec_result.returncode == 0:
            console.print(f"✅ {language} CLI executed successfully in {exec_time:.1f}ms")
            console.print(f"  Help output length: {len(exec_result.stdout)} chars")
            return True
        else:
            console.print(f"❌ {language} CLI execution failed:")
            console.print(f"  stdout: {exec_result.stdout[:200]}...")
            console.print(f"  stderr: {exec_result.stderr[:200]}...")
            return False
    
    except Exception as e:
        console.print(f"❌ {language} CLI execution failed with exception: {e}")
        return False
    
    finally:
        # Cleanup
        if test_dir.exists():
            shutil.rmtree(test_dir, ignore_errors=True)

def main():
    """Run Phase 4E integration tests"""
    console.print("[bold green]🚀 Phase 4E - Quick Integration Test Suite[/bold green]")
    console.print("Testing basic CLI generation and execution across all supported languages\n")
    
    languages = ["python", "nodejs", "typescript", "rust"]
    results = {}
    
    # Test 1: CLI Generation
    console.print("[bold blue]Test 1: CLI Generation[/bold blue]")
    for language in languages:
        results[f"{language}_generation"] = test_cli_generation(language)
    
    console.print()
    
    # Test 2: CLI Execution (only for languages that generated successfully)
    console.print("[bold blue]Test 2: CLI Execution[/bold blue]")
    for language in languages:
        if results.get(f"{language}_generation", False):
            results[f"{language}_execution"] = test_cli_execution(language)
        else:
            results[f"{language}_execution"] = False
            console.print(f"⏭️  Skipping {language} execution (generation failed)")
    
    # Summary
    console.print("\n[bold blue]📊 Test Summary[/bold blue]")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    console.print(f"Total Tests: {total_tests}")
    console.print(f"Passed: {passed_tests}")
    console.print(f"Failed: {total_tests - passed_tests}")
    console.print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Detailed results
    console.print("\n[bold blue]Detailed Results:[/bold blue]")
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        console.print(f"  {status} {test_name}")
    
    # Overall status
    if passed_tests == total_tests:
        console.print("\n[bold green]🎉 All tests passed! Ready for Phase 4E completion.[/bold green]")
        return 0
    elif passed_tests >= total_tests * 0.8:  # 80% pass rate
        console.print(f"\n[bold yellow]⚠️  Most tests passed ({(passed_tests/total_tests)*100:.1f}%), but some issues need attention.[/bold yellow]")
        return 1
    else:
        console.print(f"\n[bold red]❌ Many tests failed ({(passed_tests/total_tests)*100:.1f}% pass rate). Significant work needed.[/bold red]")
        return 2

if __name__ == "__main__":
    sys.exit(main())