# Vulture whitelist for false positives
# Add any functions, classes, or variables that are incorrectly flagged as dead code

# Python context manager protocol - required by Python spec
__exit__
__aexit__
exc_type  # Context manager parameter
exc_val   # Context manager parameter  
exc_tb    # Context manager parameter

# cmd module completion interface - required by Python cmd module
begidx    # readline completion parameter
endidx    # readline completion parameter

# Import-for-detection patterns - standard Python idiom for optional dependencies
Console   # Rich availability check
Progress  # Rich progress check
Status    # Rich status check

# Self-hosting detection - critical for framework dogfooding capability
goobits_main  # Framework self-hosting detection