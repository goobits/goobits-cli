#!/usr/bin/env python3
"""
RustRenderer Integration Example

This example demonstrates how the RustRenderer integrates with the Universal Template System
to generate complete Rust CLI applications with modern Clap derive macros.
"""

from rust_renderer import RustRenderer


def create_sample_cli_ir():
    """Create a comprehensive sample CLI intermediate representation"""
    return {
        "project": {
            "name": "DevTool CLI",
            "description": "A development automation CLI tool",
            "version": "1.2.0",
            "author": "Development Team",
            "license": "MIT",
            "package_name": "dev-tool-cli",
            "command_name": "devtool",
        },
        "cli": {
            "root_command": {
                "name": "devtool",
                "description": "Development automation CLI",
                "version": "1.2.0",
                "arguments": [],
                "options": [
                    {
                        "name": "config",
                        "short": "c",
                        "description": "Configuration file path",
                        "type": "path",
                        "required": False,
                        "default": "devtool.yaml",
                    },
                    {
                        "name": "verbose",
                        "short": "v",
                        "description": "Enable verbose output",
                        "type": "flag",
                        "default": False,
                    },
                    {
                        "name": "log-level",
                        "short": "l",
                        "description": "Set logging level",
                        "type": "string",
                        "default": "info",
                        "choices": ["debug", "info", "warn", "error"],
                    }
                ],
                "subcommands": [],
            },
            "commands": {
                "build": {
                    "name": "build",
                    "description": "Build the project with specified target",
                    "arguments": [
                        {
                            "name": "target",
                            "description": "Build target (debug, release, or custom)",
                            "type": "string",
                            "required": False,
                            "choices": ["debug", "release", "test"],
                        }
                    ],
                    "options": [
                        {
                            "name": "clean",
                            "description": "Clean before building",
                            "type": "flag",
                            "default": False,
                        },
                        {
                            "name": "parallel",
                            "short": "j",
                            "description": "Number of parallel jobs",
                            "type": "int",
                            "default": 4,
                        },
                        {
                            "name": "features",
                            "description": "Comma-separated list of features to enable",
                            "type": "string",
                            "required": False,
                        }
                    ],
                    "subcommands": [],
                    "hook_name": "on_build",
                },
                "test": {
                    "name": "test",
                    "description": "Run project tests",
                    "arguments": [
                        {
                            "name": "test-pattern",
                            "description": "Test pattern to match",
                            "type": "string",
                            "required": False,
                        }
                    ],
                    "options": [
                        {
                            "name": "coverage",
                            "description": "Generate coverage report",
                            "type": "bool",
                            "default": False,
                        },
                        {
                            "name": "output-format",
                            "description": "Test output format",
                            "type": "string",
                            "default": "pretty",
                            "choices": ["pretty", "json", "junit"],
                        }
                    ],
                    "subcommands": [],
                    "hook_name": "on_test",
                },
                "deploy": {
                    "name": "deploy", 
                    "description": "Deploy application to environment",
                    "arguments": [
                        {
                            "name": "environment",
                            "description": "Target deployment environment",
                            "type": "string",
                            "required": True,
                            "choices": ["dev", "staging", "prod"],
                        }
                    ],
                    "options": [
                        {
                            "name": "dry-run",
                            "description": "Perform a dry run without actual deployment",
                            "type": "flag",
                            "default": False,
                        },
                        {
                            "name": "timeout",
                            "short": "t",
                            "description": "Deployment timeout in seconds",
                            "type": "int",
                            "default": 600,
                        }
                    ],
                    "subcommands": [],
                    "hook_name": "on_deploy",
                }
            },
            "global_options": [],
            "completion": {
                "enabled": True,
                "shells": ["bash", "zsh", "fish"],
            }
        },
        "installation": {
            "pypi_name": "dev-tool-cli",
            "development_path": ".",
            "extras": {},
        },
        "dependencies": {
            "python": [],
            "system": ["git"],
            "npm": [],
            "rust": ["tokio", "serde", "anyhow", "clap", "colored"],
        },
        "metadata": {
            "generated_at": "2025-01-15T12:00:00Z",
            "generator_version": "1.4.0",
            "source_config": {},
        }
    }


def generate_modern_rust_cli():
    """Generate a modern Rust CLI using derive macros"""
    
    template_content = """
use anyhow::Result;
use clap::{Parser, Subcommand};
use std::path::PathBuf;

/// {{ project.description }}
#[derive(Parser)]
#[command(name = "{{ project.command_name }}")]
#[command(about = "{{ project.description }}")]
#[command(version = "{{ project.version }}")]
#[command(author = "{{ project.author }}")]
struct {{ project.command_name | rust_struct_name }} {
    {% for option in cli.root_command.options %}
    /// {{ option.description }}
    {{ option | clap_attribute }}
    {{ option.name | rust_field_name }}: {{ option.type | rust_type }},
    
    {% endfor %}
    #[command(subcommand)]
    command: Option<Commands>,
}

/// Available subcommands
#[derive(Subcommand)]
enum Commands {
    {% for cmd_name, cmd_data in cli.commands.items() %}
    /// {{ cmd_data.description }}
    {{ cmd_name | rust_struct_name }} {
        {% for arg in cmd_data.arguments %}
        /// {{ arg.description }}
        {{ arg.name | rust_field_name }}: {% if arg.required %}{{ arg.type | rust_type }}{% else %}Option<{{ arg.type | rust_type }}>{% endif %},
        {% endfor %}
        {% for opt in cmd_data.options %}
        /// {{ opt.description }}
        {{ opt | clap_attribute }}
        {{ opt.name | rust_field_name }}: {{ opt.type | rust_type }},
        {% endfor %}
    },
    {% endfor %}
}

fn main() -> Result<()> {
    let cli = {{ project.command_name | rust_struct_name }}::parse();
    
    // Initialize logging based on verbosity
    let log_level = if cli.verbose { "debug" } else { &cli.log_level };
    env_logger::init_from_env(
        env_logger::Env::default().default_filter_or(log_level)
    );
    
    match cli.command {
        Some(command) => {
            match command {
                {% for cmd_name, cmd_data in cli.commands.items() %}
                Commands::{{ cmd_name | rust_struct_name }} {
                    {% for arg in cmd_data.arguments %}{{ arg.name | rust_field_name }}, {% endfor %}
                    {% for opt in cmd_data.options %}{{ opt.name | rust_field_name }}, {% endfor %}
                } => {
                    execute_{{ cmd_name | rust_function_name }}(
                        {% for arg in cmd_data.arguments %}
                        {% if arg.required %}{{ arg.name | rust_field_name }}{% else %}{{ arg.name | rust_field_name }}.as_deref(){% endif %},
                        {% endfor %}
                        {% for opt in cmd_data.options %}{{ opt.name | rust_field_name }}, {% endfor %}
                    )?;
                }
                {% endfor %}
            }
        }
        None => {
            println!("No subcommand provided. Use --help for usage information.");
        }
    }
    
    Ok(())
}

{% for cmd_name, cmd_data in cli.commands.items() %}
/// Execute {{ cmd_name }} command
fn execute_{{ cmd_name | rust_function_name }}(
    {% for arg in cmd_data.arguments %}
    {% if arg.required %}{{ arg.name | rust_field_name }}: {{ arg.type | rust_type }},{% else %}{{ arg.name | rust_field_name }}: Option<&str>,{% endif %}
    {% endfor %}
    {% for opt in cmd_data.options %}
    {{ opt.name | rust_field_name }}: {{ opt.type | rust_type }},
    {% endfor %}
) -> Result<()> {
    log::info!("Executing {{ cmd_name }} command");
    
    {% if cmd_data.arguments %}
    // Process arguments
    {% for arg in cmd_data.arguments %}
    {% if arg.required %}
    log::debug!("{{ arg.name }}: {}", {{ arg.name | rust_field_name }});
    {% else %}
    if let Some({{ arg.name | rust_field_name }}) = {{ arg.name | rust_field_name }} {
        log::debug!("{{ arg.name }}: {}", {{ arg.name | rust_field_name }});
    }
    {% endif %}
    {% endfor %}
    {% endif %}
    
    {% if cmd_data.options %}
    // Process options
    {% for opt in cmd_data.options %}
    {% if opt.type == 'flag' or opt.type == 'bool' %}
    if {{ opt.name | rust_field_name }} {
        log::debug!("{{ opt.name }} option is enabled");
    }
    {% else %}
    log::debug!("{{ opt.name }}: {:?}", {{ opt.name | rust_field_name }});
    {% endif %}
    {% endfor %}
    {% endif %}
    
    // TODO: Implement {{ cmd_name }} logic here
    println!("🚀 {{ cmd_name | title }} command executed successfully!");
    
    Ok(())
}

{% endfor %}
    """.strip()
    
    return template_content


def main():
    """Main demonstration function"""
    print("🦀 RustRenderer Integration Example")
    print("=" * 50)
    
    # Initialize renderer and sample data
    renderer = RustRenderer()
    sample_ir = create_sample_cli_ir()
    
    # Generate context
    print("🔧 Generating Rust-specific context...")
    context = renderer.get_template_context(sample_ir)
    
    # Show what gets generated
    print(f"✅ Project: {context['project']['name']} v{context['project']['version']}")
    print(f"✅ Crate: {context['rust']['crate_name']}")
    print(f"✅ Main Struct: {context['rust']['struct_name']}")
    print(f"✅ Commands: {len(context['cli']['commands'])}")
    print()
    
    # Generate modern Rust CLI code
    print("🦀 Generated Modern Rust CLI (Clap Derive):")
    print("-" * 50)
    
    modern_template = generate_modern_rust_cli()
    rendered_code = renderer.render_component("modern_cli", modern_template, context)
    
    # Show a portion of the generated code
    lines = rendered_code.split('\n')
    for i, line in enumerate(lines[:60]):  # Show first 60 lines
        print(f"{i+1:3}: {line}")
    
    if len(lines) > 60:
        print(f"... ({len(lines) - 60} more lines)")
    
    print()
    print("-" * 50)
    
    # Show output structure
    print("📁 Generated File Structure:")
    structure = renderer.get_output_structure(sample_ir)
    for component, path in sorted(structure.items()):
        print(f"  {component:18} -> {path}")
    
    print()
    
    # Show dependencies for Cargo.toml
    print("📦 Cargo.toml Dependencies:")
    deps = context['rust']['dependencies']
    for name, spec in sorted(deps.items()):
        if isinstance(spec, dict):
            print(f"  {name} = {spec}")
        else:
            print(f"  {name} = \"{spec}\"")
    
    print()
    
    # Show key features
    print("🌟 Key RustRenderer Features:")
    features = [
        "✅ Modern Clap derive macros (#[derive(Parser, Subcommand)])",
        "✅ Proper Rust type conversions (String, i32, bool, PathBuf)",
        "✅ Snake_case for functions and fields", 
        "✅ PascalCase for structs and enums",
        "✅ Result<T, E> error handling patterns",
        "✅ Option<T> for optional arguments",
        "✅ Comprehensive #[arg(...)] attributes",
        "✅ Rust naming convention compliance",
        "✅ Integration with existing Rust ecosystem",
        "✅ Support for complex CLI structures"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print()
    print("🎉 RustRenderer successfully demonstrates modern Rust CLI generation!")
    print("The generated code follows Rust best practices and integrates seamlessly")
    print("with the Clap derive framework for type-safe, ergonomic CLI interfaces.")


if __name__ == "__main__":
    main()