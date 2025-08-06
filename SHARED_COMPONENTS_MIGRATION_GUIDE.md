# Shared Components Migration Guide
## Adopting Shared Components in goobits-cli Generators

*Generated: 2025-08-06*
*Version: Phase 2 Week 8*

## Overview

This guide provides step-by-step instructions for adopting and integrating the newly available shared components in the goobits-cli multi-language generator framework. The shared components eliminate code duplication and provide consistent functionality across Python, Node.js, TypeScript, and Rust generators.

## Table of Contents

1. [Shared Components Overview](#shared-components-overview)
2. [Integration Patterns](#integration-patterns)
3. [Component-Specific Migration](#component-specific-migration)
4. [Language-Specific Adaptations](#language-specific-adaptations)
5. [Testing Integration](#testing-integration)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Shared Components Overview

### Available Shared Components

| Component | Purpose | Lines | Dependencies |
|-----------|---------|-------|--------------|
| `completion_engine.py.j2` | Universal shell completion | 346 | PyYAML |
| `progress_helper.py.j2` | Progress indicators & feedback | 323 | Rich (optional) |
| `config_manager.py.j2` | Configuration management | 449 | PyYAML, tomli (optional) |
| `prompts_helper.py.j2` | Interactive user prompts | 390 | Rich (optional) |
| `completion_helper.py.j2` | Shell completion generators | 218 | None |
| `builtin_commands.py.j2` | Standard CLI commands | 2,140 | Click, requests |
| `cli_template.py.j2` | Main CLI structure | 1,071 | Click |
| `setup_template.sh.j2` | Installation scripts | 115 | bash |

### Component Architecture

```
src/goobits_cli/templates/
├── completion_engine.py.j2      # Universal completion system
├── progress_helper.py.j2        # Progress & feedback utilities  
├── config_manager.py.j2         # Configuration management
├── prompts_helper.py.j2         # Interactive prompts
├── completion_helper.py.j2      # Shell completion support
├── builtin_commands.py.j2       # Standard commands
├── cli_template.py.j2           # Main CLI template
└── setup_template.sh.j2         # Installation script
```

## Integration Patterns

### 1. Template Inclusion Pattern

The most straightforward way to integrate shared components:

```jinja2
{# In your language-specific template #}
{% include 'shared_component.py.j2' %}
```

**Example: Adding configuration management**
```jinja2
{# In your main CLI template #}
{% include 'config_manager.py.j2' %}

# Your CLI-specific code continues here...
```

### 2. Variable Context Pattern

Pass specific variables to customize shared components:

```jinja2
{# Set context variables before inclusion #}
{% set component_config = {
    'package_name': package_name,
    'display_name': display_name,
    'enable_async': true
} %}
{% include 'shared_component.py.j2' %}
```

### 3. Conditional Inclusion Pattern

Include components based on configuration:

```jinja2
{% if cli.enable_completion %}
{% include 'completion_engine.py.j2' %}
{% endif %}

{% if cli.enable_progress %}
{% include 'progress_helper.py.j2' %}
{% endif %}
```

### 4. Override Pattern

Customize shared components for specific needs:

```jinja2
{# Define overrides before inclusion #}
{% set progress_spinner_default = 'dots2' %}
{% set config_file_extension = '.toml' %}

{% include 'progress_helper.py.j2' %}
```

## Component-Specific Migration

### Completion Engine Integration

**Purpose:** Universal shell completion that reads goobits.yaml at runtime

**Migration Steps:**

1. **Include the completion engine:**
```jinja2
{% include 'completion_engine.py.j2' %}
```

2. **Add completion command to your CLI:**
```python
@cli.command(hidden=True)
@click.argument('shell')
@click.argument('current_line') 
@click.argument('cursor_pos', required=False)
def completion(shell, current_line, cursor_pos):
    """Generate shell completions"""
    engine = CompletionEngine()
    completions = engine.get_completions(shell, current_line, cursor_pos)
    for completion in completions:
        click.echo(completion)
```

3. **Generate shell completion scripts:**
```bash
# The completion helper will generate scripts for:
eval "$(your-cli completion bash)"  # Bash
eval "$(your-cli completion zsh)"   # Zsh  
your-cli completion fish | source   # Fish
```

### Progress Helper Integration

**Purpose:** Rich-based progress indicators with graceful fallbacks

**Migration Steps:**

1. **Include progress helper:**
```jinja2
{% include 'progress_helper.py.j2' %}
```

2. **Use in your commands:**
```python
from progress_helper import spinner, progress_bar, print_success

@cli.command()
def long_task():
    with spinner("Processing data..."):
        # Your long-running task
        time.sleep(2)
    
    print_success("Task completed!")

@cli.command()  
def batch_process():
    items = range(100)
    with progress_bar("Processing items", total=len(items)) as (progress, task_id):
        for item in items:
            # Process item
            time.sleep(0.1)
            progress.update(task_id, advance=1)
```

3. **Add optional dependency:**
```python
# In your setup.py/pyproject.toml
extras_require = {
    'progress': ['rich>=10.0.0'],
}
```

### Configuration Manager Integration

**Purpose:** Cross-platform configuration with multiple format support

**Migration Steps:**

1. **Include config manager:**
```jinja2
{% include 'config_manager.py.j2' %}
```

2. **Use in your CLI:**
```python
from config_manager import get_config

@cli.command()
@click.option('--config-key', help='Configuration key to retrieve')
def config(config_key):
    config_mgr = get_config()
    if config_key:
        value = config_mgr.get(config_key)
        click.echo(f"{config_key}: {value}")
    else:
        # Show all config
        config_data = config_mgr.load()
        click.echo(json.dumps(config_data, indent=2))
```

3. **Support multiple config formats:**
```yaml
# .your-clirc.yaml
api:
  endpoint: https://api.example.com
  timeout: 30
features:
  enable_colors: true
  max_retries: 3
```

```json
// .your-clirc.json
{
  "api": {
    "endpoint": "https://api.example.com",
    "timeout": 30
  },
  "features": {
    "enable_colors": true,
    "max_retries": 3
  }
}
```

### Prompts Helper Integration

**Purpose:** Interactive prompts with validation and Rich support

**Migration Steps:**

1. **Include prompts helper:**
```jinja2
{% include 'prompts_helper.py.j2' %}
```

2. **Use interactive prompts:**
```python
from prompts_helper import (
    prompt_text, prompt_password, prompt_choice, 
    prompt_confirm, prompt_multiline
)

@cli.command()
def interactive_setup():
    # Text input with validation
    name = prompt_text(
        "Enter your name",
        validator=lambda x: len(x) > 0,
        error_message="Name cannot be empty"
    )
    
    # Password input
    password = prompt_password("Enter password")
    
    # Multiple choice
    option = prompt_choice(
        "Choose an option",
        choices=["option1", "option2", "option3"],
        default="option1"
    )
    
    # Confirmation
    confirmed = prompt_confirm("Continue with setup?", default=True)
```

### Built-in Commands Integration

**Purpose:** Standard CLI commands (help, version, upgrade, etc.)

**Migration Steps:**

1. **Include built-in commands:**
```jinja2
{% include 'builtin_commands.py.j2' %}
```

2. **Register commands with your CLI:**
```python
# Commands are automatically registered if you include the template
# Customize by setting variables before inclusion:

{% set enable_upgrade_command = true %}
{% set enable_daemon_commands = true %}  
{% set enable_plugin_system = false %}

{% include 'builtin_commands.py.j2' %}
```

## Language-Specific Adaptations

### Node.js/JavaScript Integration

For Node.js generators, shared Python components need adaptation:

```javascript
// Adapted from config_manager.py.j2
const ConfigManager = require('./lib/config-manager');

class CLIConfigManager extends ConfigManager {
    constructor() {
        super();
        this.packageName = '{{ package_name }}';
        this.configFileName = 'config.json';
    }
    
    async getConfigDir() {
        const os = require('os');
        const path = require('path');
        
        if (process.platform === 'win32') {
            return path.join(os.homedir(), 'AppData', 'Local', this.packageName);
        } else if (process.platform === 'darwin') {
            return path.join(os.homedir(), 'Library', 'Application Support', this.packageName);
        } else {
            return path.join(os.homedir(), '.config', this.packageName);
        }
    }
}
```

### TypeScript Integration

TypeScript adaptations add type safety:

```typescript
// Adapted from progress_helper.py.j2
interface ProgressOptions {
    description: string;
    total?: number;
    showTime?: boolean;
    showPercentage?: boolean;
}

class ProgressHelper {
    private hasRich: boolean = false;
    
    constructor() {
        try {
            // Check if CLI progress library is available
            require('cli-progress');
            this.hasRich = true;
        } catch {
            this.hasRich = false;
        }
    }
    
    async spinner<T>(text: string, operation: () => Promise<T>): Promise<T> {
        if (!this.hasRich) {
            process.stdout.write(`${text}...`);
            try {
                const result = await operation();
                console.log(' ✓');
                return result;
            } catch (error) {
                console.log(' ✗');
                throw error;
            }
        }
        
        // Use cli-progress spinner
        // Implementation details...
    }
}
```

### Rust Integration  

Rust adaptations focus on memory safety and Result types:

```rust
// Adapted from config_manager.py.j2
use std::path::PathBuf;
use serde_json::Value;

#[derive(Debug)]
pub enum ConfigError {
    IoError(std::io::Error),
    ParseError(serde_json::Error),
    ValidationError(String),
}

pub struct ConfigManager {
    package_name: String,
    config_path: Option<PathBuf>,
}

impl ConfigManager {
    pub fn new() -> Self {
        Self {
            package_name: "{{ package_name }}".to_string(),
            config_path: None,
        }
    }
    
    pub fn get_config_dir(&self) -> Result<PathBuf, ConfigError> {
        let home = dirs::home_dir()
            .ok_or_else(|| ConfigError::ValidationError("Cannot find home directory".to_string()))?;
            
        #[cfg(target_os = "windows")]
        return Ok(home.join("AppData").join("Local").join(&self.package_name));
        
        #[cfg(target_os = "macos")]
        return Ok(home.join("Library").join("Application Support").join(&self.package_name));
        
        #[cfg(not(any(target_os = "windows", target_os = "macos")))]
        return Ok(home.join(".config").join(&self.package_name));
    }
    
    pub fn load(&mut self) -> Result<Value, ConfigError> {
        let config_path = self.get_config_path()?;
        
        if !config_path.exists() {
            return Ok(self.get_defaults());
        }
        
        let contents = std::fs::read_to_string(&config_path)
            .map_err(ConfigError::IoError)?;
            
        let config: Value = serde_json::from_str(&contents)
            .map_err(ConfigError::ParseError)?;
            
        Ok(config)
    }
}
```

## Testing Integration

### Unit Testing Shared Components

When using shared components, add tests to verify integration:

```python
# test_shared_components.py
import pytest
from unittest.mock import patch, MagicMock

def test_completion_engine_integration():
    """Test that completion engine integrates correctly"""
    from your_cli.completion_engine import CompletionEngine
    
    engine = CompletionEngine()
    completions = engine.get_completions('bash', 'your-cli he', None)
    assert 'help' in completions

def test_config_manager_integration():
    """Test configuration manager integration"""
    from your_cli.config_manager import get_config
    
    config_mgr = get_config()
    config_mgr.set('test.key', 'test_value')
    assert config_mgr.get('test.key') == 'test_value'

@patch('your_cli.progress_helper.HAS_RICH', False)
def test_progress_helper_fallback():
    """Test progress helper fallback when Rich not available"""
    from your_cli.progress_helper import get_progress_helper
    
    helper = get_progress_helper()
    with helper.spinner("Testing..."):
        pass  # Should not raise exception
```

### Integration Testing

Test the complete workflow with shared components:

```python
def test_full_cli_with_shared_components():
    """Test complete CLI functionality with all shared components"""
    from click.testing import CliRunner
    from your_cli.main import cli
    
    runner = CliRunner()
    
    # Test completion integration
    result = runner.invoke(cli, ['completion', 'bash', 'your-cli he'])
    assert result.exit_code == 0
    assert 'help' in result.output
    
    # Test config integration
    result = runner.invoke(cli, ['config', '--set', 'test.key=value'])
    assert result.exit_code == 0
    
    # Test progress integration in commands
    result = runner.invoke(cli, ['some-long-command'])
    assert result.exit_code == 0
```

## Best Practices

### 1. Dependency Management

**Graceful Degradation:**
```jinja2
{# Always check for optional dependencies #}
{% if enable_rich_features %}
try:
    from rich.console import Console
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
{% endif %}
```

**Clear Error Messages:**
```python
if not HAS_RICH and feature_requires_rich:
    raise DependencyMissingError(
        'rich', 
        'advanced progress indicators',
        'pip install rich'
    )
```

### 2. Configuration Consistency

**Use Consistent Variable Names:**
```jinja2
{# Always use these standard variables #}
{{ package_name }}      # Python package name
{{ display_name }}      # Human-readable name  
{{ version }}           # Package version
{{ description }}       # Package description
```

**Validate Configuration:**
```python
def validate_shared_component_config(config):
    required_fields = ['package_name', 'display_name']
    for field in required_fields:
        if field not in config:
            raise ConfigValidationError(f"Missing required field: {field}")
```

### 3. Error Handling

**Use Shared Error Classes:**
```python
# Inherit from shared base classes
class YourCLIError(ConfigError):
    """CLI-specific configuration error"""
    pass
```

**Provide Helpful Suggestions:**
```python
try:
    config_mgr.load()
except ConfigFileError as e:
    click.echo(f"Error: {e.message}", err=True)
    if e.suggestion:
        click.echo(f"Suggestion: {e.suggestion}", err=True)
    sys.exit(1)
```

### 4. Documentation Integration

**Document Shared Features:**
```python
@cli.command()
@click.option('--config', help='Configuration file path (supports JSON, YAML, TOML)')
def my_command(config):
    """
    My command with enhanced configuration support.
    
    Configuration is loaded from multiple sources in order:
    1. Command line options
    2. Configuration file (if specified)  
    3. RC files (.myapp-rc.json, .myapp-rc.yaml, etc.)
    4. Environment variables (MYAPP_*)
    5. Default values
    """
    pass
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ImportError: No module named 'shared_component'`

**Solution:** Ensure shared components are included in your template:
```jinja2
{% include 'shared_component.py.j2' %}
```

#### 2. Variable Not Found Errors

**Problem:** `jinja2.exceptions.UndefinedError: 'variable_name' is undefined`

**Solution:** Set required variables before inclusion:
```jinja2
{% set package_name = package_name or 'default-name' %}
{% include 'config_manager.py.j2' %}
```

#### 3. Dependency Conflicts

**Problem:** Rich/PyYAML version conflicts

**Solution:** Use optional dependencies and fallbacks:
```python
try:
    from rich.console import Console
    console = Console()
except ImportError:
    console = None
    
def print_message(message):
    if console:
        console.print(message)
    else:
        print(message)
```

#### 4. Configuration Not Loading

**Problem:** Configuration manager not finding config files

**Solution:** Check search paths and permissions:
```python
config_mgr = get_config()
config_path = config_mgr.get_config_path()
print(f"Looking for config at: {config_path}")
print(f"Exists: {config_path.exists()}")
print(f"Readable: {os.access(config_path, os.R_OK)}")
```

### Debug Mode

Enable debug logging to troubleshoot shared components:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Shared components will log their operations
config_mgr = get_config()
config_mgr.load()  # Will log config search paths and operations
```

## Migration Checklist

### Pre-Migration

- [ ] Review current CLI implementation
- [ ] Identify components that could use shared functionality
- [ ] Plan integration approach (gradual vs. complete)
- [ ] Backup existing working implementation

### During Migration

- [ ] Include appropriate shared components
- [ ] Set required context variables
- [ ] Test component integration individually  
- [ ] Update dependencies in setup.py/pyproject.toml
- [ ] Add optional dependency handling

### Post-Migration

- [ ] Run complete test suite
- [ ] Verify CLI behavior unchanged
- [ ] Update documentation
- [ ] Test installation process
- [ ] Validate cross-platform compatibility

### Validation

- [ ] Generate CLI with new components
- [ ] Test all commands and options
- [ ] Verify completion system works
- [ ] Test configuration management
- [ ] Validate progress indicators
- [ ] Check error handling and messages

## Support and Resources

### Getting Help

1. **Check the Integration Report:** Review `PHASE_2_INTEGRATION_REPORT.md` for detailed technical information
2. **Test Examples:** Look at existing generator implementations in `src/goobits_cli/generators/`
3. **Template Examples:** Examine `src/goobits_cli/templates/` for usage patterns
4. **Run Tests:** Execute `pytest src/tests/` to see working examples

### Future Enhancements

The shared components will continue to evolve. Future improvements may include:

- Additional utility components
- Enhanced language-specific adaptations
- Performance optimizations
- Extended configuration format support
- Advanced completion features

---

*This migration guide reflects the current state of shared components as of Phase 2 completion. For the latest updates, refer to the project repository and documentation.*