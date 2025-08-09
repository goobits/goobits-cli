# API Reference

This document provides a comprehensive reference for the Goobits CLI Framework v2.0 API, including generator interfaces, configuration schemas, and extension points for developers who want to understand or extend the framework.

## Table of Contents

1. [Core API Overview](#core-api-overview)
2. [Configuration Schema API](#configuration-schema-api)
3. [Generator Interface API](#generator-interface-api)
4. [Universal Template API](#universal-template-api)
5. [Performance Framework API](#performance-framework-api)
6. [Hook System API](#hook-system-api)
7. [Extension Points](#extension-points)
8. [Command Line Interface](#command-line-interface)

## Core API Overview

### Main Entry Points

**`main.py`** - Framework Entry Point
```python
from goobits_cli.main import main, build_cli, init_project

# Main CLI entry point
def main() -> int:
    """Main entry point for the Goobits CLI Framework"""
    
# Programmatic CLI building
def build_cli(config_path: str = "goobits.yaml", 
              universal_templates: bool = False) -> bool:
    """Build CLI from configuration file"""
    
# Project initialization
def init_project(name: str, language: str = "python") -> bool:
    """Initialize a new CLI project"""
```

**`builder.py`** - Generation Orchestrator
```python
from goobits_cli.builder import CLIBuilder

class CLIBuilder:
    def __init__(self, config: GoobitsConfigSchema):
        """Initialize builder with validated configuration"""
        
    def build(self, output_dir: str = ".", 
              universal_templates: bool = False) -> Dict[str, Any]:
        """Build CLI and return generation results"""
        
    def get_generator(self, language: str) -> BaseGenerator:
        """Get appropriate generator for language"""
```

## Configuration Schema API

### Schema Classes

**`GoobitsConfigSchema`** - Complete Project Configuration
```python
from goobits_cli.schemas import GoobitsConfigSchema
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class GoobitsConfigSchema(BaseModel):
    """Complete project configuration schema"""
    
    # Required fields
    package_name: str
    command_name: str
    cli: ConfigSchema
    
    # Optional fields
    language: Optional[str] = "python"
    display_name: Optional[str] = None
    description: Optional[str] = None
    python: Optional[PythonConfig] = None
    dependencies: Optional[DependencyConfig] = None
    installation: Optional[InstallationConfig] = None
    
    # Validation methods
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return list of errors"""
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
```

**`ConfigSchema`** - CLI Structure Definition
```python
class ConfigSchema(BaseModel):
    """CLI structure definition"""
    
    name: str
    tagline: Optional[str] = None
    version: str = "1.0.0"
    
    # Commands and options
    commands: Dict[str, CommandSchema]
    options: Optional[List[OptionSchema]] = []
    
    # Advanced features
    features: Optional[FeaturesSchema] = None
    
    def get_command(self, name: str) -> Optional[CommandSchema]:
        """Get command by name"""
        
    def list_commands(self) -> List[str]:
        """List all command names"""
```

**`CommandSchema`** - Individual Command Definition
```python
class CommandSchema(BaseModel):
    """Individual command definition"""
    
    desc: str  # Command description
    args: Optional[List[ArgumentSchema]] = []
    options: Optional[List[OptionSchema]] = []
    subcommands: Optional[Dict[str, 'CommandSchema']] = {}
    
    # Command metadata
    examples: Optional[List[str]] = []
    deprecated: bool = False
    hidden: bool = False
    
    def get_hook_name(self) -> str:
        """Get the corresponding hook function name"""
        
    def validate_arguments(self) -> List[str]:
        """Validate command arguments"""
```

**`ArgumentSchema`** - Command Argument Definition
```python
class ArgumentSchema(BaseModel):
    """Command argument definition"""
    
    name: str
    desc: str
    required: bool = True
    
    # Validation
    type: Optional[str] = "str"  # str, int, float, bool
    choices: Optional[List[str]] = None
    default: Optional[Any] = None
    nargs: Optional[str] = None  # ?, *, +, or integer
    
    def validate_value(self, value: Any) -> bool:
        """Validate argument value against constraints"""
```

**`OptionSchema`** - Command Option Definition
```python
class OptionSchema(BaseModel):
    """Command option definition"""
    
    name: str
    desc: str
    short: Optional[str] = None  # Short form (-v)
    
    # Option behavior
    type: str = "str"  # flag, str, int, float, count
    required: bool = False
    default: Optional[Any] = None
    choices: Optional[List[str]] = None
    
    # Advanced features
    hidden: bool = False
    deprecated: bool = False
    envvar: Optional[str] = None  # Environment variable name
    
    def get_click_params(self) -> Dict[str, Any]:
        """Get Click framework parameters"""
        
    def get_commander_params(self) -> Dict[str, Any]:
        """Get Commander.js framework parameters"""
```

### Configuration Validation

```python
from goobits_cli.schemas import validate_configuration

def validate_configuration(config_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate configuration dictionary"""
    
def load_and_validate_config(config_path: str) -> GoobitsConfigSchema:
    """Load and validate configuration from file"""
    
def migrate_configuration(old_config: Dict[str, Any], 
                         from_version: str, 
                         to_version: str) -> Dict[str, Any]:
    """Migrate configuration between versions"""
```

## Generator Interface API

### Base Generator Interface

**`BaseGenerator`** - Abstract Base Class
```python
from abc import ABC, abstractmethod
from goobits_cli.generators.base import BaseGenerator

class BaseGenerator(ABC):
    """Abstract base class for language generators"""
    
    def __init__(self, config: GoobitsConfigSchema):
        self.config = config
        self.language = self.get_language()
        
    @abstractmethod
    def get_language(self) -> str:
        """Return the target language name"""
        
    @abstractmethod
    def generate_cli(self, output_dir: str = ".") -> Dict[str, str]:
        """Generate CLI files and return file mapping"""
        
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Get list of required dependencies"""
        
    def validate_config(self) -> List[str]:
        """Validate configuration for this generator"""
        
    def get_hook_template(self) -> str:
        """Get template for hook functions"""
```

### Language-Specific Generators

**`PythonGenerator`** - Python CLI Generator
```python
from goobits_cli.generators.python import PythonGenerator

class PythonGenerator(BaseGenerator):
    """Python CLI generator using Click framework"""
    
    def generate_cli(self, output_dir: str = ".") -> Dict[str, str]:
        """Generate Python CLI with Click"""
        
    def generate_click_commands(self) -> str:
        """Generate Click command definitions"""
        
    def generate_hook_calls(self) -> str:
        """Generate hook function calls"""
        
    def get_setup_script(self) -> str:
        """Generate setup.sh script for Python"""
        
    def get_dependencies(self) -> List[str]:
        """Get Python dependencies (click, etc.)"""
        
    # Template methods
    def render_template(self, template_name: str, **context) -> str:
        """Render Jinja2 template with context"""
```

**`NodeJSGenerator`** - Node.js CLI Generator
```python
from goobits_cli.generators.nodejs import NodeJSGenerator

class NodeJSGenerator(BaseGenerator):
    """Node.js CLI generator using Commander.js"""
    
    def generate_cli(self, output_dir: str = ".") -> Dict[str, str]:
        """Generate Node.js CLI with Commander.js"""
        
    def generate_commander_program(self) -> str:
        """Generate Commander.js program definition"""
        
    def generate_package_json(self) -> str:
        """Generate package.json with dependencies"""
        
    def get_npm_dependencies(self) -> List[str]:
        """Get npm dependencies"""
        
    def generate_hook_imports(self) -> str:
        """Generate ES module imports for hooks"""
```

**`TypeScriptGenerator`** - TypeScript CLI Generator
```python
from goobits_cli.generators.typescript import TypeScriptGenerator

class TypeScriptGenerator(BaseGenerator):
    """TypeScript CLI generator with full type safety"""
    
    def generate_cli(self, output_dir: str = ".") -> Dict[str, str]:
        """Generate TypeScript CLI with types"""
        
    def generate_type_definitions(self) -> str:
        """Generate TypeScript type definitions"""
        
    def generate_tsconfig(self) -> str:
        """Generate TypeScript configuration"""
        
    def generate_hook_interfaces(self) -> str:
        """Generate interfaces for hook functions"""
```

### Generator Registration

```python
from goobits_cli.generators import register_generator, get_generator

def register_generator(language: str, generator_class: Type[BaseGenerator]):
    """Register a new generator for a language"""
    
def get_generator(language: str) -> Type[BaseGenerator]:
    """Get generator class for language"""
    
def list_supported_languages() -> List[str]:
    """List all supported languages"""

# Usage example
@register_generator("go")
class GoGenerator(BaseGenerator):
    def get_language(self) -> str:
        return "go"
        
    def generate_cli(self, output_dir: str = ".") -> Dict[str, str]:
        # Implementation
        pass
```

## Universal Template API

### Universal Template Engine

**`UniversalTemplateEngine`** - Core Template Engine
```python
from goobits_cli.universal.template_engine import UniversalTemplateEngine

class UniversalTemplateEngine:
    """Universal template engine for cross-language generation"""
    
    def __init__(self):
        self.component_registry = ComponentRegistry()
        self.renderers = {}
        
    def generate_cli(self, config: GoobitsConfigSchema, 
                    language: str, 
                    output_dir: str = ".") -> Dict[str, str]:
        """Generate CLI using universal templates"""
        
    def create_intermediate_representation(self, 
                                        config: GoobitsConfigSchema) -> UniversalCLI:
        """Create language-agnostic IR from configuration"""
        
    def render_with_language(self, ir: UniversalCLI, 
                           language: str) -> Dict[str, str]:
        """Render IR using language-specific renderer"""
        
    def register_renderer(self, language: str, renderer: BaseRenderer):
        """Register a language renderer"""
```

**`ComponentRegistry`** - Component Management
```python
from goobits_cli.universal.component_registry import ComponentRegistry

class ComponentRegistry:
    """Registry for universal template components"""
    
    def register_component(self, name: str, component: UniversalComponent):
        """Register a universal component"""
        
    def get_component(self, name: str) -> UniversalComponent:
        """Get component by name"""
        
    def list_components(self) -> List[str]:
        """List all registered components"""
        
    def render_component(self, name: str, context: Dict[str, Any], 
                        language: str) -> str:
        """Render component for specific language"""

# Component registration decorator
def register_component(name: str):
    def decorator(func):
        ComponentRegistry.instance().register_component(name, func)
        return func
    return decorator

# Usage
@register_component("command_handler")
def render_command_handler(context: Dict[str, Any], language: str) -> str:
    """Render command handler for any language"""
    pass
```

### Language Renderers

**`BaseRenderer`** - Abstract Renderer Interface
```python
from goobits_cli.universal.renderers.base import BaseRenderer

class BaseRenderer(ABC):
    """Abstract base class for language renderers"""
    
    language: str
    
    @abstractmethod
    def render_cli(self, ir: UniversalCLI) -> Dict[str, str]:
        """Render complete CLI from IR"""
        
    @abstractmethod
    def render_command(self, command: UniversalCommand) -> str:
        """Render individual command"""
        
    @abstractmethod
    def render_option(self, option: UniversalOption) -> str:
        """Render command option"""
        
    def render_template(self, template: str, **context) -> str:
        """Render template with context"""
```

### Intermediate Representation Classes

**`UniversalCLI`** - Language-Agnostic CLI Representation
```python
from goobits_cli.universal.ir import UniversalCLI

@dataclass
class UniversalCLI:
    """Language-agnostic CLI representation"""
    
    name: str
    version: str
    description: str
    
    commands: List[UniversalCommand]
    global_options: List[UniversalOption]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        
    @classmethod
    def from_config(cls, config: GoobitsConfigSchema) -> 'UniversalCLI':
        """Create from configuration"""

@dataclass
class UniversalCommand:
    """Universal command representation"""
    
    name: str
    description: str
    arguments: List[UniversalArgument]
    options: List[UniversalOption]
    subcommands: List['UniversalCommand']
    
    def get_hook_name(self, language: str) -> str:
        """Get hook function name for language"""
```

## Performance Framework API

### Performance Validation

**`PerformanceSuite`** - Master Performance Controller
```python
from goobits_cli.performance.performance_suite import PerformanceSuite

class PerformanceSuite:
    """Master performance validation controller"""
    
    def __init__(self, languages: List[str] = None):
        self.languages = languages or ["python", "nodejs", "typescript"]
        
    def validate_performance(self, 
                           iterations: int = 5, 
                           quick: bool = False) -> PerformanceResults:
        """Run comprehensive performance validation"""
        
    def is_production_ready(self, results: PerformanceResults) -> bool:
        """Determine if CLI meets production standards"""
        
    def generate_report(self, results: PerformanceResults) -> str:
        """Generate human-readable performance report"""

@dataclass
class PerformanceResults:
    startup_times: Dict[str, float]
    memory_usage: Dict[str, float]
    template_performance: Dict[str, float]
    overall_grade: str
    production_ready: bool
```

**`StartupValidator`** - Startup Time Validation
```python
from goobits_cli.performance.startup_validator import StartupValidator

class StartupValidator:
    """Validate CLI startup performance"""
    
    def validate_startup_time(self, 
                            command: str, 
                            target_ms: float = 100.0,
                            iterations: int = 10) -> StartupResults:
        """Validate startup time against target"""
        
    def measure_startup_time(self, command: str) -> float:
        """Measure single startup time in milliseconds"""
        
    def get_optimization_suggestions(self, results: StartupResults) -> List[str]:
        """Get performance optimization suggestions"""
```

**`MemoryProfiler`** - Memory Usage Analysis
```python
from goobits_cli.performance.memory_profiler import MemoryProfiler

class MemoryProfiler:
    """Profile memory usage during CLI execution"""
    
    def profile_memory_usage(self, command: str) -> MemoryResults:
        """Profile memory usage during command execution"""
        
    def detect_memory_leaks(self, command: str, 
                          iterations: int = 10) -> LeakResults:
        """Detect potential memory leaks"""
        
    def get_memory_optimization_score(self, results: MemoryResults) -> int:
        """Get memory optimization score (0-100)"""
```

## Hook System API

### Hook Discovery and Execution

**`HookManager`** - Hook System Management
```python
from goobits_cli.hooks import HookManager

class HookManager:
    """Manage hook function discovery and execution"""
    
    def __init__(self, language: str, hook_file: str = None):
        self.language = language
        self.hook_file = hook_file or self.get_default_hook_file()
        
    def discover_hooks(self) -> Dict[str, callable]:
        """Discover all hook functions"""
        
    def execute_hook(self, command_name: str, args: Dict[str, Any]) -> Any:
        """Execute hook function for command"""
        
    def validate_hook_signature(self, hook_func: callable, 
                              command: CommandSchema) -> List[str]:
        """Validate hook function signature"""
        
    def get_hook_name(self, command_path: List[str]) -> str:
        """Get hook function name for command path"""
```

### Hook Function Interfaces

**Python Hook Interface**:
```python
from typing import Any, Dict, Optional

def on_command_name(**kwargs: Any) -> Optional[int]:
    """
    Python hook function signature
    
    Args:
        **kwargs: Command arguments and options
        
    Returns:
        Optional[int]: Exit code (0 for success, non-zero for error)
    """
    pass
```

**JavaScript/TypeScript Hook Interface**:
```typescript
// TypeScript hook function interface
interface CommandArgs {
    [key: string]: any;
}

export async function onCommandName(args: CommandArgs): Promise<void> {
    // Hook implementation
}
```

## Extension Points

### Custom Generators

**Creating Custom Generators**:
```python
from goobits_cli.generators.base import BaseGenerator
from goobits_cli.generators import register_generator

@register_generator("rust")
class RustGenerator(BaseGenerator):
    """Custom Rust CLI generator"""
    
    def get_language(self) -> str:
        return "rust"
        
    def generate_cli(self, output_dir: str = ".") -> Dict[str, str]:
        # Generate Rust CLI with Clap
        return {
            "main.rs": self.render_main_rs(),
            "Cargo.toml": self.render_cargo_toml(),
            "lib.rs": self.render_lib_rs()
        }
        
    def get_dependencies(self) -> List[str]:
        return ["clap", "serde", "tokio"]
```

### Custom Template Filters

**Registering Template Filters**:
```python
from goobits_cli.templates import register_filter

@register_filter("snake_to_camel")
def snake_to_camel_case(value: str) -> str:
    """Convert snake_case to camelCase"""
    components = value.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])

# Usage in templates
{{ command.name | snake_to_camel }}
```

### Performance Extensions

**Custom Performance Metrics**:
```python
from goobits_cli.performance import register_metric

@register_metric("binary_size")
class BinarySizeMetric:
    """Custom metric for binary size analysis"""
    
    def measure(self, cli_path: str) -> float:
        """Measure binary size in MB"""
        import os
        return os.path.getsize(cli_path) / (1024 * 1024)
        
    def evaluate(self, value: float) -> str:
        """Evaluate metric value"""
        if value < 10:
            return "EXCELLENT"
        elif value < 50:
            return "GOOD"
        else:
            return "NEEDS_OPTIMIZATION"
```

## Command Line Interface

### Main CLI Commands

**`goobits build`** - Build CLI from Configuration
```bash
# Basic usage
goobits build

# With options
goobits build --universal-templates --output-dir ./output

# Parameters:
#   --universal-templates    Use universal template system
#   --output-dir DIR        Output directory (default: current)
#   --config FILE           Configuration file (default: goobits.yaml)
#   --verbose               Verbose output
#   --dry-run              Show what would be generated
```

**`goobits init`** - Initialize New Project
```bash
# Initialize Python project
goobits init my-cli

# Initialize Node.js project
goobits init my-cli --language nodejs

# Parameters:
#   PROJECT_NAME            Name of the CLI project
#   --language LANG         Target language (python, nodejs, typescript)
#   --template TEMPLATE     Project template (basic, advanced)
#   --interactive          Interactive configuration
```

**`goobits validate`** - Validate Configuration
```bash
# Validate current configuration
goobits validate

# Validate specific file
goobits validate --config custom.yaml

# Parameters:
#   --config FILE           Configuration file to validate
#   --strict               Strict validation mode
#   --fix                  Attempt to fix common issues
```

**`goobits performance`** - Performance Validation
```bash
# Run performance validation
goobits performance

# Quick performance check
goobits performance --quick

# Parameters:
#   --quick                Quick validation (fewer iterations)
#   --iterations N         Number of test iterations
#   --target-startup MS    Startup time target in milliseconds
#   --language LANG        Test specific language only
#   --json                 Output results as JSON
```

### Programmatic Usage

**Using Goobits as a Library**:
```python
from goobits_cli import build_cli, validate_config, init_project
from goobits_cli.schemas import load_config

# Build CLI programmatically
config = load_config("goobits.yaml")
success = build_cli(config, universal_templates=True, output_dir="./build")

# Validate configuration
valid, errors = validate_config(config)
if not valid:
    print("Configuration errors:", errors)

# Initialize new project
init_project("my-cli", language="typescript", template="advanced")
```

### Environment Variables

**Configuration via Environment Variables**:
```bash
# Performance monitoring
export GOOBITS_PERFORMANCE_MONITORING=true
export GOOBITS_METRICS_ENDPOINT=https://metrics.example.com

# Debug settings
export GOOBITS_DEBUG=true
export GOOBITS_LOG_LEVEL=DEBUG

# Template settings
export GOOBITS_TEMPLATE_CACHE_DIR=/tmp/goobits-cache
export GOOBITS_UNIVERSAL_TEMPLATES=true
```

---

This API reference provides comprehensive documentation for developers working with or extending the Goobits CLI Framework. For usage examples and tutorials, refer to the other documentation files in this repository.