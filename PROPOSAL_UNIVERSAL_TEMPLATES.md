# Proposal: Universal Jinja Templates for All Languages

## Concept

Since Python, Node.js, and Rust CLIs have the same structure and patterns, we could use **one set of templates** with language conditionals.

## Example: Universal cli.j2 Template

```jinja
{%- if language == 'python' -%}
#!/usr/bin/env python3
"""Auto-generated from {{ file_name }}"""
import click
from app_hooks import {{ commands.keys() | map('prefix_on_') | join(', ') }}
{%- elif language == 'javascript' -%}
#!/usr/bin/env node
/**
 * Auto-generated from {{ file_name }}
 */
const { Command } = require('commander');
const hooks = require('./app_hooks');
{%- elif language == 'rust' -%}
//! Auto-generated from {{ file_name }}
use clap::{Parser, Subcommand};

mod app_hooks;
use app_hooks::{
{%- for cmd in commands.keys() %}
    on_{{ cmd }}{{ ", " if not loop.last else "" }}
{%- endfor %}
};
{%- endif %}

{#- Main CLI setup -#}
{%- if language == 'python' %}
@click.group()
@click.version_option(version='{{ version }}')
def main():
    """{{ description }}"""
    pass
{%- elif language == 'javascript' %}
const program = new Command();
program
    .name('{{ command_name }}')
    .description('{{ description }}')
    .version('{{ version }}');
{%- elif language == 'rust' %}
#[derive(Parser)]
#[command(author, version = "{{ version }}", about = "{{ description }}")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
{%- endif %}

{#- Commands definition -#}
{%- for cmd_name, cmd in commands.items() %}
{%- if language == 'python' %}

@main.command()
{%- for opt in cmd.options %}
@click.option('--{{ opt.long }}', 
              {%- if opt.short %} '-{{ opt.short }}',{%- endif %}
              {%- if opt.type == 'bool' %} is_flag=True,{%- endif %}
              {%- if opt.type == 'int' %} type=int,{%- endif %}
              help='{{ opt.desc }}')
{%- endfor %}
def {{ cmd_name }}({{ cmd.options | map(attribute='name') | join(', ') }}):
    """{{ cmd.desc }}"""
    on_{{ cmd_name }}({{ cmd.options | map(attribute='name') | map('keyword_arg') | join(', ') }})

{%- elif language == 'javascript' %}

program
    .command('{{ cmd_name }}')
    .description('{{ cmd.desc }}')
{%- for opt in cmd.options %}
    .option('--{{ opt.long }}{{ " -" + opt.short if opt.short else "" }}', '{{ opt.desc }}')
{%- endfor %}
    .action((options) => {
        hooks.on{{ cmd_name | capitalize }}(options);
    });

{%- elif language == 'rust' %}
    /// {{ cmd.desc }}
    {{ cmd_name | capitalize }} {
{%- for opt in cmd.options %}
        /// {{ opt.desc }}
        #[arg(long)]
        {{ opt.name }}: {% if opt.type == 'bool' %}bool{% elif opt.type == 'int' %}Option<usize>{% else %}Option<String>{% endif %},
{%- endfor %}
    },
{%- endif %}
{%- endfor %}

{#- Main execution -#}
{%- if language == 'python' %}

if __name__ == '__main__':
    main()

{%- elif language == 'javascript' %}

program.parse(process.argv);

{%- elif language == 'rust' %}
}

fn main() {
    let cli = Cli::parse();
    
    match cli.command {
{%- for cmd_name, cmd in commands.items() %}
        Commands::{{ cmd_name | capitalize }} { {{ cmd.options | map(attribute='name') | join(', ') }} } => {
            on_{{ cmd_name }}({{ cmd.options | map(attribute='name') | join(', ') }});
        }
{%- endfor %}
    }
}
{%- endif %}
```

## Example: Universal app_hooks.j2 Template

```jinja
{%- if language == 'python' -%}
#!/usr/bin/env python3
"""Hook implementations for {{ package_name }}"""

{%- for cmd_name, cmd in commands.items() %}
def on_{{ cmd_name }}({{ cmd.options | python_params }}, **kwargs):
    """{{ cmd.desc }}"""
    # TODO: Implement {{ cmd_name }} command
    print("{{ cmd_name | capitalize }} command called with:", locals())

{% endfor %}

{%- elif language == 'javascript' -%}
/**
 * Hook implementations for {{ package_name }}
 */

{%- for cmd_name, cmd in commands.items() %}
exports.on{{ cmd_name | capitalize }} = function(options) {
    // {{ cmd.desc }}
    // TODO: Implement {{ cmd_name }} command
    console.log('{{ cmd_name | capitalize }} command called with:', options);
};

{% endfor %}

{%- elif language == 'rust' -%}
//! Hook implementations for {{ package_name }}

{%- for cmd_name, cmd in commands.items() %}
pub fn on_{{ cmd_name }}({{ cmd.options | rust_params }}) {
    // {{ cmd.desc }}
    // TODO: Implement {{ cmd_name }} command
    println!("{{ cmd_name | capitalize }} command called with: {{ cmd.options | rust_debug_format }}");
}

{% endfor %}
{%- endif %}
```

## Benefits

1. **Single Source of Truth**: One template to maintain instead of three
2. **Guaranteed Consistency**: All languages get the same structure
3. **Easier Updates**: Change once, apply to all languages
4. **Reduced Duplication**: Common patterns defined once
5. **Language Parity**: New features automatically available to all

## Implementation Approach

### 1. Create Universal Templates Directory
```
templates/
├── universal/
│   ├── cli.j2
│   ├── app_hooks.j2
│   ├── setup.sh.j2
│   └── gitignore.j2
├── python/          # Language-specific only
│   └── pyproject.toml.j2
├── rust/            # Language-specific only
│   └── Cargo.toml.j2
└── nodejs/          # Language-specific only
    └── package.json.j2
```

### 2. Update Generators to Use Universal Templates

```python
class BaseGenerator:
    def __init__(self, language):
        self.language = language
        # Load universal templates
        self.env = Environment(loader=FileSystemLoader([
            'templates/universal',
            f'templates/{language}'
        ]))
        
    def generate_cli(self, context):
        template = self.env.get_template('cli.j2')
        context['language'] = self.language
        return template.render(**context)
```

### 3. Custom Filters for Each Language

```python
# Python filters
def python_params(options):
    params = []
    for opt in options:
        if opt.type == 'bool':
            params.append(f"{opt.name}=False")
        else:
            params.append(f"{opt.name}=None")
    return ', '.join(params)

# Rust filters  
def rust_params(options):
    params = []
    for opt in options:
        if opt.type == 'bool':
            params.append(f"{opt.name}: bool")
        elif opt.type == 'int':
            params.append(f"{opt.name}: Option<usize>")
        else:
            params.append(f"{opt.name}: Option<String>")
    return ', '.join(params)

# Register filters
env.filters['python_params'] = python_params
env.filters['rust_params'] = rust_params
env.filters['capitalize'] = str.capitalize
```

## Challenges & Solutions

1. **Complex Language Differences**
   - Solution: Use helper functions and filters
   - Keep language-specific logic in filters, not templates

2. **Readability**
   - Solution: Clear comments and sections
   - Consistent indentation despite conditionals

3. **Testing**
   - Solution: Generate for all languages and diff
   - Ensure output matches current generators

## Migration Path

1. Start with simple templates (app_hooks.j2)
2. Gradually convert complex ones (cli.j2)
3. Keep backward compatibility
4. Extensive testing with diff tools

## Conclusion

Universal templates would:
- Reduce code by ~60%
- Ensure perfect consistency
- Make adding new languages easier
- Simplify maintenance

The syntax differences can be handled with smart filters and conditionals.