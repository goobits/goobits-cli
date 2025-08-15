#!/usr/bin/env python3
"""
Performance test script for Goobits CLI lazy loading optimizations.

This script measures CLI startup time with and without advanced features
to validate the <50ms overhead target.
"""

import time
import subprocess
import sys
import tempfile
import os
from pathlib import Path
import statistics


def measure_startup_time(command, iterations=5):
    """Measure CLI startup time over multiple iterations."""
    times = []
    
    for i in range(iterations):
        start = time.perf_counter()
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=10
            )
            end = time.perf_counter()
            
            # Only count successful runs
            if result.returncode == 0 or result.returncode == 1:  # 1 is expected for --help
                times.append((end - start) * 1000)  # Convert to milliseconds
            else:
                print(f"Warning: Command failed with code {result.returncode}: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"Warning: Command timed out on iteration {i+1}")
            continue
    
    if not times:
        return None
        
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'min': min(times),
        'max': max(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'count': len(times)
    }


def generate_test_cli():
    """Generate a test CLI to measure performance."""
    print("📦 Generating test CLI for performance measurement...")
    
    # First, build the current goobits CLI 
    result = subprocess.run(
        ["python3", "-m", "goobits_cli.main", "build"], 
        cwd="/workspace/goobits-cli",
        capture_output=True, 
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Failed to build test CLI: {result.stderr}")
        return None
    
    # The generated CLI should be in src/goobits_cli/generated_cli.py
    cli_path = "/workspace/goobits-cli/src/goobits_cli/generated_cli.py"
    if Path(cli_path).exists():
        return cli_path
    else:
        print(f"❌ Generated CLI not found at expected path: {cli_path}")
        return None


def main():
    """Main performance test function."""
    print("🚀 Goobits CLI Performance Test - Lazy Loading Optimization")
    print("=" * 60)
    
    # Generate test CLI
    cli_path = generate_test_cli()
    if not cli_path:
        sys.exit(1)
    
    print(f"✅ Test CLI generated: {cli_path}")
    print()
    
    # Test 1: Basic help command (should not trigger advanced features)
    print("📊 Test 1: Basic help command (no advanced features)")
    basic_command = f"cd /workspace/goobits-cli && python3 {cli_path} --help"
    basic_times = measure_startup_time(basic_command)
    
    if basic_times:
        print(f"   Mean startup time: {basic_times['mean']:.1f}ms")
        print(f"   Median: {basic_times['median']:.1f}ms")
        print(f"   Range: {basic_times['min']:.1f}ms - {basic_times['max']:.1f}ms")
        print(f"   Std Dev: {basic_times['stdev']:.1f}ms")
    else:
        print("   ❌ Failed to measure basic startup time")
        return
    
    print()
    
    # Test 2: Interactive mode flag (should trigger lazy loading)
    print("📊 Test 2: Interactive mode startup (with advanced features)")
    # Use echo to provide exit command to interactive mode
    interactive_command = f"cd /workspace/goobits-cli && echo 'exit' | python3 {cli_path} --interactive"
    interactive_times = measure_startup_time(interactive_command)
    
    if interactive_times:
        print(f"   Mean startup time: {interactive_times['mean']:.1f}ms")
        print(f"   Median: {interactive_times['median']:.1f}ms") 
        print(f"   Range: {interactive_times['min']:.1f}ms - {interactive_times['max']:.1f}ms")
        print(f"   Std Dev: {interactive_times['stdev']:.1f}ms")
        
        # Calculate overhead
        overhead = interactive_times['mean'] - basic_times['mean']
        print(f"   Advanced features overhead: +{overhead:.1f}ms")
    else:
        print("   ❌ Failed to measure interactive startup time")
        return
    
    print()
    print("📋 Performance Analysis")
    print("-" * 30)
    
    # Analyze results
    basic_time = basic_times['mean']
    interactive_time = interactive_times['mean']
    overhead = interactive_time - basic_time
    
    # Performance targets
    BASIC_TARGET = 100  # <100ms for basic CLI
    OVERHEAD_TARGET = 50  # <50ms overhead for advanced features
    
    print(f"Basic CLI startup:     {basic_time:.1f}ms (target: <{BASIC_TARGET}ms)")
    print(f"Advanced features:     {interactive_time:.1f}ms")
    print(f"Overhead:              +{overhead:.1f}ms (target: <{OVERHEAD_TARGET}ms)")
    print()
    
    # Results
    basic_pass = basic_time < BASIC_TARGET
    overhead_pass = overhead < OVERHEAD_TARGET
    
    print("🎯 Performance Results:")
    print(f"   Basic CLI target:      {'✅ PASS' if basic_pass else '❌ FAIL'}")
    print(f"   Overhead target:       {'✅ PASS' if overhead_pass else '❌ FAIL'}")
    
    if basic_pass and overhead_pass:
        print()
        print("🎉 ALL PERFORMANCE TARGETS MET!")
        print(f"   Lazy loading optimization successful!")
        print(f"   Advanced features overhead reduced to {overhead:.1f}ms (target: <{OVERHEAD_TARGET}ms)")
    else:
        print()
        print("⚠️  Performance targets not met:")
        if not basic_pass:
            print(f"   - Basic CLI startup: {basic_time:.1f}ms exceeds {BASIC_TARGET}ms target")
        if not overhead_pass:
            print(f"   - Advanced features overhead: {overhead:.1f}ms exceeds {OVERHEAD_TARGET}ms target")


if __name__ == "__main__":
    main()