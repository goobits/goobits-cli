#!/usr/bin/env python3
"""
Performance Suite Controller - Master orchestrator for all performance tools
This script runs the benchmark_suite.py and provides unified reporting
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Main entry point - delegates to benchmark_suite.py"""
    # Pass all arguments through to benchmark_suite.py
    benchmark_script = Path(__file__).parent / "benchmark_suite.py"
    
    cmd = [sys.executable, str(benchmark_script)] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️ Performance validation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Failed to run performance validation: {e}")
        return 1

if __name__ == "__main__":
    exit(main())