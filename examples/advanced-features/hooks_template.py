"""
Hook Template for Nested Command Demo
This shows the proposed hook naming system for deep nested commands
"""

# =============================================================================
# SIMPLE COMMANDS (Level 1) - ✅ Works Today
# =============================================================================

def on_simple(message, verbose=False):
    """Handle simple command - works perfectly in current system."""
    if verbose:
        print(f"Verbose: Processing message '{message}'")
    else:
        print(message)
    return 0


# =============================================================================  
# SINGLE-LEVEL SUBCOMMANDS (Level 2) - ⚠️ Partially Works
# =============================================================================

def on_database_users(action, format="table"):
    """
    Handle database users command.
    
    CURRENT ISSUE: 'action' argument is ignored by template generator
    Only 'format' option works correctly.
    """
    print(f"Database users action: {action}")
    print(f"Output format: {format}")
    return 0

def on_database_backup(compress=False):
    """Handle database backup - works correctly."""
    if compress:
        print("Creating compressed backup...")
    else:
        print("Creating uncompressed backup...")
    return 0


# =============================================================================
# DEEP NESTED COMMANDS (Level 3+) - ❌ Broken in Current System  
# =============================================================================

# PROPOSED: Smart hook naming with abbreviation
def on_api_users_create(username, email, admin=False, send_email=False):
    """
    PROPOSED: Handle api v1 users create command.
    
    Full path: api -> v1 -> users -> create
    Hook name: on_api_users_create (v1 omitted for brevity)
    """
    print(f"Creating user: {username} <{email}>")
    if admin:
        print("  ↳ Granting admin privileges")
    if send_email:
        print("  ↳ Sending welcome email")
    return 0

def on_api_permissions_grant(user_id, permission, expires=None):
    """
    PROPOSED: Handle api v1 users permissions grant command.
    
    Full path: api -> v1 -> users -> permissions -> grant  
    Hook name: on_api_permissions_grant (abbreviated)
    """
    print(f"Granting permission '{permission}' to user {user_id}")
    if expires:
        print(f"  ↳ Expires: {expires}")
    return 0

def on_api_permissions_revoke(user_id, permission, force=False):
    """
    PROPOSED: Handle api v1 users permissions revoke command.
    
    Full path: api -> v1 -> users -> permissions -> revoke
    Hook name: on_api_permissions_revoke (abbreviated)  
    """
    if force:
        print(f"Force revoking permission '{permission}' from user {user_id}")
    else:
        print(f"Revoking permission '{permission}' from user {user_id}")
    return 0


# =============================================================================
# ALTERNATIVE HOOK NAMING STRATEGIES (Proposed)
# =============================================================================

# Strategy 1: Full path (verbose but explicit)
def on_api_v1_users_permissions_grant_full(user_id, permission, expires=None):
    """Alternative: Full command path hook name."""
    return on_api_permissions_grant(user_id, permission, expires)

# Strategy 2: Namespace separation (clean but longer)  
def on_api__users__permissions__grant(user_id, permission, expires=None):
    """Alternative: Namespace-separated hook name."""
    return on_api_permissions_grant(user_id, permission, expires)

# Strategy 3: Generic fallback (simple but less specific)
def on_command_executed(command_path, args, options):
    """
    Generic fallback for any command without specific hook.
    
    Args:
        command_path: List of command names ['api', 'v1', 'users', 'create']
        args: Dict of positional arguments {'username': 'john', 'email': 'john@example.com'}
        options: Dict of options {'admin': True, 'send_email': False}
    """
    print(f"Executing command: {' '.join(command_path)}")
    print(f"Arguments: {args}")
    print(f"Options: {options}")
    return 0


# =============================================================================
# HOOK DISCOVERY DEMONSTRATION  
# =============================================================================

def discover_hook_for_command(command_path, available_hooks):
    """
    PROPOSED: Smart hook discovery algorithm.
    
    This demonstrates how the proposed system would find the right hook
    for any command path using multiple fallback strategies.
    """
    
    # Strategy 1: Exact match
    exact_name = f"on_{'_'.join(command_path)}"
    if exact_name in available_hooks:
        return available_hooks[exact_name]
    
    # Strategy 2: Abbreviated match (skip middle components)
    if len(command_path) > 3:
        abbrev_name = f"on_{command_path[0]}_{command_path[-2]}_{command_path[-1]}"
        if abbrev_name in available_hooks:
            return available_hooks[abbrev_name]
    
    # Strategy 3: Namespace match
    namespace_name = f"on_{'__'.join(command_path)}"
    if namespace_name in available_hooks:
        return available_hooks[namespace_name]
    
    # Strategy 4: Generic fallback
    if 'on_command_executed' in available_hooks:
        return available_hooks['on_command_executed']
    
    # No hook found
    raise HookNotFoundError(f"No hook found for command path: {command_path}")


# =============================================================================
# TESTING SCENARIOS
# =============================================================================

if __name__ == "__main__":
    # Test current working commands
    print("=== Testing Current System ===")
    on_simple("Hello World", verbose=True)
    on_database_backup(compress=True)
    
    print("\n=== Testing Proposed Deep Nesting ===")
    on_api_users_create("john_doe", "john@example.com", admin=True, send_email=True)
    on_api_permissions_grant("123", "admin", expires="2024-12-31")
    on_api_permissions_revoke("123", "read", force=True)
    
    print("\n=== Testing Hook Discovery ===")
    available_hooks = globals()
    
    try:
        # Test exact match
        hook = discover_hook_for_command(['simple'], available_hooks)
        print(f"Found hook for 'simple': {hook.__name__}")
        
        # Test abbreviated match  
        hook = discover_hook_for_command(['api', 'v1', 'users', 'create'], available_hooks)
        print(f"Found hook for deep command: {hook.__name__}")
        
    except Exception as e:
        print(f"Hook discovery failed: {e}")