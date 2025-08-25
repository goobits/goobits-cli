# Security Policy

## Overview

Goobits CLI Framework is designed as a development tool for creating command-line interfaces. This document outlines our security model and design decisions.

## Filesystem Access Model

### Design Decision: Full Filesystem Access

The Goobits CLI Framework **intentionally** provides full filesystem access without path sandboxing. This is a deliberate design decision based on the tool's purpose:

**Rationale:**
- Goobits is a CLI development framework, similar to tools like Yeoman, Create React App, or Cargo
- CLI developers need to read configuration files, write generated code, and access project resources anywhere on the filesystem
- Artificial path restrictions would severely limit legitimate use cases
- Users of development tools expect and require full filesystem access

**Security Model:**
- Trust boundary is at the developer level - developers using Goobits are trusted
- Generated CLIs inherit the security model appropriate for their use case
- Path validation should be implemented in the generated CLI if needed, not in the framework

### Examples of Legitimate Filesystem Operations

```python
# Reading configuration from user's home directory
config_path = Path("~/.config/myapp/config.yaml").expanduser()

# Writing generated files to project directory
output_path = Path(args.output).resolve()

# Accessing system-wide resources
system_config = Path("/etc/myapp/defaults.conf")
```

## Plugin Security

### Current Implementation

Plugins can specify dependencies that are installed via pip. This is necessary for plugin functionality but requires trust in plugin authors.

**Recommendations for Plugin Users:**
- Only install plugins from trusted sources
- Review plugin manifests before installation
- Consider using virtual environments for plugin testing

### Future Enhancements (Roadmap)

1. **Plugin Sandboxing** (Planned)
   - Isolated virtual environments per plugin
   - Resource usage limits
   - Capability-based permissions

2. **Plugin Signing** (Under Consideration)
   - Cryptographic signatures for verified plugins
   - Official plugin registry with vetted packages

## Input Validation

### Interactive Mode

The framework's interactive mode accepts user commands without restrictive validation. This is intentional:

- Interactive mode is for development and debugging
- Developers need flexibility to test various inputs
- Validation should be implemented at the command handler level

### Generated CLIs

Generated CLIs should implement appropriate input validation based on their specific requirements:

```python
# Example: Generated CLI with input validation
def handle_file_command(filepath):
    # Add validation appropriate for your use case
    if not Path(filepath).exists():
        raise ValueError(f"File not found: {filepath}")
    
    # Add sandboxing if needed for your application
    safe_path = validate_safe_path(filepath, allowed_dir="/app/data")
```

## Best Practices for Generated CLIs

When using Goobits to generate production CLIs, consider:

1. **Add Input Validation**: Validate all user inputs appropriately
2. **Implement Path Restrictions**: If your CLI should only access specific directories
3. **Use Least Privilege**: Run with minimal required permissions
4. **Audit Dependencies**: Review all dependencies in generated package files
5. **Security Testing**: Include security tests in your CI/CD pipeline

## Reporting Security Issues

If you discover a security vulnerability in the Goobits CLI Framework:

1. **Do NOT** create a public GitHub issue
2. Email security concerns to: security@goobits.dev
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We aim to respond to security reports within 48 hours.

## Security Updates

Security updates are released as:
- **Critical**: Immediate patch release (x.x.N+1)
- **High**: Next minor release (x.N+1.0)
- **Medium/Low**: Next major release (N+1.0.0)

Subscribe to security announcements:
- GitHub: Watch the repository for releases
- PyPI: Monitor for new versions

## Compliance

The Goobits CLI Framework:
- Does not collect or transmit user data
- Does not require network access for core functionality
- Operates entirely on local resources
- Respects system security policies

## Version Support

| Version | Support Status | Security Updates |
|---------|---------------|------------------|
| 3.x     | Active        | ✅ Yes           |
| 2.x     | Maintenance   | Critical only    |
| 1.x     | End of Life   | ❌ No            |

---

Last Updated: 2024
Security Contact: security@goobits.dev