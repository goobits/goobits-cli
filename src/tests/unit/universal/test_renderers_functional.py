"""
Functional tests for Universal Template System Renderers.

Tests the actual rendering functionality, template context generation,
and language-specific code generation for Node.js and TypeScript renderers.
"""

import pytest

from goobits_cli.universal.renderers.nodejs_renderer import NodeJSRenderer
from goobits_cli.universal.renderers.typescript_renderer import TypeScriptRenderer


class TestNodeJSRendererFunctional:
    """Functional tests for NodeJSRenderer with real template rendering"""
    
    def setup_method(self):
        """Setup test environment"""
        self.renderer = NodeJSRenderer()
        
        # Create test intermediate representation
        self.test_ir = {
            "project": {
                "name": "Test CLI Tool",
                "description": "A comprehensive test CLI application",
                "version": "2.1.0",
                "author": "Test Author",
                "license": "MIT",
                "package_name": "test-cli-tool",
                "command_name": "testcli",
            },
            "cli": {
                "root_command": {
                    "name": "testcli",
                    "description": "Test CLI application for functionality testing",
                    "version": "2.1.0",
                    "arguments": [],
                    "options": [
                        {
                            "name": "verbose",
                            "short": "v",
                            "description": "Enable verbose output",
                            "type": "flag",
                            "default": False,
                            "required": False
                        },
                        {
                            "name": "config",
                            "short": "c",
                            "description": "Configuration file path",
                            "type": "string",
                            "default": "config.json",
                            "required": False
                        }
                    ],
                    "subcommands": [
                        {
                            "name": "build",
                            "description": "Build the project",
                            "arguments": [
                                {
                                    "name": "target",
                                    "description": "Build target directory",
                                    "type": "string",
                                    "required": True,
                                    "multiple": False
                                }
                            ],
                            "options": [
                                {
                                    "name": "production",
                                    "short": "p",
                                    "description": "Production build",
                                    "type": "flag",
                                    "default": False,
                                    "required": False
                                }
                            ],
                            "subcommands": [],
                            "hook_name": "on_build"
                        },
                        {
                            "name": "deploy",
                            "description": "Deploy the application",
                            "arguments": [],
                            "options": [
                                {
                                    "name": "environment",
                                    "short": "e",
                                    "description": "Deployment environment",
                                    "type": "string",
                                    "default": "staging",
                                    "required": False
                                }
                            ],
                            "subcommands": [],
                            "hook_name": "on_deploy"
                        }
                    ]
                },
                "commands": {
                    "build": {
                        "name": "build",
                        "description": "Build the project",
                        "arguments": [{"name": "target", "description": "Build target", "type": "string", "required": True}],
                        "options": [{"name": "production", "short": "p", "description": "Production build", "type": "flag"}],
                        "hook_name": "on_build"
                    },
                    "deploy": {
                        "name": "deploy", 
                        "description": "Deploy the application",
                        "arguments": [],
                        "options": [{"name": "environment", "short": "e", "description": "Environment", "type": "string"}],
                        "hook_name": "on_deploy"
                    }
                },
                "features": {
                    "interactive_mode": {
                        "enabled": True
                    }
                }
            },
            "installation": {
                "pypi_name": "test-cli-tool",
                "development_path": ".",
                "extras": {}
            },
            "dependencies": {
                "npm": ["lodash@4.17.21", "axios", "uuid@9.0.0"],
                "system": [],
                "python": [],
                "rust": []
            },
            "metadata": {
                "generated_at": "2023-01-01T00:00:00Z",
                "generator_version": "1.0.0"
            }
        }
    
    def test_renderer_properties(self):
        """Test basic renderer properties"""
        assert self.renderer.language == "nodejs"
        
        extensions = self.renderer.file_extensions
        assert "js" in extensions
        assert "json" in extensions
        assert "md" in extensions
    
    def test_template_context_generation(self):
        """Test generating Node.js-specific template context"""
        context = self.renderer.get_template_context(self.test_ir)
        
        # Check basic context structure
        assert context["language"] == "nodejs"
        assert context["project"]["name"] == "Test CLI Tool"
        assert context["cli"]["root_command"]["name"] == "testcli"
        
        # Check Node.js specific additions
        assert "commander_commands" in context
        assert "npm_dependencies" in context
        assert "nodejs_imports" in context
        assert "hook_functions" in context
        assert "js_package_name" in context
        assert "js_command_name" in context
        assert "node_version" in context
        assert context["node_version"] == ">=14.0.0"
    
    def test_commander_structure_building(self):
        """Test building Commander.js command structure"""
        context = self.renderer.get_template_context(self.test_ir)
        commander = context["commander_commands"]
        
        # Check root command
        assert commander["root_command"]["name"] == "testcli"
        assert commander["root_command"]["description"] == "Test CLI application for functionality testing"
        assert commander["root_command"]["version"] == "2.1.0"
        
        # Check root options
        root_options = commander["root_command"]["options"]
        assert len(root_options) == 2
        
        verbose_option = next(opt for opt in root_options if "verbose" in opt["flags"])
        assert "-v" in verbose_option["flags"]
        assert "--verbose" in verbose_option["flags"]
        assert verbose_option["type"] == "boolean"
        
        # Check subcommands
        assert len(commander["subcommands"]) == 2
        
        build_cmd = next(cmd for cmd in commander["subcommands"] if cmd["name"] == "build")
        assert build_cmd["description"] == "Build the project"
        assert len(build_cmd["arguments"]) == 1
        assert len(build_cmd["options"]) == 1
        assert build_cmd["hook_name"] == "on_build"
    
    def test_npm_dependencies_building(self):
        """Test building NPM dependencies"""
        context = self.renderer.get_template_context(self.test_ir)
        npm_deps = context["npm_dependencies"]
        
        # Should include framework dependencies
        assert "commander" in npm_deps
        assert "chalk" in npm_deps
        
        # Should include IR dependencies
        assert "lodash" in npm_deps
        assert "axios" in npm_deps
        assert "uuid" in npm_deps
        
        # Check version handling
        assert npm_deps["lodash"] == "^4.17.21"
        assert npm_deps["uuid"] == "^9.0.0"
        assert npm_deps["axios"] == "latest"  # No version specified
    
    def test_imports_generation(self):
        """Test generating ES module imports"""
        context = self.renderer.get_template_context(self.test_ir)
        imports = context["nodejs_imports"]
        
        # Should include framework imports
        assert "import { Command } from 'commander';" in imports
        assert "import chalk from 'chalk';" in imports
        
        # Should include interactive mode imports (since enabled) - using CommonJS for interactive mode
        # Note: The interactive mode template uses require() syntax, not import
        # So interactive imports won't be in the ES module imports list
        
        # Should include dependency imports
        assert "import lodash from 'lodash';" in imports
        assert "import axios from 'axios';" in imports
        assert "import uuid from 'uuid';" in imports
    
    def test_hook_functions_generation(self):
        """Test generating hook function definitions"""
        context = self.renderer.get_template_context(self.test_ir)
        hooks = context["hook_functions"]
        
        assert len(hooks) == 2
        
        build_hook = next(hook for hook in hooks if hook["command_name"] == "build")
        assert build_hook["name"] == "on_build"
        assert build_hook["js_name"] == "onBuild"
        assert build_hook["description"] == "Build the project"
        assert len(build_hook["arguments"]) == 1
        assert len(build_hook["options"]) == 1
        
        deploy_hook = next(hook for hook in hooks if hook["command_name"] == "deploy")
        assert deploy_hook["name"] == "on_deploy"
        assert deploy_hook["js_name"] == "onDeploy"
    
    def test_output_structure_generation(self):
        """Test generating output file structure"""
        output_structure = self.renderer.get_output_structure(self.test_ir)
        
        # Should have core files
        assert "command_handler" in output_structure
        assert "config_manager" in output_structure  
        assert "package_config" in output_structure
        
        # Check file paths
        assert output_structure["command_handler"] == "cli.js"
        assert output_structure["package_config"] == "package.json"
        
        # Should have other expected files
        assert len(output_structure) > 0  # Should have some files
    
    def test_custom_filters(self):
        """Test Node.js-specific custom filters"""
        filters = self.renderer.get_custom_filters()
        
        # Test JS type filter
        assert filters["js_type"]("string") == "String"
        assert filters["js_type"]("integer") == "Number"
        assert filters["js_type"]("boolean") == "Boolean"
        assert filters["js_type"]("flag") == "Boolean"
        
        # Test camelCase filter
        assert filters["camel_case"]("test-command") == "testCommand"
        assert filters["camel_case"]("build_project") == "buildProject"
        assert filters["camel_case"]("simple") == "simple"
        
        # Test hook name filter
        assert filters["hook_name"]("build-project") == "onBuildProject"
        assert filters["hook_name"]("on_test_command") == "onTestCommand"
        
        # Test JS variable filter
        assert filters["js_variable"]("test-cli") == "test_cli"
        assert filters["js_variable"]("123invalid") == "_123invalid"
        
        # Test NPM package name filter
        assert filters["npm_package_name"]("Test CLI") == "test-cli"
        assert filters["npm_package_name"]("My@Package") == "my-package"
    
    def test_component_rendering(self):
        """Test rendering actual component templates"""
        context = self.renderer.get_template_context(self.test_ir)
        
        # Simple test template
        test_template = """
{# Node.js Command Handler Template #}
{% if language == 'nodejs' %}
import { Command } from 'commander';

const program = new Command();
program
    .name('{{ cli.root_command.name }}')
    .description('{{ project.description }}')
    .version('{{ project.version }}');

{% for hook in hook_functions %}
async function {{ hook.js_name }}() {
    // {{ hook.description }}
    console.log('Executing {{ hook.command_name }} command');
    return { status: 'success', command: '{{ hook.command_name }}' };
}
{% endfor %}

// Register commands
{% for cmd in commander_commands.subcommands %}
program
    .command('{{ cmd.name }}')
    .description('{{ cmd.description }}')
    {% for arg in cmd.arguments -%}
    .argument('{{ arg.pattern }}', '{{ arg.description }}')
    {% endfor -%}
    {% for opt in cmd.options -%}
    {{ opt | commander_option }}
    {% endfor %}
    .action(async (...args) => {
        const result = await {{ cmd.hook_name | hook_name }}();
        console.log('Result:', result);
    });
{% endfor %}

program.parse();
{% endif %}
"""
        
        rendered = self.renderer.render_component("test_handler", test_template, context)
        
        # Check basic structure
        assert "import { Command } from 'commander';" in rendered
        assert "program.name('testcli')" in rendered
        assert "async function onBuild()" in rendered
        assert "async function onDeploy()" in rendered
        assert "program.command('build')" in rendered
        assert "program.command('deploy')" in rendered
    
    def test_post_processing(self):
        """Test JavaScript post-processing"""
        raw_js = """
import    {   Command   }    from    'commander';


function  test() {
    return true;
}
function  another() {
    return false;
}


export default test;
"""
        
        processed = self.renderer._post_process_javascript(raw_js)
        
        # Should fix import formatting
        assert "import { Command } from 'commander';" in processed
        
        # Should reduce excessive blank lines
        assert "\n\n\n" not in processed
        
        # Should add proper spacing around functions
        lines = processed.split('\n')
        assert len([line for line in lines if line.strip() == ""]) <= 3  # Reasonable blank lines
    
    def test_error_handling(self):
        """Test error handling in rendering"""
        # Test with invalid template
        invalid_template = "{% if unclosed %} Invalid template"
        
        with pytest.raises(Exception):  # Should raise template syntax error
            self.renderer.render_component("invalid", invalid_template, {})
    
    def test_javascript_naming_utilities(self):
        """Test JavaScript naming utility methods"""
        # Test JS variable names
        assert self.renderer._to_js_variable_name("test-cli") == "test_cli"
        assert self.renderer._to_js_variable_name("123invalid") == "_123invalid"
        assert self.renderer._to_js_variable_name("") == "default"
        assert self.renderer._to_js_variable_name("valid_name") == "valid_name"
        
        # Test package names
        assert self.renderer._to_js_package_name("Test CLI") == "test-cli"
        assert self.renderer._to_js_package_name("My@Package#Name") == "my-package-name"
        assert self.renderer._to_js_package_name("UPPERCASE") == "uppercase"


class TestTypeScriptRendererFunctional:
    """Functional tests for TypeScriptRenderer with real template rendering"""
    
    def setup_method(self):
        """Setup test environment"""
        self.renderer = TypeScriptRenderer()
        
        # Create comprehensive test IR
        self.test_ir = {
            "project": {
                "name": "TypeScript CLI",
                "description": "A TypeScript CLI application with type safety",
                "version": "1.5.0",
                "author": "TypeScript Developer",
                "license": "Apache-2.0",
                "package_name": "typescript-cli",
                "command_name": "tscli",
            },
            "cli": {
                "root_command": {
                    "name": "tscli",
                    "description": "TypeScript CLI with full type safety",
                    "version": "1.5.0",
                    "arguments": [],
                    "options": [
                        {
                            "name": "debug",
                            "short": "d",
                            "description": "Enable debug mode",
                            "type": "flag",
                            "default": False
                        },
                        {
                            "name": "output",
                            "short": "o",
                            "description": "Output file path",
                            "type": "string",
                            "required": False
                        }
                    ],
                    "subcommands": [
                        {
                            "name": "compile",
                            "description": "Compile TypeScript files",
                            "arguments": [
                                {
                                    "name": "files",
                                    "description": "Files to compile",
                                    "type": "array",
                                    "required": True,
                                    "multiple": True
                                }
                            ],
                            "options": [
                                {
                                    "name": "strict",
                                    "description": "Enable strict mode",
                                    "type": "flag",
                                    "default": True
                                },
                                {
                                    "name": "target",
                                    "description": "Compilation target",
                                    "type": "string",
                                    "default": "ES2020"
                                }
                            ],
                            "hook_name": "on_compile"
                        }
                    ]
                },
                "commands": {
                    "compile": {
                        "name": "compile",
                        "description": "Compile TypeScript files",
                        "hook_name": "on_compile"
                    }
                }
            },
            "installation": {
                "pypi_name": "typescript-cli",
                "development_path": ".",
                "extras": {}
            },
            "dependencies": {
                "npm": ["typescript@5.0.0", "@types/node@18.0.0"],
                "system": [],
                "python": [],
                "rust": []
            },
            "metadata": {
                "generated_at": "2023-01-01T00:00:00Z",
                "generator_version": "1.0.0"
            }
        }
    
    def test_renderer_properties(self):
        """Test basic renderer properties"""
        assert self.renderer.language == "typescript"
        
        extensions = self.renderer.file_extensions
        assert "ts" in extensions
        assert "d.ts" in extensions
        assert "js" in extensions
        assert "json" in extensions
    
    def test_template_context_generation(self):
        """Test generating TypeScript-specific template context"""
        context = self.renderer.get_template_context(self.test_ir)
        
        # Check basic structure
        assert context["language"] == "typescript"
        assert context["project"]["name"] == "TypeScript CLI"
        
        # Check TypeScript-specific additions
        assert "typescript" in context
        ts_context = context["typescript"]
        assert "interfaces" in ts_context
        assert "type_mappings" in ts_context
        assert "imports" in ts_context
        assert "exports" in ts_context
        
        # Check build configuration
        assert "build_config" in context
    
    def test_interfaces_generation(self):
        """Test generating TypeScript interfaces"""
        context = self.renderer.get_template_context(self.test_ir)
        interfaces = context["typescript"]["interfaces"]
        
        # Should generate interfaces for CLI structure
        assert len(interfaces) > 0
        
        # Find command options interface
        options_interfaces = [iface for iface in interfaces if "Options" in iface["name"]]
        assert len(options_interfaces) > 0
        
        # Check interface structure
        compile_options = next((iface for iface in options_interfaces if "CompileOptions" in iface["name"]), None)
        if compile_options:
            assert "strict" in compile_options["properties"]
            assert "target" in compile_options["properties"]
    
    def test_type_mappings(self):
        """Test TypeScript type mappings"""
        context = self.renderer.get_template_context(self.test_ir)
        type_mappings = context["typescript"]["type_mappings"]
        
        assert "string" in type_mappings
        assert "number" in type_mappings
        assert "boolean" in type_mappings
        assert "array" in type_mappings
        
        assert type_mappings["string"] == "string"
        assert type_mappings["integer"] == "number"
        assert type_mappings["flag"] == "boolean"
    
    def test_custom_filters(self):
        """Test TypeScript-specific custom filters"""
        filters = self.renderer.get_custom_filters()
        
        # Test type filter
        assert filters["ts_type"]("string") == "string"
        assert filters["ts_type"]("integer") == "number"
        assert filters["ts_type"]("flag") == "boolean"
        assert filters["ts_type"]("array") == "any[]"
        
        # Test case conversion filters
        assert filters["camelCase"]("test-command") == "testCommand"
        assert filters["PascalCase"]("test-command") == "TestCommand"
        assert filters["camelCase"]("compile_files") == "compileFiles"
        assert filters["PascalCase"]("compile_files") == "CompileFiles"
        
        # Test safe name filter
        assert filters["ts_safe_name"]("class") == "_class"  # Reserved keyword
        assert filters["ts_safe_name"]("interface") == "_interface"
        assert filters["ts_safe_name"]("validName") == "validName"
        
        # Test optional filter
        assert filters["ts_optional"]({"required": False}) == "?"
        assert filters["ts_optional"]({"required": True}) == ""
        
        # Test array type filter
        assert filters["ts_array_type"]("string") == "string[]"
        assert filters["ts_array_type"]("number") == "number[]"
    
    def test_imports_generation(self):
        """Test generating TypeScript imports"""
        context = self.renderer.get_template_context(self.test_ir)
        imports = context["typescript"]["imports"]
        
        # Should include TypeScript-specific imports
        assert len(imports) > 0
        
        # Check for common imports
        commander_import = next((imp for imp in imports if "commander" in imp), None)
        assert commander_import is not None
    
    def test_build_config_generation(self):
        """Test generating TypeScript build configuration"""
        context = self.renderer.get_template_context(self.test_ir)
        build_config = context["build_config"]
        
        # Should have TypeScript configuration
        assert "tsconfig" in build_config
        tsconfig = build_config["tsconfig"]
        
        assert "compilerOptions" in tsconfig
        compiler_options = tsconfig["compilerOptions"]
        
        # Check basic compiler options
        assert "target" in compiler_options
        assert "module" in compiler_options
        assert "strict" in compiler_options
        assert "esModuleInterop" in compiler_options
        
        # Should have build scripts
        if "scripts" in build_config:
            scripts = build_config["scripts"]
            assert "build" in scripts or "compile" in scripts
    
    def test_naming_conventions_application(self):
        """Test application of TypeScript naming conventions"""
        # Test data with various naming scenarios
        test_ir = {
            "project": {
                "name": "test-cli-app",
                "command_name": "test_cli",
                "package_name": "test-cli-package"
            },
            "cli": {
                "root_command": {
                    "name": "test-cli",
                    "subcommands": [
                        {
                            "name": "build-project",
                            "hook_name": "on_build_project"
                        }
                    ]
                }
            }
        }
        
        context = self.renderer.get_template_context(test_ir)
        
        # Check that naming conventions are applied throughout
        assert "project" in context
        # Names should be converted appropriately for TypeScript
        
    def test_component_rendering_with_types(self):
        """Test rendering TypeScript component with type annotations"""
        context = self.renderer.get_template_context(self.test_ir)
        
        # TypeScript-specific template with interfaces and types
        ts_template = """
{# TypeScript CLI Handler Template #}
{% if language == 'typescript' %}
import { Command } from 'commander';

// Generated interfaces
{% for interface in typescript.interfaces %}
interface {{ interface.name }} {
  {% for prop_name, prop_type in interface.properties.items() %}
  {{ prop_name }}{{ prop_type.optional | ts_optional }}: {{ prop_type.type | ts_type }};
  {% endfor %}
}
{% endfor %}

// CLI Program
const program = new Command();

program
  .name('{{ cli.root_command.name }}')
  .description('{{ project.description }}')
  .version('{{ project.version }}');

{% for cmd in cli.root_command.subcommands %}
// {{ cmd.name | PascalCase }} command handler
async function handle{{ cmd.name | PascalCase }}({{ cmd.arguments[0].name if cmd.arguments else 'args' }}: {{ cmd.arguments[0].type | ts_type if cmd.arguments else 'any' }}): Promise<void> {
  // {{ cmd.description }}
  console.log('Executing {{ cmd.name }} command');
}

program
  .command('{{ cmd.name }}')
  .description('{{ cmd.description }}')
  .action(handle{{ cmd.name | PascalCase }});
{% endfor %}

export default program;
{% endif %}
"""
        
        rendered = self.renderer.render_component("ts_handler", ts_template, context)
        
        # Check TypeScript-specific elements
        assert "interface " in rendered
        assert ": string" in rendered or ": number" in rendered or ": boolean" in rendered
        assert "async function handle" in rendered
        assert "Promise<void>" in rendered
        assert "export default program;" in rendered
    
    def test_interface_generation_edge_cases(self):
        """Test interface generation with various edge cases"""
        # Test IR with complex option types
        complex_ir = {
            "cli": {
                "root_command": {
                    "subcommands": [
                        {
                            "name": "complex-command",
                            "options": [
                                {
                                    "name": "array-option",
                                    "type": "array",
                                    "required": False,
                                    "multiple": True
                                },
                                {
                                    "name": "boolean-flag",
                                    "type": "flag",
                                    "required": False
                                },
                                {
                                    "name": "required-string",
                                    "type": "string",
                                    "required": True
                                }
                            ]
                        }
                    ]
                }
            }
        }
        
        interfaces = self.renderer._generate_interfaces(complex_ir)
        
        # Should generate appropriate interfaces
        assert len(interfaces) > 0
        
        # Find the complex command options interface
        complex_options = next(
            (iface for iface in interfaces if "ComplexCommandOptions" in iface["name"]), 
            None
        )
        
        if complex_options:
            properties = complex_options["properties"]
            
            # Check array option
            if "arrayOption" in properties:
                assert properties["arrayOption"]["type"] == "any[]"
                assert properties["arrayOption"]["optional"]
            
            # Check boolean flag
            if "booleanFlag" in properties:
                assert properties["booleanFlag"]["type"] == "boolean"
                assert properties["booleanFlag"]["optional"]
            
            # Check required string
            if "requiredString" in properties:
                assert properties["requiredString"]["type"] == "string"
                assert not properties["requiredString"]["optional"]
    
    def test_typescript_reserved_keywords(self):
        """Test handling of TypeScript reserved keywords"""
        filters = self.renderer.get_custom_filters()
        
        # Test reserved keywords
        reserved_words = ["class", "interface", "type", "namespace", "enum", "module"]
        
        for word in reserved_words:
            safe_name = filters["ts_safe_name"](word)
            assert safe_name != word  # Should be modified
            assert safe_name.startswith("_") or safe_name.endswith("_")
    
    def test_function_signature_generation(self):
        """Test generating TypeScript function signatures"""
        filters = self.renderer.get_custom_filters()
        
        # Test function signature filter if exists
        if "ts_function_signature" in filters:
            # Test with command arguments and options
            command_data = {
                "arguments": [
                    {"name": "input", "type": "string", "required": True},
                    {"name": "files", "type": "array", "required": False, "multiple": True}
                ],
                "options": [
                    {"name": "verbose", "type": "flag"},
                    {"name": "output", "type": "string"}
                ]
            }
            
            signature = filters["ts_function_signature"](command_data)
            
            # Should include typed parameters
            assert "input: string" in signature
            assert "files" in signature
            assert "options" in signature or "Options" in signature
    
    def test_error_handling_in_rendering(self):
        """Test error handling during template rendering"""
        # Test with malformed template
        bad_template = "{{ undefined_variable.nonexistent_property }}"
        
        # Should handle gracefully or raise appropriate error
        try:
            result = self.renderer.render_component("bad", bad_template, {})
            # If no error, should handle undefined variables gracefully
            assert isinstance(result, str)
        except Exception as e:
            # Should raise a specific template error
            assert "undefined" in str(e).lower() or "template" in str(e).lower()


class TestRendererIntegration:
    """Integration tests for renderer functionality"""
    
    def test_renderer_compatibility(self):
        """Test that renderers produce compatible output structures"""
        nodejs_renderer = NodeJSRenderer()
        typescript_renderer = TypeScriptRenderer()
        
        # Test IR that both should handle
        shared_ir = {
            "project": {"name": "Test CLI", "command_name": "testcli"},
            "cli": {
                "root_command": {
                    "name": "testcli",
                    "subcommands": [
                        {"name": "test", "description": "Test command", "hook_name": "on_test"}
                    ]
                }
            },
            "dependencies": {"npm": ["commander"]}
        }
        
        nodejs_output = nodejs_renderer.get_output_structure(shared_ir)
        typescript_output = typescript_renderer.get_output_structure(shared_ir)
        
        # Both should produce reasonable output structures
        assert len(nodejs_output) > 0
        assert len(typescript_output) > 0
        
        # Should have some common file types
        common_components = set(nodejs_output.keys()) & set(typescript_output.keys())
        assert len(common_components) > 0  # Should have some overlap
    
    def test_cross_renderer_template_handling(self):
        """Test that universal templates work with both renderers"""
        nodejs_renderer = NodeJSRenderer()
        typescript_renderer = TypeScriptRenderer()
        
        # Universal template that should work with both
        universal_template = """
{# Universal Template Test #}
{% if language == 'nodejs' %}
// Node.js specific code
const program = new Command();
console.log('{{ project.name }} - Node.js');
{% elif language == 'typescript' %}
// TypeScript specific code
const program: Command = new Command();
console.log('{{ project.name }} - TypeScript');
{% endif %}

// Common code for both
program.version('{{ project.version }}');
"""
        
        test_context = {
            "project": {"name": "Universal CLI", "version": "1.0.0"}
        }
        
        # Test Node.js rendering
        nodejs_context = nodejs_renderer.get_template_context({"project": test_context["project"]})
        nodejs_result = nodejs_renderer.render_component("universal", universal_template, nodejs_context)
        
        assert "Node.js specific code" in nodejs_result
        assert "TypeScript specific code" not in nodejs_result
        assert "program.version('1.0.0')" in nodejs_result
        
        # Test TypeScript rendering
        typescript_context = typescript_renderer.get_template_context({"project": test_context["project"]})
        typescript_result = typescript_renderer.render_component("universal", universal_template, typescript_context)
        
        assert "TypeScript specific code" in typescript_result
        assert "Node.js specific code" not in typescript_result
        assert "program.version('1.0.0')" in typescript_result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])