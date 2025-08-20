#!/usr/bin/env python3
"""Run feature parity tests across all supported languages"""

import sys
import argparse
from pathlib import Path
from runner.parity_runner import ParityTestRunner


def main():
    parser = argparse.ArgumentParser(
        description="Run feature parity tests for goobits-cli across all supported languages"
    )
    parser.add_argument(
        "--suite",
        help="Run specific test suite(s)",
        nargs="+",
        choices=["basic-commands", "config-commands", "completion-commands", 
                 "error-handling", "advanced-features"]
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--language",
        help="Test only specific language(s)",
        nargs="+",
        choices=["python", "nodejs", "typescript", "rust"]
    )
    
    args = parser.parse_args()
    
    # Find test suites
    suites_dir = Path(__file__).parent / "suites"
    
    if args.suite:
        suite_files = [suites_dir / f"{suite}.yaml" for suite in args.suite]
    else:
        suite_files = sorted(suites_dir.glob("*.yaml"))
        
    # Check that all suite files exist
    for suite_file in suite_files:
        if not suite_file.exists():
            print(f"Error: Test suite not found: {suite_file}")
            sys.exit(1)
            
    # Create test runner
    runner = ParityTestRunner(verbose=args.verbose)
    
    # Override languages if specified
    if args.language:
        runner.LANGUAGES = args.language
        
    # Run all test suites
    all_results = {}
    
    for suite_file in suite_files:
        try:
            results = runner.run_suite(suite_file)
            all_results[suite_file.stem] = results
        except Exception as e:
            print(f"\nError running suite {suite_file.name}: {str(e)}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
            
    # Print summary
    all_passed = runner.print_summary(all_results)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()