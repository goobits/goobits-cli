#!/usr/bin/env python3
"""
Build Size Analyzer and Budget Checker for Goobits CLI Framework
"""

import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any
import subprocess

# Size budgets in bytes
SIZE_BUDGETS = {
    'python_source': 15 * 1024,      # 15 KB
    'nodejs_source': 120 * 1024,     # 120 KB  
    'typescript_source': 100 * 1024,  # 100 KB
    'rust_source': 60 * 1024,        # 60 KB
}

def analyze_generated_sizes() -> Dict[str, int]:
    """Analyze generated CLI sizes across all languages"""
    
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    
    from goobits_cli.generators.python import PythonGenerator
    from goobits_cli.generators.nodejs import NodeJSGenerator
    from goobits_cli.generators.typescript import TypeScriptGenerator
    from goobits_cli.generators.rust import RustGenerator
    from goobits_cli.schemas import ConfigSchema

    # Test configuration
    config = ConfigSchema(cli={
        'name': 'test-cli',
        'tagline': 'Test CLI for size analysis',
        'version': '1.0.0',
        'commands': {
            'hello': {'desc': 'Say hello'},
            'build': {'desc': 'Build something', 'subcommands': {
                'fast': {'desc': 'Fast build'},
                'full': {'desc': 'Full build'}
            }}
        }
    })

    generators = {
        'python': PythonGenerator(),
        'nodejs': NodeJSGenerator(),
        'typescript': TypeScriptGenerator(),
        'rust': RustGenerator()
    }

    sizes = {}
    
    for lang, gen in generators.items():
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                files = gen.generate_to_directory(config, temp_dir)
                
                temp_path = Path(temp_dir)
                total_size = sum(
                    f.stat().st_size 
                    for f in temp_path.rglob('*') 
                    if f.is_file() and not f.name.startswith('.')
                )
                
                sizes[f'{lang}_source'] = total_size
                
            except Exception as e:
                print(f"❌ Failed to analyze {lang}: {e}")
                sizes[f'{lang}_source'] = 0
    
    return sizes

def check_size_budgets(sizes: Dict[str, int]) -> bool:
    """Check if sizes meet budgets"""
    
    print("📊 SIZE BUDGET ANALYSIS")
    print("=" * 50)
    
    all_passed = True
    
    for target, budget in SIZE_BUDGETS.items():
        actual = sizes.get(target, 0)
        passed = actual <= budget
        status = "✅" if passed else "❌"
        
        print(f"{status} {target}: {actual:,} bytes ({actual/1024:.1f} KB) "
              f"vs {budget:,} bytes budget ({budget/1024:.1f} KB)")
        
        if not passed:
            all_passed = False
            over_by = actual - budget
            print(f"   Exceeds budget by {over_by:,} bytes ({over_by/1024:.1f} KB)")
    
    print(f"\n🎯 Overall: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    
    return all_passed

def generate_size_report(sizes: Dict[str, int]) -> str:
    """Generate comprehensive size report"""
    
    report = [
        "# Build Size Analysis Report",
        f"Generated: {subprocess.check_output(['date']).decode().strip()}",
        "",
        "## Current Sizes",
        ""
    ]
    
    for target, size in sizes.items():
        report.append(f"- **{target}**: {size:,} bytes ({size/1024:.1f} KB)")
    
    report.extend([
        "",
        "## Size Budgets",
        ""
    ])
    
    for target, budget in SIZE_BUDGETS.items():
        actual = sizes.get(target, 0)
        status = "✅" if actual <= budget else "❌" 
        report.append(f"- {status} **{target}**: {actual:,} / {budget:,} bytes")
    
    # Optimization recommendations
    report.extend([
        "",
        "## Optimization Recommendations",
        ""
    ])
    
    for target, budget in SIZE_BUDGETS.items():
        actual = sizes.get(target, 0)
        if actual > budget:
            over_pct = ((actual - budget) / budget) * 100
            report.append(f"- **{target}**: Reduce by {over_pct:.1f}% ({actual-budget:,} bytes)")
    
    return "\n".join(report)

def main():
    """Main entry point"""
    
    print("🔍 Analyzing generated CLI sizes...")
    sizes = analyze_generated_sizes()
    
    # Check budgets
    passed = check_size_budgets(sizes)
    
    # Generate report
    report = generate_size_report(sizes)
    
    # Save report
    report_path = Path("build_size_report.md")
    report_path.write_text(report)
    print(f"\n📄 Size report saved to {report_path}")
    
    # Save sizes as JSON for CI
    sizes_path = Path("build_sizes.json")
    with open(sizes_path, 'w') as f:
        json.dump(sizes, f, indent=2)
    
    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())