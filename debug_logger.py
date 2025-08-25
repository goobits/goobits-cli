#!/usr/bin/env python3
"""
Debug script for framework logging functionality.
"""

import os
import sys
import tempfile
import logging

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

from goobits_cli.logger import setup_logging, get_logger, set_context, clear_context

def debug_basic_logging():
    """Debug basic logging to understand the issue."""
    print("=== Debugging Basic Logging ===")
    
    # Reset environment
    for key in ['LOG_LEVEL', 'LOG_OUTPUT', 'ENVIRONMENT']:
        if key in os.environ:
            del os.environ[key]
    
    print("Environment reset, setting up logging...")
    setup_logging()
    logger = get_logger("debug_test")
    
    print("Sending test messages...")
    logger.info("Debug info message")
    logger.warning("Debug warning message") 
    logger.error("Debug error message")
    
    print("Messages sent directly to console - should appear above")

def debug_environment_production():
    """Debug production environment logging."""
    print("\n=== Debugging Production Environment ===")
    
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['LOG_OUTPUT'] = 'stderr'
    
    setup_logging()
    logger = get_logger("debug_production")
    
    print("Sending production message to stderr...")
    logger.warning("Production warning message")
    print("Production message sent")

def debug_context():
    """Debug context management."""
    print("\n=== Debugging Context Management ===")
    
    os.environ['ENVIRONMENT'] = 'development'
    
    setup_logging()
    logger = get_logger("debug_context")
    
    set_context(test_id="123", component="debug")
    print("Context set, sending message...")
    logger.info("Message with context")
    print("Message with context sent")

def debug_file_logging():
    """Debug file logging."""
    print("\n=== Debugging File Logging ===")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
        log_file = temp_file.name
    
    print(f"Log file: {log_file}")
    
    os.environ['LOG_OUTPUT'] = f'file:{log_file}'
    
    setup_logging()
    logger = get_logger("debug_file")
    
    logger.info("File logging test message")
    logger.warning("File logging warning")
    
    # Read and display file content
    with open(log_file, 'r') as f:
        content = f.read()
    
    print(f"File content:\n{content}")
    
    # Clean up
    os.unlink(log_file)

def main():
    print("Debugging Goobits CLI Framework Logger")
    print("=" * 50)
    
    debug_basic_logging()
    debug_environment_production()
    debug_context() 
    debug_file_logging()

if __name__ == "__main__":
    main()