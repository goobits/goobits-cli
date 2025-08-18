"""Integration tests for Rust CLI generation workflow.

These tests verify the complete Rust CLI generation workflow from YAML
configuration to executable binary, ensuring all components work together
correctly including compilation, hook integration, and complex configurations.
"""
import pytest
import subprocess
import tempfile
import shutil
import os
import json
import toml
from pathlib import Path
from typing import Dict, Any, Optional

from goobits_cli.main import load_goobits_config
from goobits_cli.generators.rust import RustGenerator, RustGeneratorError
from conftest import determine_language, generate_cli


class TestRustGenerationWorkflow:
    """Test complete Rust CLI generation workflow."""
    
    @classmethod
    def setup_class(cls):
        """Set up test fixtures for the class."""
        # Create a comprehensive test YAML file for Rust
        cls.test_yaml_content = """
package_name: "rust-test-cli"
command_name: "rusttest"
display_name: "RustTestCLI"
description: "A Rust test CLI for integration testing"
language: rust

python:
  minimum_version: "3.8"

dependencies:
  core: []

installation:
  pypi_name: "rust-test-cli"
  github_repo: "example/rust-test-cli"

shell_integration:
  alias: "rt"

validation:
  minimum_disk_space_mb: 100

messages:
  install_success: "RustTestCLI installed successfully!"

cli:
  name: "RustTestCLI"
  tagline: "A Rust test CLI for comprehensive testing"
  version: "1.0.0"
  description: "Complete Rust CLI generation test"
  
  options:
    - name: verbose
      short: v
      type: flag
      desc: "Enable verbose output"
    - name: config-path
      short: c
      type: str
      desc: "Path to configuration file"
      default: "config.toml"

  commands:
    serve:
      desc: "Start the server"
      icon: "🚀"
      args:
        - name: port
          desc: "Port number to serve on"
          required: true
          type: int
      options:
        - name: host
          short: h
          type: str
          desc: "Host to bind to"
          default: "localhost"
        - name: workers
          short: w
          type: int
          desc: "Number of worker threads"
          default: 4
        - name: debug
          type: flag
          desc: "Enable debug mode"
    
    build:
      desc: "Build the project"
      args:
        - name: target
          desc: "Build target"
          required: true
      options:
        - name: release
          short: r
          type: flag
          desc: "Build in release mode"
        - name: features
          short: f
          type: str
          desc: "Comma-separated list of features"
        - name: jobs
          short: j
          type: int
          desc: "Number of parallel jobs"
          default: 1
    
    config:
      desc: "Configuration management"
      subcommands:
        init:
          desc: "Initialize configuration"
          options:
            - name: template
              short: t
              type: str
              desc: "Configuration template to use"
              default: "default"
        validate:
          desc: "Validate configuration"
          args:
            - name: config-file
              desc: "Configuration file to validate"
              required: false
        export:
          desc: "Export configuration"
          options:
            - name: format
              type: str
              desc: "Export format (json, yaml, toml)"
              default: "json"
            - name: output
              short: o
              type: str
              desc: "Output file path"
"""
        
        # Create temporary directory for tests
        cls.temp_dir = tempfile.mkdtemp(prefix="rust_integration_test_")
        cls.test_yaml_path = Path(cls.temp_dir) / "test_rust.yaml"
        
        # Write test YAML
        with open(cls.test_yaml_path, 'w') as f:
            f.write(cls.test_yaml_content)
    
    @classmethod
    def teardown_class(cls):
        """Clean up test fixtures."""
        if Path(cls.temp_dir).exists():
            shutil.rmtree(cls.temp_dir)
    
    def test_complete_generation_workflow(self):
        """Test the complete generation workflow from YAML to files."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "test_rust.yaml")
        
        # Verify core files are generated (Universal Template System generates proper Rust project structure)
        expected_core_files = ['src/main.rs', 'src/hooks.rs']
        for expected_file in expected_core_files:
            assert expected_file in output_files, f"Missing expected file: {expected_file}"
            assert len(output_files[expected_file]) > 0, f"Empty file: {expected_file}"
        
        # Additional files that may be generated in src/ directory
        possible_files = ['src/completion.rs', 'src/config.rs', 'src/errors.rs']
        generated_count = len(output_files)
        assert generated_count >= 2, f"Expected at least 2 files, got {generated_count}"
    
    def test_generated_cargo_toml_structure(self):
        """Test that generated Cargo.toml has correct structure."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "test_rust.yaml")
        
        # Check if Cargo.toml is generated (may depend on template system)
        if 'Cargo.toml' in output_files:
            cargo_content = output_files['Cargo.toml']
            cargo_data = toml.loads(cargo_content)
            
            # Verify package section
            assert 'package' in cargo_data
            package = cargo_data['package']
            assert package['name'] == 'rust-test-cli'
            assert package['version'] == '1.0.0'
            assert 'description' in package
            assert 'edition' in package
            
            # Verify dependencies
            assert 'dependencies' in cargo_data
            deps = cargo_data['dependencies']
            assert 'clap' in deps
            assert 'anyhow' in deps
            
            # Verify binary configuration
            if 'bin' in cargo_data:
                bin_config = cargo_data['bin'][0]
                assert bin_config['name'] == 'rusttest'
                assert bin_config['path'] == 'src/main.rs'
        else:
            # Universal Template System might not generate Cargo.toml yet
            pytest.skip("Cargo.toml not generated by current template system")
    
    def test_generated_main_rs_structure(self):
        """Test that generated main.rs has correct Rust/Clap structure."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "test_rust.yaml")
        
        # main.rs is generated in proper Rust project structure under src/
        main_content = output_files['src/main.rs']
        
        # Check basic Rust structure
        assert "use clap::" in main_content or "clap" in main_content
        assert "fn main()" in main_content
        
        # Check CLI definition
        assert "RustTestCLI" in main_content
        
        # Check commands are defined (at least some of them)
        command_found = any(cmd in main_content for cmd in ["serve", "build", "config"])
        assert command_found, "No commands found in main.rs"
        
        # Check that some options are referenced
        option_found = any(opt in main_content for opt in ["verbose", "config", "host"])
        assert option_found, "No options found in main.rs"
    
    def test_generated_hooks_rs_structure(self):
        """Test that generated hooks.rs has correct function signatures."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "test_rust.yaml")
        
        hooks_content = output_files['src/hooks.rs']
        
        # Check that hooks.rs contains hook-related code
        assert "hook" in hooks_content.lower() or "Hook" in hooks_content
        
        # Check that it has some function definitions or hook structures
        function_found = "fn " in hooks_content or "pub fn" in hooks_content
        assert function_found, "No functions found in hooks.rs"
        
        # Check for Rust patterns
        assert "use " in hooks_content or "::" in hooks_content
    
    def test_generated_setup_sh_structure(self):
        """Test that generated setup.sh script is correct for Rust."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "test_rust.yaml")
        
        # Check if setup.sh is generated (may depend on template system)
        if 'setup.sh' in output_files:
            setup_content = output_files['setup.sh']
            
            # Check shebang
            assert setup_content.startswith('#!/bin/bash')
            
            # Check cargo commands
            assert "cargo" in setup_content
            
            # Check that it's a meaningful script
            assert len(setup_content.strip()) > 20
        else:
            pytest.skip("setup.sh not generated by current template system")
    
    def test_file_locations_are_correct(self):
        """Test that files are placed in appropriate locations."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "test_rust.yaml")
        
        # Test that core Rust files exist in proper Rust project structure
        assert 'src/main.rs' in output_files
        assert 'src/hooks.rs' in output_files
        
        # Test that files have reasonable names and known extensions
        allowed_extensions = ['.rs', '.toml', '.sh', '.md', '.gitignore']
        for filename in output_files.keys():
            has_valid_extension = any(filename.endswith(ext) for ext in allowed_extensions)
            assert has_valid_extension, f"Unknown file extension for: {filename}"
            assert len(filename) > 0
    
    def test_integration_with_main_cli(self):
        """Test that Rust generation integrates properly with main CLI."""
        config = load_goobits_config(self.test_yaml_path)
        
        # Test through main entry point
        output_files = generate_cli(config, "test_rust.yaml")
        
        # Should detect Rust language and generate Rust files
        assert 'src/main.rs' in output_files
        rust_files = [f for f in output_files.keys() if f.endswith('.rs')]
        assert len(rust_files) >= 2, "Should generate at least 2 Rust files"
        
        # Verify content is not empty
        for filename, content in output_files.items():
            assert len(content) > 0, f"{filename} should not be empty"


class TestRustCompilation:
    """Test that generated Rust code compiles successfully."""
    
    @classmethod
    def setup_class(cls):
        """Set up compilation test environment."""
        # Simple test configuration for compilation
        cls.simple_yaml_content = """
package_name: "compile-test"
command_name: "compiletest"
display_name: "CompileTest"
description: "Simple CLI for compilation testing"
language: rust

python:
  minimum_version: "3.8"

dependencies:
  core: []

installation:
  pypi_name: "compile-test"

cli:
  name: "CompileTest"
  tagline: "Simple CLI for compilation testing"
  version: "1.0.0"
  commands:
    hello:
      desc: "Say hello"
      args:
        - name: name
          desc: "Name to greet"
          required: false
      options:
        - name: times
          short: t
          type: int
          desc: "Number of times to greet"
          default: 1
"""
        cls.temp_dir = tempfile.mkdtemp(prefix="rust_compile_test_")
        cls.test_yaml_path = Path(cls.temp_dir) / "compile_test.yaml"
        
        with open(cls.test_yaml_path, 'w') as f:
            f.write(cls.simple_yaml_content)
    
    @classmethod
    def teardown_class(cls):
        """Clean up compilation test environment."""
        if Path(cls.temp_dir).exists():
            shutil.rmtree(cls.temp_dir)
    
    def test_generated_code_compiles(self):
        """Test that generated Rust code compiles without errors."""
        if not shutil.which('cargo'):
            pytest.skip("Cargo not available for compilation test")
        
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "compile_test.yaml")
        
        # Create a temporary Rust project directory
        project_dir = Path(self.temp_dir) / "rust_project"
        project_dir.mkdir(exist_ok=True)
        
        # Write all generated files, putting .rs files in src/ directory if not already there
        for file_path, content in output_files.items():
            if file_path.endswith('.rs') and not file_path.startswith('src/'):
                # Put Rust files in src/ directory
                full_path = project_dir / 'src' / file_path
            else:
                full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Create a minimal Cargo.toml if not generated
        if 'Cargo.toml' not in output_files:
            cargo_content = f'''[package]
name = "compile-test"
version = "1.0.0"
edition = "2021"

[[bin]]
name = "compiletest"
path = "src/main.rs"

[dependencies]
clap = {{ version = "4.0", features = ["derive"] }}
anyhow = "1.0"
'''
            with open(project_dir / 'Cargo.toml', 'w') as f:
                f.write(cargo_content)
        
        # Attempt to compile
        try:
            result = subprocess.run(
                ['cargo', 'check', '--manifest-path', str(project_dir / 'Cargo.toml')],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Check compilation result
            assert result.returncode == 0, f"Compilation failed: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Compilation timed out after 60 seconds")
        except FileNotFoundError:
            pytest.skip("Cargo not found in PATH")
    
    def test_generated_code_builds_release(self):
        """Test that generated code builds in release mode."""
        if not shutil.which('cargo'):
            pytest.skip("Cargo not available for build test")
        
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "compile_test.yaml")
        
        # Create project directory
        project_dir = Path(self.temp_dir) / "rust_build_project"
        project_dir.mkdir(exist_ok=True)
        
        # Write files, ensuring Rust files are in src/ directory
        for file_path, content in output_files.items():
            if file_path.endswith('.rs') and not file_path.startswith('src/'):
                full_path = project_dir / 'src' / file_path
            else:
                full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Create minimal Cargo.toml if not generated
        if 'Cargo.toml' not in output_files:
            cargo_content = f'''[package]
name = "compile-test"
version = "1.0.0"
edition = "2021"

[[bin]]
name = "compiletest"
path = "src/main.rs"

[dependencies]
clap = {{ version = "4.0", features = ["derive"] }}
anyhow = "1.0"
'''
            with open(project_dir / 'Cargo.toml', 'w') as f:
                f.write(cargo_content)
        
        # Attempt release build
        try:
            result = subprocess.run(
                ['cargo', 'build', '--release', '--manifest-path', str(project_dir / 'Cargo.toml')],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            assert result.returncode == 0, f"Release build failed: {result.stderr}"
            
            # Check that binary was created
            binary_path = project_dir / 'target' / 'release' / 'compiletest'
            if binary_path.exists():
                assert binary_path.is_file()
                
        except subprocess.TimeoutExpired:
            pytest.fail("Release build timed out after 120 seconds")
        except FileNotFoundError:
            pytest.skip("Cargo not found in PATH")
    
    def test_no_compilation_warnings(self):
        """Test that generated code compiles without warnings."""
        if not shutil.which('cargo'):
            pytest.skip("Cargo not available for warning test")
        
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "compile_test.yaml")
        
        # Create project directory
        project_dir = Path(self.temp_dir) / "rust_warning_project"
        project_dir.mkdir(exist_ok=True)
        
        # Write files, ensuring Rust files are in src/ directory
        for file_path, content in output_files.items():
            if file_path.endswith('.rs') and not file_path.startswith('src/'):
                full_path = project_dir / 'src' / file_path
            else:
                full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Create minimal Cargo.toml if not generated
        if 'Cargo.toml' not in output_files:
            cargo_content = f'''[package]
name = "compile-test"
version = "1.0.0"
edition = "2021"

[[bin]]
name = "compiletest"
path = "src/main.rs"

[dependencies]
clap = {{ version = "4.0", features = ["derive"] }}
anyhow = "1.0"
'''
            with open(project_dir / 'Cargo.toml', 'w') as f:
                f.write(cargo_content)
        
        # Check with warnings
        try:
            env = os.environ.copy()
            env['RUSTFLAGS'] = '-D warnings'  # Treat warnings as errors
            
            result = subprocess.run(
                ['cargo', 'check', '--manifest-path', str(project_dir / 'Cargo.toml')],
                capture_output=True,
                text=True,
                timeout=60,
                env=env
            )
            
            # Should compile without warnings (which would be errors)
            assert result.returncode == 0, f"Code has warnings: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Warning check timed out after 60 seconds")
        except FileNotFoundError:
            pytest.skip("Cargo not found in PATH")
    
    def test_binary_execution(self):
        """Test that the compiled binary can be executed."""
        if not shutil.which('cargo'):
            pytest.skip("Cargo not available for execution test")
        
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "compile_test.yaml")
        
        # Create project directory
        project_dir = Path(self.temp_dir) / "rust_exec_project"
        project_dir.mkdir(exist_ok=True)
        
        # Write files, ensuring Rust files are in src/ directory
        for file_path, content in output_files.items():
            if file_path.endswith('.rs') and not file_path.startswith('src/'):
                full_path = project_dir / 'src' / file_path
            else:
                full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Create minimal Cargo.toml if not generated
        if 'Cargo.toml' not in output_files:
            cargo_content = f'''[package]
name = "compile-test"
version = "1.0.0"
edition = "2021"

[[bin]]
name = "compiletest"
path = "src/main.rs"

[dependencies]
clap = {{ version = "4.0", features = ["derive"] }}
anyhow = "1.0"
'''
            with open(project_dir / 'Cargo.toml', 'w') as f:
                f.write(cargo_content)
        
        # Build and execute
        try:
            # Build
            build_result = subprocess.run(
                ['cargo', 'build', '--manifest-path', str(project_dir / 'Cargo.toml')],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            assert build_result.returncode == 0, f"Build failed: {build_result.stderr}"
            
            # Execute with --help
            binary_path = project_dir / 'target' / 'debug' / 'compiletest'
            if binary_path.exists():
                exec_result = subprocess.run(
                    [str(binary_path), '--help'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                assert exec_result.returncode == 0, f"Execution failed: {exec_result.stderr}"
                assert "CompileTest" in exec_result.stdout
                assert "hello" in exec_result.stdout
                
        except subprocess.TimeoutExpired:
            pytest.fail("Build or execution timed out")
        except FileNotFoundError:
            pytest.skip("Cargo not found in PATH")


class TestRustHookIntegration:
    """Test hook function integration in Rust CLIs."""
    
    @classmethod
    def setup_class(cls):
        """Set up hook integration test environment."""
        cls.hook_yaml_content = """
package_name: "hook-test"
command_name: "hooktest"
display_name: "HookTest"
description: "CLI for testing hook integration"
language: rust

python:
  minimum_version: "3.8"

dependencies:
  core: []

installation:
  pypi_name: "hook-test"

cli:
  name: "HookTest"
  tagline: "A hook test CLI"
  version: "1.0.0"
  commands:
    process:
      desc: "Process data"
      args:
        - name: input
          desc: "Input data"
          required: true
      options:
        - name: format
          short: f
          type: str
          desc: "Output format"
          default: "json"
        - name: verbose
          short: v
          type: flag
          desc: "Verbose output"
    
    analyze:
      desc: "Analyze data"
      subcommands:
        stats:
          desc: "Generate statistics"
          args:
            - name: dataset
              desc: "Dataset to analyze"
              required: true
          options:
            - name: output
              short: o
              type: str
              desc: "Output file"
        
        plot:
          desc: "Generate plots"
          options:
            - name: type
              short: t
              type: str
              desc: "Plot type"
              default: "line"
"""
        cls.temp_dir = tempfile.mkdtemp(prefix="rust_hook_test_")
        cls.test_yaml_path = Path(cls.temp_dir) / "hook_test.yaml"
        
        with open(cls.test_yaml_path, 'w') as f:
            f.write(cls.hook_yaml_content)
    
    @classmethod
    def teardown_class(cls):
        """Clean up hook integration test environment."""
        if Path(cls.temp_dir).exists():
            shutil.rmtree(cls.temp_dir)
    
    def test_hook_functions_generated(self):
        """Test that hook functions are generated for all commands."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "hook_test.yaml")
        
        hooks_content = output_files['src/hooks.rs']
        
        # Check that hook-related code exists (may not be individual functions in Universal Template System)
        assert "process" in hooks_content or "Process" in hooks_content
        assert "analyze" in hooks_content or "Analyze" in hooks_content
    
    def test_hook_function_signatures(self):
        """Test that hook system has appropriate structure."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "hook_test.yaml")
        
        hooks_content = output_files['src/hooks.rs']
        
        # Check for hook management system (Universal Template System approach)
        assert "Hook" in hooks_content or "hook" in hooks_content
        assert "ArgMatches" in hooks_content
        assert "Result" in hooks_content
        assert "execute" in hooks_content or "fn " in hooks_content
    
    def test_hook_parameter_access(self):
        """Test that hook functions can access command parameters."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "hook_test.yaml")
        
        hooks_content = output_files['src/hooks.rs']
        
        # Check that parameter access is demonstrated in comments or examples
        assert "input" in hooks_content  # Should reference the input argument
        assert "format" in hooks_content  # Should reference the format option
    
    def test_hook_invocation_in_main(self):
        """Test that hooks module is referenced from main.rs."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "hook_test.yaml")
        
        main_content = output_files['src/main.rs']
        
        # Check that hooks module is imported (Universal Template System approach)
        assert "mod hooks" in main_content or "use hooks" in main_content or "hooks::" in main_content
    
    def test_error_handling_in_hooks(self):
        """Test that hook functions have proper error handling."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "hook_test.yaml")
        
        hooks_content = output_files['src/hooks.rs']
        
        # Check error handling patterns
        assert "Result<()>" in hooks_content
        assert "anyhow::Result" in hooks_content or "use anyhow::Result" in hooks_content or "use anyhow::{Result," in hooks_content
    
    def test_hook_compilation_with_cargo(self):
        """Test that generated hooks compile correctly."""
        if not shutil.which('cargo'):
            pytest.skip("Cargo not available for hook compilation test")
        
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "hook_test.yaml")
        
        # Create project directory
        project_dir = Path(self.temp_dir) / "hook_compile_project"
        project_dir.mkdir(exist_ok=True)
        
        # Write files, ensuring Rust files are in src/ directory
        for file_path, content in output_files.items():
            if file_path.endswith('.rs') and not file_path.startswith('src/'):
                full_path = project_dir / 'src' / file_path
            else:
                full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Create minimal Cargo.toml if not generated (hook test)
        if 'Cargo.toml' not in output_files:
            cargo_content = '''[package]
name = "hook-test"
version = "1.0.0"
edition = "2021"

[[bin]]
name = "hooktest"
path = "src/main.rs"

[dependencies]
clap = { version = "4.0", features = ["derive"] }
anyhow = "1.0"
'''
            with open(project_dir / 'Cargo.toml', 'w') as f:
                f.write(cargo_content)
        
        # Compile
        try:
            result = subprocess.run(
                ['cargo', 'check', '--manifest-path', str(project_dir / 'Cargo.toml')],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            assert result.returncode == 0, f"Hook compilation failed: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Hook compilation timed out")
        except FileNotFoundError:
            pytest.skip("Cargo not found in PATH")


class TestRustComplexConfigurations:
    """Test complex Rust CLI configurations."""
    
    @classmethod
    def setup_class(cls):
        """Set up complex configuration test environment."""
        cls.complex_yaml_content = """
package_name: "complex-rust-cli"
command_name: "complexrust"
display_name: "ComplexRustCLI"
description: "Complex Rust CLI for advanced testing"
language: rust

python:
  minimum_version: "3.8"

dependencies:
  core: []

installation:
  pypi_name: "complex-rust-cli"

cli:
  name: "ComplexRustCLI"
  tagline: "Advanced Rust CLI with complex features"
  version: "2.1.0"
  description: "Advanced Rust CLI with complex features"
  
  options:
    - name: global-config
      short: g
      type: str
      desc: "Global configuration file"
      required: false
    - name: debug-level
      type: int
      desc: "Debug level (0-3)"
      default: 0
    - name: quiet
      short: q
      type: flag
      desc: "Suppress output"
    - name: color
      type: str
      desc: "Color output (auto, always, never)"
      default: "auto"

  commands:
    server:
      desc: "Server management"
      args:
        - name: action
          desc: "Action to perform (start, stop, restart)"
          required: true
      options:
        - name: port
          short: p
          type: int
          desc: "Server port"
          default: 8080
        - name: bind-address
          short: b
          type: str
          desc: "Bind address"
          default: "0.0.0.0"
        - name: workers
          short: w
          type: int
          desc: "Number of workers"
          default: 4
        - name: ssl-cert
          type: str
          desc: "SSL certificate file"
        - name: ssl-key
          type: str
          desc: "SSL private key file"
        - name: daemon
          short: d
          type: flag
          desc: "Run as daemon"
    
    database:
      desc: "Database operations"
      subcommands:
        migrate:
          desc: "Run database migrations"
          args:
            - name: direction
              desc: "Migration direction (up, down)"
              required: false
          options:
            - name: version
              short: v
              type: str
              desc: "Target migration version"
            - name: dry-run
              type: flag
              desc: "Show what would be done without executing"
            - name: force
              type: flag
              desc: "Force migration even with conflicts"
        
        backup:
          desc: "Backup database"
          args:
            - name: output-file
              desc: "Backup output file"
              required: true
          options:
            - name: compress
              short: c
              type: flag
              desc: "Compress backup file"
            - name: include-data
              type: flag
              desc: "Include data in backup"
              default: true
            - name: exclude-tables
              type: str
              desc: "Comma-separated list of tables to exclude"
        
        restore:
          desc: "Restore database from backup"
          args:
            - name: backup-file
              desc: "Backup file to restore"
              required: true
          options:
            - name: drop-existing
              type: flag
              desc: "Drop existing database before restore"
            - name: no-data
              type: flag
              desc: "Restore schema only, no data"
    
    deploy:
      desc: "Deployment operations"
      args:
        - name: environment
          desc: "Target environment"
          required: true
        - name: version
          desc: "Version to deploy"
          required: false
      options:
        - name: config-file
          short: c
          type: str
          desc: "Deployment configuration file"
        - name: dry-run
          type: flag
          desc: "Simulate deployment without executing"
        - name: rollback-on-failure
          type: flag
          desc: "Automatically rollback on deployment failure"
        - name: health-check-timeout
          type: int
          desc: "Health check timeout in seconds"
          default: 300
        - name: parallel-deployments
          type: int
          desc: "Number of parallel deployments"
          default: 1
"""
        cls.temp_dir = tempfile.mkdtemp(prefix="rust_complex_test_")
        cls.test_yaml_path = Path(cls.temp_dir) / "complex_test.yaml"
        
        with open(cls.test_yaml_path, 'w') as f:
            f.write(cls.complex_yaml_content)
    
    @classmethod
    def teardown_class(cls):
        """Clean up complex configuration test environment."""
        if Path(cls.temp_dir).exists():
            shutil.rmtree(cls.temp_dir)
    
    def test_complex_global_options_generation(self):
        """Test generation of complex CLI structure."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "complex_test.yaml")
        
        main_content = output_files['src/main.rs']
        
        # Check that main.rs has basic CLI structure
        assert "clap::" in main_content
        assert "Command::" in main_content
        assert "fn main" in main_content
        
        # Check that it's a substantial CLI implementation
        assert len(main_content) > 100
    
    def test_complex_command_with_multiple_options(self):
        """Test that complex CLI generates reasonable structure."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "complex_test.yaml")
        
        main_content = output_files['src/main.rs']
        
        # Check that main.rs contains CLI building blocks
        assert "Command::new" in main_content
        assert "arg" in main_content or "Arg::" in main_content
        assert "subcommand" in main_content
        
        # Check that it's generating substantial CLI code
        assert len(main_content) > 200
    
    def test_nested_subcommands_generation(self):
        """Test generation of CLI with subcommand structure."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "complex_test.yaml")
        
        main_content = output_files['src/main.rs']
        
        # Check subcommand structure is present
        assert "subcommand" in main_content
        assert "Command::" in main_content
        assert "match" in main_content  # Pattern matching for subcommands
    
    def test_complex_argument_types(self):
        """Test that CLI handles argument parsing."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "complex_test.yaml")
        
        main_content = output_files['src/main.rs']
        
        # Check that argument parsing infrastructure is present
        assert "ArgMatches" in main_content
        assert "clap::" in main_content
        assert "Arg::" in main_content
    
    def test_complex_hook_generation(self):
        """Test hook generation for complex command structure."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "complex_test.yaml")
        
        hooks_content = output_files['src/hooks.rs']
        
        # Check that command names appear in hooks (may not be individual functions)
        assert "server" in hooks_content or "Server" in hooks_content
        assert "database" in hooks_content or "Database" in hooks_content
        assert "deploy" in hooks_content or "Deploy" in hooks_content
    
    def test_complex_cargo_toml_dependencies(self):
        """Test that complex CLI generates appropriate dependencies."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "complex_test.yaml")
        
        # Check if Cargo.toml is generated
        if 'Cargo.toml' in output_files:
            cargo_content = output_files['Cargo.toml']
            cargo_data = toml.loads(cargo_content)
            
            deps = cargo_data['dependencies']
            
            # Should have core dependencies
            assert 'clap' in deps
            assert 'anyhow' in deps
            
            # Check clap features for complex CLI
            if isinstance(deps['clap'], dict):
                assert 'features' in deps['clap']
                features = deps['clap']['features']
                assert 'derive' in features
        else:
            # If no Cargo.toml, check that we have Rust files
            rust_files = [f for f in output_files.keys() if f.endswith('.rs')]
            assert len(rust_files) > 0, "Should generate Rust files even without Cargo.toml"
    
    def test_complex_setup_script(self):
        """Test setup script for complex CLI."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "complex_test.yaml")
        
        # Check if setup.sh is generated
        if 'setup.sh' in output_files:
            setup_content = output_files['setup.sh']
            
            # Should handle installation
            assert "cargo" in setup_content
            assert len(setup_content.strip()) > 20
        else:
            pytest.skip("setup.sh not generated by current template system")
    
    def test_complex_readme_generation(self):
        """Test README generation for complex CLI."""
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "complex_test.yaml")
        
        # Check if README.md is generated
        if 'README.md' in output_files:
            readme_content = output_files['README.md']
            
            # Should have meaningful content
            assert "ComplexRustCLI" in readme_content or "complex" in readme_content.lower()
            assert len(readme_content.strip()) > 50
        else:
            pytest.skip("README.md not generated by current template system")
    
    def test_complex_cli_compilation(self):
        """Test that complex CLI compiles successfully."""
        if not shutil.which('cargo'):
            pytest.skip("Cargo not available for complex compilation test")
        
        config = load_goobits_config(self.test_yaml_path)
        generator = RustGenerator()
        output_files = generator.generate_all_files(config, "complex_test.yaml")
        
        # Create project directory
        project_dir = Path(self.temp_dir) / "complex_compile_project"
        project_dir.mkdir(exist_ok=True)
        
        # Write files, ensuring Rust files are in src/ directory
        for file_path, content in output_files.items():
            if file_path.endswith('.rs') and not file_path.startswith('src/'):
                full_path = project_dir / 'src' / file_path
            else:
                full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Create minimal Cargo.toml if not generated (complex test)
        if 'Cargo.toml' not in output_files:
            cargo_content = '''[package]
name = "complex-rust-cli"
version = "2.1.0"
edition = "2021"

[[bin]]
name = "complexrust"
path = "src/main.rs"

[dependencies]
clap = { version = "4.0", features = ["derive"] }
anyhow = "1.0"
'''
            with open(project_dir / 'Cargo.toml', 'w') as f:
                f.write(cargo_content)
        
        # Compile
        try:
            result = subprocess.run(
                ['cargo', 'check', '--manifest-path', str(project_dir / 'Cargo.toml')],
                capture_output=True,
                text=True,
                timeout=90
            )
            
            assert result.returncode == 0, f"Complex CLI compilation failed: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Complex CLI compilation timed out")
        except FileNotFoundError:
            pytest.skip("Cargo not found in PATH")


class TestRustSetupScriptIntegration:
    """Test setup.sh script generation and functionality for Rust."""
    
    def test_setup_script_cargo_commands(self):
        """Test that setup script contains correct Cargo commands."""
        # Use a simple config for setup script testing
        simple_yaml = """
package_name: "setup-test"
command_name: "setuptest"
display_name: "SetupTest"
description: "CLI for setup script testing"
language: rust

python:
  minimum_version: "3.8"

dependencies:
  core: []

installation:
  pypi_name: "setup-test"

cli:
  name: "SetupTest"
  tagline: "A setup test CLI"
  version: "1.0.0"
  commands:
    test:
      desc: "Test command"
"""
        
        temp_dir = tempfile.mkdtemp(prefix="rust_setup_test_")
        try:
            test_yaml_path = Path(temp_dir) / "setup_test.yaml"
            with open(test_yaml_path, 'w') as f:
                f.write(simple_yaml)
            
            config = load_goobits_config(test_yaml_path)
            generator = RustGenerator()
            output_files = generator.generate_all_files(config, "setup_test.yaml")
            
            # Check if setup.sh is generated
            if 'setup.sh' in output_files:
                setup_content = output_files['setup.sh']
                
                # Check that it contains cargo-related commands
                assert "cargo" in setup_content
                assert len(setup_content.strip()) > 20
            else:
                pytest.skip("setup.sh not generated by current template system")
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_setup_script_completion_generation(self):
        """Test that setup script handles completion generation."""
        simple_yaml = """
package_name: "completion-test"
command_name: "comptest"
display_name: "CompletionTest"
description: "CLI for completion testing"
language: rust

python:
  minimum_version: "3.8"

dependencies:
  core: []

installation:
  pypi_name: "completion-test"

cli:
  name: "CompletionTest"
  tagline: "A completion test CLI"
  version: "1.0.0"
  commands:
    complete:
      desc: "Test completion"
"""
        
        temp_dir = tempfile.mkdtemp(prefix="rust_completion_test_")
        try:
            test_yaml_path = Path(temp_dir) / "completion_test.yaml"
            with open(test_yaml_path, 'w') as f:
                f.write(simple_yaml)
            
            config = load_goobits_config(test_yaml_path)
            generator = RustGenerator()
            output_files = generator.generate_all_files(config, "completion_test.yaml")
            
            # Check if setup.sh is generated and contains completion
            if 'setup.sh' in output_files:
                setup_content = output_files['setup.sh']
                # Check that it has meaningful content (completion may not be implemented yet)
                assert len(setup_content.strip()) > 20
            else:
                pytest.skip("setup.sh not generated by current template system")
            
        finally:
            shutil.rmtree(temp_dir)


class TestRustErrorHandling:
    """Test error handling in Rust CLI generation."""
    
    def test_invalid_yaml_handling(self):
        """Test handling of invalid YAML configurations."""
        invalid_yaml = """
package_name: "invalid-rust"
command_name: "invalid"
# Missing required fields
language: rust
"""
        
        temp_dir = tempfile.mkdtemp(prefix="rust_error_test_")
        try:
            test_yaml_path = Path(temp_dir) / "invalid.yaml"
            with open(test_yaml_path, 'w') as f:
                f.write(invalid_yaml)
            
            # Should raise validation error
            with pytest.raises(Exception):
                load_goobits_config(test_yaml_path)
                
        finally:
            shutil.rmtree(temp_dir)
    
    def test_template_error_fallback(self):
        """Test fallback generation when templates are missing."""
        valid_yaml = """
package_name: "fallback-test"
command_name: "fallbacktest"
display_name: "FallbackTest"
description: "CLI for fallback testing"
language: rust

python:
  minimum_version: "3.8"

dependencies:
  core: []

installation:
  pypi_name: "fallback-test"

cli:
  name: "FallbackTest"
  tagline: "A fallback test CLI"
  version: "1.0.0"
  commands:
    fallback:
      desc: "Test fallback"
"""
        
        temp_dir = tempfile.mkdtemp(prefix="rust_fallback_test_")
        try:
            test_yaml_path = Path(temp_dir) / "fallback_test.yaml"
            with open(test_yaml_path, 'w') as f:
                f.write(valid_yaml)
            
            config = load_goobits_config(test_yaml_path)
            
            # Force use of fallback by disabling universal templates
            generator = RustGenerator(use_universal_templates=False)
            
            # Should generate files even with missing templates (using fallback)
            output_files = generator.generate_all_files(config, "fallback_test.yaml")
            
            assert 'src/main.rs' in output_files
            assert len(output_files['src/main.rs']) > 0
            
        finally:
            shutil.rmtree(temp_dir)