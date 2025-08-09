#!/usr/bin/env python3
"""Test script for interactive mode integration."""

import subprocess
import sys
import time
import os

def test_interactive_flag():
    """Test the --interactive flag integration."""
    print("Testing interactive mode integration...")
    
    # Test 1: Check if --interactive flag is recognized
    print("\n1. Testing --interactive flag recognition...")
    try:
        result = subprocess.run([
            sys.executable, "cli.py", "--interactive"
        ], timeout=3, capture_output=True, text=True, input="\n")
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
    except subprocess.TimeoutExpired:
        print("Interactive mode started (process had to be terminated due to timeout)")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Check if interactive mode help works
    print("\n2. Testing CLI help shows --interactive flag...")
    try:
        result = subprocess.run([
            sys.executable, "cli.py", "--help"
        ], capture_output=True, text=True)
        
        if "--interactive" in result.stdout:
            print("✅ --interactive flag found in help")
        else:
            print("❌ --interactive flag NOT found in help")
            
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: Direct module test
    print("\n3. Testing interactive mode module directly...")
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            "import enhanced_interactive_mode; enhanced_interactive_mode.start_enhanced_interactive()"
        ], timeout=2, capture_output=True, text=True, input="exit\n")
        
        if "Enhanced Interactive Mode" in result.stdout:
            print("✅ Interactive mode module works directly")
        else:
            print("❌ Interactive mode module failed")
            print(f"Output: {result.stdout}")
            
    except subprocess.TimeoutExpired:
        print("✅ Interactive mode started (had to timeout)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_interactive_flag()