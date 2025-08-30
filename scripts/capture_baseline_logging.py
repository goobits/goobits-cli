#!/usr/bin/env python3
"""
Phase 1: Capture baseline logging outputs for validation.

This script captures the current logging template outputs for all test configurations
to establish a baseline for regression testing during the extraction process.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import hashlib

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from goobits_cli.schemas import GoobitsConfigSchema, CLISchema
from goobits_cli.universal.template_engine import UniversalTemplateEngine
from goobits_cli.universal.component_registry import ComponentRegistry

def create_test_configurations() -> List[Dict[str, Any]]:
    """Create various test configurations for baseline capture."""
    
    base_cli = {
        "name": "test-cli",
        "description": "Test CLI for logging baseline",
        "tagline": "Testing logging framework",
        "commands": {
            "test": {"desc": "Test command"}
        }
    }
    
    configurations = []
    
    # Test different logging configurations
    for env in ["development", "production"]:
        for log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            for structured in [True, False]:
                config = {
                    "package_name": f"test-{env}-{log_level.lower()}",
                    "command_name": "test-cli",
                    "display_name": "Test CLI",
                    "description": "Test configuration",
                    "environment": env,
                    "log_level": log_level,
                    "structured_logging": structured,
                    "cli": base_cli
                }
                configurations.append(config)
    
    return configurations

def capture_logging_output(config: Dict[str, Any], language: str) -> str:
    """Capture the logging template output for a given configuration and language."""
    
    # Create component registry
    registry = ComponentRegistry()
    
    # Load the logger template directly
    logger_template_path = Path("/workspace/src/goobits_cli/universal/components/logger.j2")
    with open(logger_template_path, "r") as f:
        template_content = f.read()
    
    # Create context for template rendering
    context = {
        "language": language,
        "project": {
            "name": config["package_name"],
            "command_name": config["command_name"],
            "display_name": config["display_name"],
            "description": config["description"]
        },
        "environment": config.get("environment", "development"),
        "log_level": config.get("log_level", "INFO"),
        "structured_logging": config.get("structured_logging", False)
    }
    
    # Render the template (simplified - in reality would use full engine)
    from jinja2 import Environment, BaseLoader
    env = Environment(loader=BaseLoader())
    template = env.from_string(template_content)
    
    return template.render(**context)

def save_baseline(language: str, config: Dict[str, Any], output: str) -> Path:
    """Save baseline output to file for later comparison."""
    
    baseline_dir = Path("/workspace/baselines/phase1/logging") / language
    baseline_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a unique filename based on config
    config_hash = hashlib.md5(json.dumps(config, sort_keys=True).encode()).hexdigest()[:8]
    filename = f"{config['environment']}_{config['log_level'].lower()}_{config_hash}.baseline"
    
    baseline_path = baseline_dir / filename
    
    with open(baseline_path, "w") as f:
        f.write(output)
    
    return baseline_path

def main():
    """Capture all baseline outputs."""
    
    print("📸 Phase 1: Capturing baseline logging outputs...")
    print("=" * 60)
    
    configurations = create_test_configurations()
    languages = ["python", "nodejs", "typescript", "rust"]
    
    baselines_captured = 0
    baseline_manifest = {
        "configurations": configurations,
        "languages": languages,
        "baselines": {}
    }
    
    for language in languages:
        print(f"\n🔍 Processing {language}...")
        baseline_manifest["baselines"][language] = []
        
        for config in configurations:
            try:
                # Capture output
                output = capture_logging_output(config, language)
                
                # Save baseline
                baseline_path = save_baseline(language, config, output)
                
                baseline_manifest["baselines"][language].append({
                    "config": config,
                    "path": str(baseline_path),
                    "size": len(output),
                    "hash": hashlib.sha256(output.encode()).hexdigest()
                })
                
                baselines_captured += 1
                print(f"  ✅ Captured: {baseline_path.name}")
                
            except Exception as e:
                print(f"  ❌ Failed for {config['package_name']}: {e}")
    
    # Save manifest
    manifest_path = Path("/workspace/baselines/phase1/manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(manifest_path, "w") as f:
        json.dump(baseline_manifest, f, indent=2)
    
    print(f"\n✅ Phase 1 Baseline Capture Complete!")
    print(f"  📊 Total baselines captured: {baselines_captured}")
    print(f"  📄 Manifest saved to: {manifest_path}")
    print(f"  📁 Baselines directory: /workspace/baselines/phase1/")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())