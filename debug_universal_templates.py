#!/usr/bin/env python3
"""
Debug Universal Template System to see why it's falling back to legacy.
"""

import sys
import tempfile
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tests.integration.test_cross_language import EndToEndIntegrationTester


def main():
    """Debug Universal Template System failure."""
    print("🔍 Debug Universal Template System Failure")
    print("=" * 60)
    
    tester = EndToEndIntegrationTester()
    
    try:
        # Create configuration
        config = tester.create_comprehensive_test_config("python", "e2e_test")
        
        # Create generator with verbose error handling
        generator = tester._get_generator("python")
        
        # Force use of proper filename to avoid legacy fallback
        all_files = generator.generate_all_files(config, "e2e_test_python.yaml", "1.0.0")
        print(f"✅ Generation successful: {len(all_files)} files")
        
    except Exception as e:
        print(f"❌ Universal Template System error: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    main()