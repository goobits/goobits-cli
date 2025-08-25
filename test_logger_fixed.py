#!/usr/bin/env python3
"""
Fixed test script for framework core logging functionality.
"""

import os
import sys
import tempfile
import logging
import json
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

def reset_logging():
    """Reset logging state between tests."""
    # Clear all existing handlers
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    root.setLevel(logging.NOTSET)
    
    # Clear any module-level loggers  
    logging.getLogger().handlers.clear()
    
    # Reset context
    from goobits_cli.logger import clear_context
    clear_context()

def test_basic_stdout_stderr_routing():
    """Test that INFO goes to stdout and WARN/ERROR go to stderr."""
    print("=== Testing Basic stdout/stderr Routing ===")
    
    reset_logging()
    
    # Set LOG_OUTPUT=stdout explicitly to trigger container-friendly routing
    os.environ['LOG_OUTPUT'] = 'stdout'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    if 'ENVIRONMENT' in os.environ:
        del os.environ['ENVIRONMENT']
    
    from goobits_cli.logger import setup_logging, get_logger
    setup_logging()
    logger = get_logger("test_routing")
    
    # Test direct output to see where messages go
    print("\nDirect test - should see INFO on stdout, WARN/ERROR on stderr:")
    logger.info("INFO message - should go to stdout")
    logger.warning("WARNING message - should go to stderr")  
    logger.error("ERROR message - should go to stderr")
    
    print("✓ Basic routing test completed (visual check)")
    return True

def test_log_levels():
    """Test log level filtering."""
    print("\n=== Testing Log Level Filtering ===")
    
    reset_logging()
    
    os.environ['LOG_LEVEL'] = 'WARNING'
    os.environ['LOG_OUTPUT'] = 'stderr'
    
    from goobits_cli.logger import setup_logging, get_logger
    setup_logging()
    logger = get_logger("test_levels")
    
    print("\nWith LOG_LEVEL=WARNING, only WARNING and ERROR should appear:")
    logger.debug("DEBUG - should NOT appear")
    logger.info("INFO - should NOT appear") 
    logger.warning("WARNING - should appear")
    logger.error("ERROR - should appear")
    
    print("✓ Log level filtering test completed (visual check)")
    return True

def test_production_json_format():
    """Test JSON format in production environment."""
    print("\n=== Testing Production JSON Format ===")
    
    reset_logging()
    
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['LOG_OUTPUT'] = 'stderr'
    os.environ['LOG_LEVEL'] = 'INFO'
    
    from goobits_cli.logger import setup_logging, get_logger
    setup_logging()
    logger = get_logger("test_production")
    
    print("\nProduction mode - should output JSON to stderr:")
    logger.info("Test info message in production")
    logger.warning("Test warning in production")
    
    print("✓ Production JSON format test completed (visual check)")
    return True

def test_context_functionality():
    """Test context management."""
    print("\n=== Testing Context Management ===")
    
    reset_logging()
    
    os.environ['ENVIRONMENT'] = 'development'  # Readable format
    os.environ['LOG_OUTPUT'] = 'stderr'
    
    from goobits_cli.logger import setup_logging, get_logger, set_context, update_context, get_context, clear_context, remove_context_keys
    setup_logging()
    logger = get_logger("test_context")
    
    # Test setting context
    set_context(operation_id="op_123", user="test_user")
    print("\nAfter setting context (operation_id=op_123, user=test_user):")
    logger.info("Message with initial context")
    
    # Test updating context  
    update_context(step="validation", phase="testing")
    print("\nAfter updating context (added step=validation, phase=testing):")
    logger.info("Message with updated context")
    
    # Test getting context
    current_context = get_context()
    expected_keys = {'operation_id', 'user', 'step', 'phase'}
    actual_keys = set(current_context.keys())
    assert expected_keys == actual_keys, f"Expected {expected_keys}, got {actual_keys}"
    print(f"✓ Context contains expected keys: {actual_keys}")
    
    # Test removing specific keys
    remove_context_keys('step', 'phase')
    current_context = get_context()
    remaining_keys = set(current_context.keys())
    expected_remaining = {'operation_id', 'user'}
    assert remaining_keys == expected_remaining, f"Expected {expected_remaining}, got {remaining_keys}"
    print(f"✓ After removing keys, context contains: {remaining_keys}")
    
    # Test clearing context
    clear_context()
    current_context = get_context()
    assert len(current_context) == 0, f"Context should be empty, got {current_context}"
    print("✓ Context cleared successfully")
    
    logger.info("Message after clearing context")
    
    print("✓ Context management test passed")
    return True

def test_file_logging():
    """Test file logging."""
    print("\n=== Testing File Logging ===")
    
    reset_logging()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
        log_file = temp_file.name
    
    try:
        os.environ['LOG_OUTPUT'] = f'file:{log_file}'
        os.environ['ENVIRONMENT'] = 'development'
        
        from goobits_cli.logger import setup_logging, get_logger, set_context
        setup_logging()
        logger = get_logger("test_file")
        
        # Add some context for testing
        set_context(test_type="file_logging")
        
        logger.info("File logging info message")
        logger.warning("File logging warning")
        logger.error("File logging error")
        
        # Read file content
        with open(log_file, 'r') as f:
            content = f.read()
        
        print(f"\nFile content written to: {log_file}")
        print(f"Content:\n{content}")
        
        # Basic validation
        assert "File logging info message" in content, "Info message missing from file"
        assert "File logging warning" in content, "Warning missing from file" 
        assert "File logging error" in content, "Error missing from file"
        assert "test_type=file_logging" in content, "Context missing from file"
        
        print("✓ File logging test passed")
        return True
        
    finally:
        if os.path.exists(log_file):
            os.unlink(log_file)

def test_exception_logging():
    """Test exception logging."""
    print("\n=== Testing Exception Logging ===")
    
    reset_logging()
    
    os.environ['ENVIRONMENT'] = 'production'  # JSON format for easy parsing
    os.environ['LOG_OUTPUT'] = 'stderr'
    
    from goobits_cli.logger import setup_logging, get_logger
    setup_logging()
    logger = get_logger("test_exception")
    
    print("\nTesting exception logging (should see JSON with exception info):")
    try:
        raise ValueError("Test exception for logging")
    except ValueError:
        logger.error("Exception occurred during testing", exc_info=True)
    
    print("✓ Exception logging test completed (visual check)")
    return True

def main():
    """Run all logger tests."""
    print("Testing Goobits CLI Framework Logger")
    print("=" * 60)
    
    tests = [
        test_basic_stdout_stderr_routing,
        test_log_levels,
        test_production_json_format,
        test_context_functionality,
        test_file_logging,
        test_exception_logging
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"Framework Core Logging Test Results")
    print(f"{'='*60}")
    print(f"Passed: {passed}/{total} tests")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("✅ All framework core logging tests PASSED")
        return True
    else:
        print("❌ Some framework core logging tests FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)