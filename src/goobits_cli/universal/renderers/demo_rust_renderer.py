#!/usr/bin/env python3
"""
RustRenderer Demo

This script demonstrates the RustRenderer in action, showing how it transforms
a CLI configuration into Rust-specific code with Clap framework integration.
"""

from rust_renderer import RustRenderer


def main():
    """Demonstrate RustRenderer capabilities"""
    print("🦀 RustRenderer Demo - Universal Template System")
    print("=" * 60)
    
    renderer = RustRenderer()
    
    # Sample intermediate representation
    sample_ir = {
        "project": {
            "name": "TaskRunner CLI", 
            "description": "A task automation CLI tool",
            "version": "2.1.0",
            "author": "CLI Builder Team",
            "package_name": "task-runner-cli",
            "command_name": "taskrun",
        },
        "cli": {
            "root_command": {
                "name": "taskrun",
                "description": "Task automation CLI tool",
                "version": "2.1.0",
                "arguments": [
                    {
                        "name": "config-file",
                        "description": "Configuration file path", 
                        "type": "path",
                        "required": False,
                    }
                ],
                "options": [
                    {
                        "name": "verbose",
                        "short": "v",
                        "description": "Enable verbose logging",
                        "type": "flag",
                        "default": False,
                    },
                    {
                        "name": "output-format",
                        "short": "o",
                        "description": "Output format for results",
                        "type": "string",
                        "default": "table",
                        "choices": ["json", "yaml", "table", "csv"],
                    },
                    {
                        "name": "parallel-jobs",
                        "short": "j",
                        "description": "Number of parallel execution jobs",
                        "type": "int", 
                        "default": 4,
                    }
                ],
                "subcommands": [],
            },
            "commands": {
                "run": {
                    "name": "run",
                    "description": "Execute a task or task group",
                    "arguments": [
                        {
                            "name": "task-name",
                            "description": "Name of the task to execute",
                            "type": "string",
                            "required": True,
                        }
                    ],
                    "options": [
                        {
                            "name": "dry-run",
                            "description": "Show what would be executed without running",
                            "type": "bool",
                            "default": False,
                        },
                        {
                            "name": "timeout",
                            "short": "t",
                            "description": "Task timeout in seconds",
                            "type": "int",
                            "default": 300,
                        }
                    ],
                    "subcommands": [],
                    "hook_name": "on_run",
                },
                "list": {
                    "name": "list",
                    "description": "List available tasks", 
                    "arguments": [],
                    "options": [
                        {
                            "name": "show-hidden",
                            "description": "Include hidden tasks in output", 
                            "type": "flag",
                            "default": False,
                        }
                    ],
                    "subcommands": [],
                    "hook_name": "on_list",
                }
            },
            "global_options": [],
            "completion": {
                "enabled": True,
                "shells": ["bash", "zsh", "fish"],
            }
        },
        "dependencies": {
            "rust": ["tokio", "serde_json", "anyhow", "clap"]
        },
        "metadata": {
            "generated_at": "2025-01-15T10:30:00Z",
            "generator_version": "1.4.0",
        }
    }
    
    # Generate Rust-specific context
    print("🔧 Generating Rust-specific template context...")
    context = renderer.get_template_context(sample_ir)
    
    print(f"✅ Language: {renderer.language}")
    print(f"✅ Crate name: {context['rust']['crate_name']}")
    print(f"✅ Main struct: {context['rust']['struct_name']}")
    print()
    
    # Show custom filters in action
    print("🎨 Custom Rust Filters Demo:")
    filters = renderer.get_custom_filters()
    
    test_cases = [
        ("task-runner", "rust_struct_name", "PascalCase for structs"),
        ("output-format", "rust_field_name", "snake_case for fields"),
        ("MAX_RETRIES", "rust_const_name", "SCREAMING_SNAKE_CASE for constants"),
        ("string", "rust_type", "Rust type conversion"),
        ("path", "rust_type", "Path type conversion"),
        ("int", "rust_type", "Integer type conversion"),
    ]
    
    for input_val, filter_name, description in test_cases:
        if filter_name in filters:
            result = filters[filter_name](input_val)
            print(f"  {input_val:15} -> {result:20} ({description})")
    print()
    
    # Show Clap attribute generation
    print("⚡ Clap Attribute Generation:")
    sample_option = {
        "name": "output-format",
        "short": "o",
        "description": "Choose output format for results",
        "type": "string",
        "default": "table",
        "choices": ["json", "yaml", "table", "csv"]
    }
    
    clap_attr = renderer._clap_attribute(sample_option)
    print(f"Option: {sample_option['name']}")
    print(f"Generated: {clap_attr}")
    print()
    
    # Generate sample Rust struct code
    print("🦀 Generated Rust Code Sample:")
    template_content = """
#[derive(Parser)]
#[command(name = "{{ project.command_name | rust_function_name }}")]
#[command(about = "{{ project.description }}")]
#[command(version = "{{ project.version }}")]
struct {{ project.command_name | rust_struct_name }} {
    {% for option in cli.root_command.options %}
    /// {{ option.description }}
    {{ option | clap_attribute }}
    {{ option.name | rust_field_name }}: {{ option.type | rust_type }},
    
    {% endfor %}
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    {% for cmd_name, cmd_data in cli.commands.items() %}
    /// {{ cmd_data.description }}
    {{ cmd_name | rust_struct_name }} {
        {% for arg in cmd_data.arguments %}
        /// {{ arg.description }}
        {{ arg.name | rust_field_name }}: {{ arg.type | rust_type }},
        {% endfor %}
        {% for opt in cmd_data.options %}
        /// {{ opt.description }}
        {{ opt | clap_attribute }}
        {{ opt.name | rust_field_name }}: {{ opt.type | rust_type }},
        {% endfor %}
    },
    {% endfor %}
}
    """.strip()
    
    rendered = renderer.render_component("main_struct", template_content, context)
    print(rendered)
    print()
    
    # Show output file structure
    print("📁 Rust CLI File Structure:")
    structure = renderer.get_output_structure(sample_ir)
    for component, path in sorted(structure.items()):
        print(f"  {component:20} -> {path}")
    print()
    
    # Show dependency management
    print("📦 Rust Dependencies (Cargo.toml):")
    rust_deps = context["rust"]["dependencies"]
    for dep_name, dep_spec in sorted(rust_deps.items()):
        if isinstance(dep_spec, dict):
            version = dep_spec.get("version", "latest")
            features = dep_spec.get("features", [])
            if features:
                print(f"  {dep_name:15} = {{ version = \"{version}\", features = {features} }}")
            else:
                print(f"  {dep_name:15} = \"{version}\"")
        else:
            print(f"  {dep_name:15} = \"{dep_spec}\"")
    print()
    
    print("🎉 RustRenderer Demo Complete!")
    print("The RustRenderer successfully transforms generic CLI configurations")
    print("into Rust-specific code with proper Clap integration, type safety,")
    print("and Rust naming conventions.")


if __name__ == "__main__":
    main()