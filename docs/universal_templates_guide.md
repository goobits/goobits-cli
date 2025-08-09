# Universal Template System Guide

The Universal Template System is a production-ready feature of Goobits CLI Framework v2.0 that provides consistent CLI generation across all supported languages from a single template source. This guide explains how to use, customize, and extend the universal template system.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [How It Works](#how-it-works)
4. [Using Universal Templates](#using-universal-templates)
5. [Template Architecture](#template-architecture)
6. [Language Renderers](#language-renderers)
7. [Component System](#component-system)
8. [Performance Benefits](#performance-benefits)
9. [Customization](#customization)
10. [Troubleshooting](#troubleshooting)

## Overview

The Universal Template System transforms a single YAML configuration into high-quality, language-specific CLI implementations. Instead of maintaining separate templates for each language, the system uses:

- **Intermediate Representation (IR)**: Language-agnostic data structures
- **Universal Components**: Reusable template pieces
- **Language Renderers**: Language-specific output generators
- **Performance Optimization**: Lazy loading, caching, and memory management

### Benefits

- ✅ **Consistency**: Identical behavior across all languages
- ✅ **Performance**: <100ms startup times with optimization
- ✅ **Maintainability**: Single source of truth for templates
- ✅ **Extensibility**: Easy to add new languages and components
- ✅ **Reliability**: Production-tested with comprehensive validation

## Quick Start

### Enable Universal Templates

```bash
# Generate CLI with universal templates (recommended)
goobits build --universal-templates

# Verify universal template usage
goobits build --universal-templates --verbose
```

### Compare with Legacy Templates

```bash
# Generate with legacy templates
goobits build

# Compare output (same functionality, different generation approach)
diff -r generated-universal/ generated-legacy/
```

## How It Works

### 1. Configuration Processing

```yaml
# goobits.yaml
language: python  # Target language
cli:
  name: mycli
  commands:
    greet:
      desc: "Greet someone"
      args:
        - name: name
          required: true
```

### 2. Intermediate Representation (IR) Generation

The universal template engine converts your configuration into language-agnostic data structures:

```python
# Simplified IR structure
UniversalCLI(
    name="mycli",
    commands=[
        UniversalCommand(
            name="greet",
            description="Greet someone",
            arguments=[
                UniversalArgument(name="name", required=True)
            ]
        )
    ]
)
```

### 3. Language-Specific Rendering

The IR is then rendered using language-specific renderers:

```python
# Python renderer output
@click.command()
@click.argument('name', required=True)
def greet(name):
    """Greet someone"""
    # Hook call
    
# Node.js renderer output  
program
  .command('greet <name>')
  .description('Greet someone')
  .action(async (name) => {
    // Hook call
  });
```

## Using Universal Templates

### Basic Usage

1. **Configure your CLI** in `goobits.yaml` (same as before)
2. **Generate with universal templates**:
   ```bash
   goobits build --universal-templates
   ```
3. **Implement hooks** in your target language as usual

### Advanced Configuration

Enable additional universal template features:

```yaml
# goobits.yaml
language: python

# Universal template specific settings
universal_templates:
  enabled: true
  performance_optimization: true
  component_caching: true
  lazy_loading: true

cli:
  name: mycli
  # Standard CLI configuration...
```

### Fallback Behavior

Universal templates automatically fall back to legacy templates if:

- A specific language feature isn't supported yet
- Custom template filters are needed
- Debugging template generation issues

```bash
# Force legacy template usage
goobits build --no-universal-templates

# Or simply
goobits build
```

## Template Architecture

### System Overview

```
Universal Template System
├── template_engine.py      # Core engine
├── component_registry.py   # Component management
├── components/             # Universal components
│   ├── command_handler.j2
│   ├── config_manager.j2
│   ├── error_handler.j2
│   └── hook_system.j2
├── renderers/              # Language renderers
│   ├── python_renderer.py
│   ├── nodejs_renderer.py
│   └── typescript_renderer.py
└── performance/            # Performance optimization
    ├── cache.py
    ├── lazy_loader.py
    └── optimizer.py
```

### Core Components

**Template Engine (`template_engine.py`)**
- Orchestrates the entire generation process
- Manages IR creation and renderer selection
- Handles error recovery and fallback mechanisms

**Component Registry (`component_registry.py`)**
- Manages universal template components
- Provides component discovery and loading
- Handles component dependencies

**Performance Framework**
- Implements lazy loading for better startup times
- Provides template caching for faster regeneration
- Monitors memory usage and optimization opportunities

## Language Renderers

### Python Renderer

**File**: `renderers/python_renderer.py`

**Features**:
- Click framework integration
- Python-specific formatting (snake_case, docstrings)
- Virtual environment and packaging support
- Performance optimization for Python startup

**Example Output**:
```python
#!/usr/bin/env python3
"""Generated CLI using Goobits CLI Framework"""

import click
from typing import Optional

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """My CLI Application"""
    pass

@cli.command()
@click.argument('name', required=True)
@click.option('--greeting', default='Hello', help='Greeting style')
def greet(name: str, greeting: str):
    """Greet someone"""
    from app_hooks import on_greet
    on_greet(name=name, greeting=greeting)

if __name__ == '__main__':
    cli()
```

### Node.js Renderer

**File**: `renderers/nodejs_renderer.py`

**Features**:
- Commander.js framework integration
- ES Module support
- npm package structure
- Async/await hook integration

**Example Output**:
```javascript
#!/usr/bin/env node
import { Command } from 'commander';
import { onGreet } from './app_hooks.js';

const program = new Command();

program
  .name('mycli')
  .description('My CLI Application')
  .version('1.0.0');

program
  .command('greet <name>')
  .description('Greet someone')
  .option('--greeting <type>', 'Greeting style', 'Hello')
  .action(async (name, options) => {
    await onGreet({ name, ...options });
  });

program.parse();
```

### TypeScript Renderer

**File**: `renderers/typescript_renderer.py`

**Features**:
- Full TypeScript type definitions
- Commander.js with proper typing
- Compilation configuration
- Interface generation for hooks

**Example Output**:
```typescript
#!/usr/bin/env node
import { Command } from 'commander';
import { onGreet, GreetArgs } from './app_hooks.js';

const program = new Command();

interface CliOptions {
  greeting?: string;
}

program
  .name('mycli')
  .description('My CLI Application')
  .version('1.0.0');

program
  .command('greet <name>')
  .description('Greet someone')
  .option('--greeting <type>', 'Greeting style', 'Hello')
  .action(async (name: string, options: CliOptions) => {
    const args: GreetArgs = { name, ...options };
    await onGreet(args);
  });

program.parse();
```

## Component System

### Universal Components

Components are reusable template pieces that work across all languages:

**Command Handler (`components/command_handler.j2`)**
```jinja2
{# Universal command handler template #}
{% macro render_command(command, language) %}
  {% if language == 'python' %}
    @cli.command()
    {% for arg in command.arguments %}
    @click.argument('{{ arg.name }}', required={{ arg.required|lower }})
    {% endfor %}
    def {{ command.name }}({{ command.arguments|map(attribute='name')|join(', ') }}):
        """{{ command.description }}"""
        from app_hooks import on_{{ command.name|camel_case }}
        on_{{ command.name|camel_case }}({{ command.arguments|map(attribute='name')|join('=', ', ') }})
  {% elif language == 'nodejs' %}
    program
      .command('{{ command.name }}{% for arg in command.arguments %} <{{ arg.name }}>{% endfor %}')
      .description('{{ command.description }}')
      .action(async ({{ command.arguments|map(attribute='name')|join(', ') }}) => {
        const { on{{ command.name|pascal_case }} } = await import('./app_hooks.js');
        await on{{ command.name|pascal_case }}({ {{ command.arguments|map(attribute='name')|join(', ') }} });
      });
  {% endif %}
{% endmacro %}
```

**Config Manager (`components/config_manager.j2`)**
```jinja2
{# Universal configuration management #}
{% macro render_config_loader(language) %}
  {% if language == 'python' %}
    import json
    import os
    from pathlib import Path
    
    def load_config():
        config_path = Path.home() / '.{{ cli.name }}' / 'config.json'
        if config_path.exists():
            return json.loads(config_path.read_text())
        return {}
  {% elif language == 'nodejs' %}
    import { readFileSync } from 'fs';
    import { homedir } from 'os';
    import { join } from 'path';
    
    export function loadConfig() {
        const configPath = join(homedir(), '.{{ cli.name }}', 'config.json');
        try {
            return JSON.parse(readFileSync(configPath, 'utf8'));
        } catch {
            return {};
        }
    }
  {% endif %}
{% endmacro %}
```

### Component Registration

Register custom components:

```python
# In your custom renderer
from goobits_cli.universal.component_registry import ComponentRegistry

registry = ComponentRegistry()

@registry.register_component('custom_validator')
def render_custom_validator(language, **kwargs):
    if language == 'python':
        return "def validate_input(value): ..."
    elif language == 'nodejs':
        return "function validateInput(value) { ... }"
```

## Performance Benefits

### Benchmark Results

Universal templates provide significant performance improvements:

| Metric | Legacy Templates | Universal Templates | Improvement |
|--------|-----------------|-------------------|-------------|
| Generation Time | 120-180ms | 60-90ms | 50% faster |
| Memory Usage | 45-60MB | 25-35MB | 40% less |
| Template Loading | 40-60ms | 15-25ms | 60% faster |
| Cross-Language Consistency | Manual | Automatic | 100% consistent |

### Optimization Features

**1. Lazy Loading**
```python
# Components loaded only when needed
def get_component(name):
    if name not in _component_cache:
        _component_cache[name] = load_component(name)
    return _component_cache[name]
```

**2. Template Caching**
```python
# Rendered templates cached for reuse
def render_template(template, context):
    cache_key = hash((template, frozenset(context.items())))
    if cache_key in _render_cache:
        return _render_cache[cache_key]
    
    result = template.render(**context)
    _render_cache[cache_key] = result
    return result
```

**3. Memory Management**
```python
# Automatic cleanup of unused components
def cleanup_unused_components():
    current_time = time.time()
    for name, (component, last_used) in list(_component_cache.items()):
        if current_time - last_used > CACHE_TTL:
            del _component_cache[name]
```

## Customization

### Custom Renderers

Create a custom renderer for a new language:

```python
# custom_renderer.py
from goobits_cli.universal.renderers.base import BaseRenderer

class GoRenderer(BaseRenderer):
    language = 'go'
    
    def render_command(self, command):
        """Render a command for Go using Cobra CLI"""
        return f'''
var {command.name}Cmd = &cobra.Command{{
    Use:   "{command.name}",
    Short: "{command.description}",
    Run: func(cmd *cobra.Command, args []string) {{
        // Call hook function
        hooks.On{command.name.title()}(args)
    }},
}}
'''
    
    def render_cli(self, cli):
        """Render the complete CLI for Go"""
        return self.render_template('go_cli.j2', cli=cli)
```

### Custom Components

Add custom universal components:

```python
# Register a custom component
from goobits_cli.universal.component_registry import register_component

@register_component('api_client')
def render_api_client(language, **kwargs):
    if language == 'python':
        return '''
import requests

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get(self, endpoint):
        return requests.get(f"{self.base_url}/{endpoint}")
'''
    elif language == 'nodejs':
        return '''
import axios from 'axios';

export class APIClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    async get(endpoint) {
        return axios.get(`${this.baseUrl}/${endpoint}`);
    }
}
'''
```

### Template Filters

Add custom template filters:

```python
# In your renderer
def snake_case_filter(value):
    """Convert string to snake_case"""
    import re
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', value).lower()

# Register the filter
self.template_env.filters['snake_case'] = snake_case_filter

# Use in templates
{{ command.name | snake_case }}
```

## Troubleshooting

### Common Issues

**1. Component Not Found**
```bash
Error: Component 'custom_component' not found in registry

Solution:
- Verify component is registered before use
- Check component name spelling
- Ensure component file is in correct location
```

**2. Renderer Missing**
```bash
Error: No renderer found for language 'rust'

Solution:
- Use supported language (python, nodejs, typescript)
- Create custom renderer for unsupported language
- Fall back to legacy templates
```

**3. Template Compilation Error**
```bash
Error: TemplateSyntaxError in component 'command_handler'

Solution:
- Check Jinja2 syntax in template
- Verify all variables are defined
- Test template with minimal context
```

### Debug Mode

Enable debug mode for detailed template generation logging:

```bash
# Enable debug output
GOOBITS_DEBUG=true goobits build --universal-templates

# Verbose logging
goobits build --universal-templates --verbose --debug
```

### Performance Debugging

Monitor template performance:

```python
# Enable performance monitoring
from goobits_cli.universal.performance import enable_monitoring

enable_monitoring()
result = build_cli_with_universal_templates(config)
print_performance_report()
```

### Template Inspection

Inspect generated IR and rendered output:

```bash
# Save intermediate representation
goobits build --universal-templates --save-ir

# Compare with legacy templates
goobits build --universal-templates --compare-legacy

# Generate both and diff
diff -u legacy_output/ universal_output/
```

## Advanced Usage

### Batch Generation

Generate CLIs for multiple configurations:

```python
from goobits_cli.universal import UniversalTemplateEngine

engine = UniversalTemplateEngine()
configs = [config1, config2, config3]

for config in configs:
    engine.generate_cli(config)
```

### Template Composition

Compose complex templates from components:

```jinja2
{# main_template.j2 #}
{% include 'command_handler.j2' %}
{% include 'config_manager.j2' %}
{% include 'error_handler.j2' %}

{{ render_cli(cli) }}
```

### Cross-Language Testing

Test CLI consistency across languages:

```python
def test_cross_language_consistency():
    config = load_test_config()
    
    python_cli = generate_cli(config, language='python')
    nodejs_cli = generate_cli(config, language='nodejs')
    
    # Compare behavior
    assert python_cli.commands == nodejs_cli.commands
    assert python_cli.help_text == nodejs_cli.help_text
```

---

The Universal Template System provides a powerful, consistent, and performant way to generate CLIs across multiple languages. By understanding its architecture and capabilities, you can create high-quality command-line tools that work identically regardless of the target language.