#!/usr/bin/env python3
"""Debug script to test the integration workflow."""

import tempfile
import subprocess
import sys
from pathlib import Path

# Add src to path so we can import goobits_cli
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tests.install.test_integration_workflows import IntegrationTestRunner

def debug_integration_flow():
    """Debug the integration workflow step by step."""
    print("🔍 Debugging integration workflow...")
    
    runner = IntegrationTestRunner()
    
    try:
        # Test Python minimal scenario
        result = runner.run_full_workflow_test("python", "minimal")
        
        print(f"🔄 Result: {result}")
        print(f"✅ Success: {result['success']}")
        print(f"❌ Error: {result.get('error', 'None')}")
        
        if 'phases' in result:
            for phase_name, phase_data in result['phases'].items():
                print(f"📋 Phase '{phase_name}': {phase_data}")
        
    except Exception as e:
        print(f"❌ Exception during integration flow: {e}")
        import traceback
        traceback.print_exc()
    finally:
        runner.cleanup()

if __name__ == "__main__":
    debug_integration_flow()