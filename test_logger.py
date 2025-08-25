#!/usr/bin/env python3
"""
Test script for framework core logging functionality.
"""

import os
import sys
import tempfile
from io import StringIO
import logging
from contextlib import redirect_stdout, redirect_stderr

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

from goobits_cli.logger import setup_logging, get_logger, set_context, clear_context, update_context, get_context, remove_context_keys

def test_basic_logging():
    """Test basic logging functionality."""
    print("=== Testing Basic Logging ===")
    
    # Reset environment
    for key in ['LOG_LEVEL', 'LOG_OUTPUT', 'ENVIRONMENT']:
        if key in os.environ:
            del os.environ[key]
    
    setup_logging()
    logger = get_logger("test_basic")
    
    # Capture output
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
    
    stdout_output = stdout_capture.getvalue()
    stderr_output = stderr_capture.getvalue()
    
    print(f"STDOUT: {repr(stdout_output)}")
    print(f"STDERR: {repr(stderr_output)}")
    
    # In default mode, INFO should go to stdout, WARN/ERROR to stderr
    assert "Test info message" in stdout_output, "Info message should go to stdout"
    assert "Test warning message" in stderr_output, "Warning message should go to stderr"
    assert "Test error message" in stderr_output, "Error message should go to stderr"
    
    print("✓ Basic logging test passed")
    return True

def test_environment_variables():
    """Test environment variable handling."""
    print("\n=== Testing Environment Variables ===")
    
    # Test LOG_LEVEL
    os.environ['LOG_LEVEL'] = 'WARNING'
    setup_logging()
    logger = get_logger("test_level")
    
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        logger.info("This should not appear")
        logger.warning("This should appear")
    
    stdout_output = stdout_capture.getvalue()
    stderr_output = stderr_capture.getvalue()
    
    assert "This should not appear" not in stdout_output and "This should not appear" not in stderr_output, "Info message should be filtered out"
    assert "This should appear" in stderr_output, "Warning message should appear"
    
    print("✓ LOG_LEVEL test passed")
    
    # Test LOG_OUTPUT=stderr
    os.environ['LOG_OUTPUT'] = 'stderr'
    setup_logging()
    logger = get_logger("test_stderr")
    
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        logger.warning("All to stderr")
    
    stdout_output = stdout_capture.getvalue()
    stderr_output = stderr_capture.getvalue()
    
    assert "All to stderr" not in stdout_output, "Message should not go to stdout"
    assert "All to stderr" in stderr_output, "Message should go to stderr"
    
    print("✓ LOG_OUTPUT=stderr test passed")
    
    # Test ENVIRONMENT=production (JSON format)
    os.environ['ENVIRONMENT'] = 'production'
    setup_logging()
    logger = get_logger("test_production")
    
    stderr_capture = StringIO()
    
    with redirect_stderr(stderr_capture):
        logger.warning("Production test")
    
    stderr_output = stderr_capture.getvalue()
    
    # Should be JSON format
    import json
    try:
        log_data = json.loads(stderr_output.strip())
        assert log_data['level'] == 'WARNING', "Level should be WARNING"
        assert log_data['message'] == 'Production test', "Message should match"
        assert 'timestamp' in log_data, "Should have timestamp"
        print("✓ ENVIRONMENT=production test passed")
    except json.JSONDecodeError:
        print(f"✗ Production output is not valid JSON: {repr(stderr_output)}")
        return False
    
    return True

def test_context_management():
    """Test context management functionality."""
    print("\n=== Testing Context Management ===")
    
    # Reset environment to development mode for readable output
    os.environ['ENVIRONMENT'] = 'development'
    os.environ['LOG_OUTPUT'] = 'stderr'
    setup_logging()
    logger = get_logger("test_context")
    
    # Test setting context
    set_context(operation_id="test_123", user="test_user")
    
    stderr_capture = StringIO()
    
    with redirect_stderr(stderr_capture):
        logger.info("Message with context")
    
    stderr_output = stderr_capture.getvalue()
    
    assert "operation_id=test_123" in stderr_output, "Context should include operation_id"
    assert "user=test_user" in stderr_output, "Context should include user"
    
    print("✓ Context setting test passed")
    
    # Test updating context
    update_context(step="validation")
    
    stderr_capture = StringIO()
    
    with redirect_stderr(stderr_capture):
        logger.info("Message with updated context")
    
    stderr_output = stderr_capture.getvalue()
    
    assert "step=validation" in stderr_output, "Context should include updated step"
    assert "operation_id=test_123" in stderr_output, "Context should retain operation_id"
    
    print("✓ Context updating test passed")
    
    # Test getting context
    current_context = get_context()
    assert current_context['operation_id'] == 'test_123', "Context should contain operation_id"
    assert current_context['step'] == 'validation', "Context should contain step"
    
    print("✓ Context getting test passed")
    
    # Test removing context keys
    remove_context_keys('step')
    current_context = get_context()
    assert 'step' not in current_context, "Step should be removed from context"
    assert 'operation_id' in current_context, "operation_id should remain"
    
    print("✓ Context key removal test passed")
    
    # Test clearing context
    clear_context()
    current_context = get_context()
    assert len(current_context) == 0, "Context should be empty after clearing"
    
    print("✓ Context clearing test passed")
    
    return True

def test_file_logging():
    """Test file logging functionality."""
    print("\n=== Testing File Logging ===")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        log_file = temp_file.name
    
    try:
        os.environ['LOG_OUTPUT'] = f'file:{log_file}'
        setup_logging()
        logger = get_logger("test_file")
        
        logger.info("Test file logging")
        logger.warning("Test file warning")
        
        # Read the log file
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        assert "Test file logging" in log_content, "Info message should be in file"
        assert "Test file warning" in log_content, "Warning message should be in file"
        
        print("✓ File logging test passed")
        return True
        
    finally:
        # Clean up
        if os.path.exists(log_file):
            os.unlink(log_file)

def test_exception_handling():
    """Test exception handling in logs."""
    print("\n=== Testing Exception Handling ===")
    
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['LOG_OUTPUT'] = 'stderr'
    setup_logging()
    logger = get_logger("test_exception")
    
    stderr_capture = StringIO()
    
    try:
        with redirect_stderr(stderr_capture):
            try:
                raise ValueError("Test exception")
            except ValueError:
                logger.error("Exception occurred", exc_info=True)
        
        stderr_output = stderr_capture.getvalue()
        
        # Should be JSON format with exception info
        import json
        log_data = json.loads(stderr_output.strip())
        
        assert 'exception' in log_data, "Should contain exception info"
        assert log_data['exception']['type'] == 'ValueError', "Should capture exception type"
        assert 'Test exception' in log_data['exception']['message'], "Should capture exception message"
        assert log_data['exception']['traceback'] is not None, "Should capture traceback"
        
        print("✓ Exception handling test passed")
        return True
        
    except Exception as e:
        print(f"✗ Exception handling test failed: {e}")
        return False

def main():
    """Run all logger tests."""
    print("Testing Goobits CLI Framework Logger")
    print("=" * 50)
    
    tests = [
        test_basic_logging,
        test_environment_variables, 
        test_context_management,
        test_file_logging,
        test_exception_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} failed with exception: {e}")
    
    print(f"\n=== Framework Core Logging Test Results ===")
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