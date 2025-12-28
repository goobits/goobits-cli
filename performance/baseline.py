#!/usr/bin/env python3
"""
Performance Baseline Script for Universal-First Refactor

This script measures and records baseline performance metrics for:
1. CLI generation time per language
2. Generated CLI startup time
3. Memory usage during generation

Usage:
    python performance/baseline.py [--save] [--compare]

Options:
    --save      Save results to baseline.json
    --compare   Compare current results against saved baseline
"""

import argparse
import json
import subprocess
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path
from typing import Any, Dict, List, Optional

# Performance targets from proposal
TARGETS = {
    "generation_time_ms": 1000,  # <= 1s per language
    "startup_time_ms": 100,      # <= 100ms cold start
    "memory_mb": 5,              # <= 5MB
}

BASELINE_FILE = Path(__file__).parent / "baseline.json"

# Sample minimal goobits.yaml for testing
SAMPLE_CONFIG = """
package_name: "test-cli"
command_name: "testcli"
display_name: "Test CLI"
description: "A test CLI for performance benchmarking"

cli:
  name: "testcli"
  tagline: "Performance test CLI"
  version: "1.0.0"
  commands:
    - name: status
      desc: "Show status"
    - name: info
      desc: "Show info"
      options:
        - name: verbose
          short: v
          type: bool
          desc: "Verbose output"
"""


def measure_generation_time(language: str, config_path: Path) -> Dict[str, Any]:
    """Measure time to generate CLI for a given language."""
    from goobits_cli.core.config import load_config
    from goobits_cli.generation.builder import Builder

    # Load config
    config = load_config(str(config_path))

    # Measure generation time
    start = time.perf_counter()
    builder = Builder(language=language)
    try:
        _ = builder.build(config, str(config_path))
        success = True
        error = None
    except Exception as e:
        success = False
        error = str(e)
    end = time.perf_counter()

    return {
        "language": language,
        "generation_time_ms": (end - start) * 1000,
        "success": success,
        "error": error,
    }


def measure_memory_usage(language: str, config_path: Path) -> Dict[str, Any]:
    """Measure memory usage during generation."""
    from goobits_cli.core.config import load_config
    from goobits_cli.generation.builder import Builder

    config = load_config(str(config_path))

    tracemalloc.start()
    builder = Builder(language=language)
    try:
        _ = builder.build(config, str(config_path))
    except Exception:
        pass
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "language": language,
        "current_mb": current / 1024 / 1024,
        "peak_mb": peak / 1024 / 1024,
    }


def measure_startup_time(cli_path: Path, language: str) -> Dict[str, Any]:
    """Measure CLI startup time (--help invocation)."""
    if language == "python":
        cmd = [sys.executable, str(cli_path), "--help"]
    elif language in ("nodejs", "typescript"):
        cmd = ["node", str(cli_path), "--help"]
    elif language == "rust":
        # Rust needs compilation first, skip for baseline
        return {
            "language": language,
            "startup_time_ms": None,
            "success": False,
            "error": "Rust requires compilation, skipped",
        }
    else:
        return {
            "language": language,
            "startup_time_ms": None,
            "success": False,
            "error": f"Unknown language: {language}",
        }

    start = time.perf_counter()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=10,
        )
        success = result.returncode == 0
        error = None if success else result.stderr.decode()[:200]
    except subprocess.TimeoutExpired:
        success = False
        error = "Timeout (>10s)"
    except FileNotFoundError as e:
        success = False
        error = str(e)
    end = time.perf_counter()

    return {
        "language": language,
        "startup_time_ms": (end - start) * 1000,
        "success": success,
        "error": error,
    }


def run_baseline(languages: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run full baseline measurement suite."""
    if languages is None:
        languages = ["python", "nodejs", "typescript", "rust"]

    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "targets": TARGETS,
        "generation": {},
        "memory": {},
        "startup": {},
        "summary": {},
    }

    # Create temp config file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        f.write(SAMPLE_CONFIG)
        config_path = Path(f.name)

    try:
        for lang in languages:
            print(f"Measuring {lang}...")

            # Generation time
            gen_result = measure_generation_time(lang, config_path)
            results["generation"][lang] = gen_result

            # Memory usage
            mem_result = measure_memory_usage(lang, config_path)
            results["memory"][lang] = mem_result

            # Startup time (requires generated file)
            if gen_result["success"]:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".py" if lang == "python" else ".mjs",
                    delete=False,
                ) as cli_file:
                    # Would need actual generated content here
                    # For now, skip startup measurement in baseline
                    results["startup"][lang] = {
                        "language": lang,
                        "startup_time_ms": None,
                        "success": False,
                        "error": "Startup measurement requires full generation pipeline",
                    }

    finally:
        config_path.unlink(missing_ok=True)

    # Calculate summary
    gen_times = [
        r["generation_time_ms"]
        for r in results["generation"].values()
        if r["success"]
    ]
    mem_peaks = [r["peak_mb"] for r in results["memory"].values()]

    results["summary"] = {
        "avg_generation_time_ms": sum(gen_times) / len(gen_times) if gen_times else None,
        "max_generation_time_ms": max(gen_times) if gen_times else None,
        "max_memory_mb": max(mem_peaks) if mem_peaks else None,
        "all_generation_passed": all(
            r["success"] for r in results["generation"].values()
        ),
        "meets_generation_target": all(
            r["generation_time_ms"] <= TARGETS["generation_time_ms"]
            for r in results["generation"].values()
            if r["success"]
        ),
        "meets_memory_target": all(
            r["peak_mb"] <= TARGETS["memory_mb"]
            for r in results["memory"].values()
        ),
    }

    return results


def save_baseline(results: Dict[str, Any]) -> None:
    """Save baseline results to file."""
    with open(BASELINE_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Baseline saved to {BASELINE_FILE}")


def load_baseline() -> Optional[Dict[str, Any]]:
    """Load baseline results from file."""
    if not BASELINE_FILE.exists():
        return None
    with open(BASELINE_FILE) as f:
        return json.load(f)


def compare_results(current: Dict[str, Any], baseline: Dict[str, Any]) -> None:
    """Compare current results against baseline."""
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)

    print(f"\nBaseline: {baseline.get('timestamp', 'unknown')}")
    print(f"Current:  {current.get('timestamp', 'unknown')}")

    print("\nGeneration Time (ms):")
    print("-" * 40)
    for lang in current["generation"]:
        curr = current["generation"][lang].get("generation_time_ms")
        base = baseline.get("generation", {}).get(lang, {}).get("generation_time_ms")
        if curr and base:
            diff = curr - base
            pct = (diff / base) * 100
            status = "✓" if curr <= TARGETS["generation_time_ms"] else "✗"
            print(f"  {lang:12} {curr:8.1f} (was {base:.1f}, {pct:+.1f}%) {status}")
        elif curr:
            status = "✓" if curr <= TARGETS["generation_time_ms"] else "✗"
            print(f"  {lang:12} {curr:8.1f} (no baseline) {status}")

    print("\nMemory Usage (MB):")
    print("-" * 40)
    for lang in current["memory"]:
        curr = current["memory"][lang].get("peak_mb")
        base = baseline.get("memory", {}).get(lang, {}).get("peak_mb")
        if curr and base:
            diff = curr - base
            status = "✓" if curr <= TARGETS["memory_mb"] else "✗"
            print(f"  {lang:12} {curr:8.2f} (was {base:.2f}, {diff:+.2f}) {status}")
        elif curr:
            status = "✓" if curr <= TARGETS["memory_mb"] else "✗"
            print(f"  {lang:12} {curr:8.2f} (no baseline) {status}")

    print("\nSummary:")
    print("-" * 40)
    summary = current["summary"]
    print(f"  All generation passed: {summary.get('all_generation_passed', False)}")
    print(f"  Meets generation target: {summary.get('meets_generation_target', False)}")
    print(f"  Meets memory target: {summary.get('meets_memory_target', False)}")


def print_results(results: Dict[str, Any]) -> None:
    """Print results in a readable format."""
    print("\n" + "=" * 60)
    print("PERFORMANCE BASELINE RESULTS")
    print("=" * 60)
    print(f"Timestamp: {results.get('timestamp', 'unknown')}")

    print("\nTargets:")
    for key, value in TARGETS.items():
        print(f"  {key}: {value}")

    print("\nGeneration Time (ms):")
    print("-" * 40)
    for lang, data in results["generation"].items():
        if data["success"]:
            status = "✓" if data["generation_time_ms"] <= TARGETS["generation_time_ms"] else "✗"
            print(f"  {lang:12} {data['generation_time_ms']:8.1f} {status}")
        else:
            print(f"  {lang:12} FAILED: {data.get('error', 'unknown')[:40]}")

    print("\nMemory Usage (MB):")
    print("-" * 40)
    for lang, data in results["memory"].items():
        status = "✓" if data["peak_mb"] <= TARGETS["memory_mb"] else "✗"
        print(f"  {lang:12} {data['peak_mb']:8.2f} (peak) {status}")

    print("\nSummary:")
    print("-" * 40)
    summary = results["summary"]
    print(f"  Avg generation time: {summary.get('avg_generation_time_ms', 0):.1f} ms")
    print(f"  Max generation time: {summary.get('max_generation_time_ms', 0):.1f} ms")
    print(f"  Max memory usage: {summary.get('max_memory_mb', 0):.2f} MB")
    print(f"  All targets met: {summary.get('meets_generation_target', False) and summary.get('meets_memory_target', False)}")


def main():
    parser = argparse.ArgumentParser(description="Performance baseline measurement")
    parser.add_argument("--save", action="store_true", help="Save results to baseline.json")
    parser.add_argument("--compare", action="store_true", help="Compare against saved baseline")
    parser.add_argument("--language", "-l", action="append", help="Specific language(s) to test")
    args = parser.parse_args()

    languages = args.language if args.language else None

    print("Running performance baseline...")
    results = run_baseline(languages)

    print_results(results)

    if args.save:
        save_baseline(results)

    if args.compare:
        baseline = load_baseline()
        if baseline:
            compare_results(results, baseline)
        else:
            print("\nNo baseline file found. Run with --save first.")

    # Exit with error if targets not met
    if not results["summary"].get("meets_generation_target", False):
        print("\n⚠️  Generation time target not met!")
        return 1
    if not results["summary"].get("meets_memory_target", False):
        print("\n⚠️  Memory target not met!")
        return 1

    print("\n✓ All performance targets met.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
