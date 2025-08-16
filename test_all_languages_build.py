#!/usr/bin/env python3
"""
Comprehensive test to verify that all 4 languages can build working CLIs.

This test:
1. Generates CLIs for Python, Node.js, TypeScript, and Rust
2. Actually installs them using their package managers  
3. Executes commands to verify they work
4. Reports success/failure for each language

This is a REAL test, not mocking - it builds actual working CLIs.
"""

import os
import sys
import tempfile
import subprocess
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from goobits_cli.schemas import GoobitsConfigSchema
from goobits_cli.generators.python import PythonGenerator
from goobits_cli.generators.nodejs import NodeJSGenerator
from goobits_cli.generators.typescript import TypeScriptGenerator
from goobits_cli.generators.rust import RustGenerator


class LanguageBuildTester:
    """Test that all 4 languages can build working CLIs."""
    
    def __init__(self):
        self.results = {}
        self.temp_dirs = []
        self.installed_packages = []
    
    def cleanup(self):
        """Clean up test artifacts."""
        # Clean up installed packages
        for pkg_info in self.installed_packages:
            try:
                self._uninstall_package(pkg_info)
            except:
                pass
        
        # Clean up temp directories
        for temp_dir in self.temp_dirs:
            try:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
    
    def _uninstall_package(self, pkg_info):
        """Uninstall a package."""
        pm = pkg_info["manager"]
        name = pkg_info["name"]
        
        if pm == "pip":
            subprocess.run(["pip", "uninstall", "-y", name], capture_output=True)
        elif pm == "pipx":
            subprocess.run(["pipx", "uninstall", name], capture_output=True)
        elif pm == "npm":
            subprocess.run(["npm", "uninstall", "-g", name], capture_output=True)
        elif pm == "cargo":
            subprocess.run(["cargo", "uninstall", name], capture_output=True)
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check what package managers are available."""
        managers = {}
        
        for manager in ["python3", "pip", "pipx", "node", "npm", "yarn", "cargo", "rustc"]:
            managers[manager] = shutil.which(manager) is not None
        
        return managers
    
    def create_test_config(self, language: str) -> GoobitsConfigSchema:
        """Create a test configuration for the language."""
        config_data = {
            "package_name": f"test-build-{language}",
            "command_name": f"test-{language}",
            "display_name": f"Test {language.title()} CLI",
            "description": f"Test CLI build for {language}",
            "language": language,
            "version": "0.1.0",
            "author": "Test Author",
            "email": "test@example.com",
            "license": "MIT",
            "homepage": "https://github.com/test/test-cli",
            "repository": "https://github.com/test/test-cli",
            "keywords": ["test", "cli", language],
            "python": {
                "minimum_version": "3.8",
                "maximum_version": "3.13"
            },
            "dependencies": {
                "required": [],
                "optional": []
            },
            "installation": {
                "pypi_name": f"test-build-{language}",
                "development_path": ".",
                "extras": {
                    "python": [],
                    "apt": [],
                    "npm": []
                }
            },
            "shell_integration": {
                "enabled": False,
                "alias": f"test-{language}"
            },
            "validation": {
                "check_api_keys": False,
                "check_disk_space": True,
                "minimum_disk_space_mb": 10
            },
            "messages": {
                "install_success": "Installation completed successfully!",
                "install_dev_success": "Development installation completed successfully!",
                "upgrade_success": "Upgrade completed successfully!",
                "uninstall_success": "Uninstall completed successfully!"
            },
            "cli": {
                "name": f"Test{language.title()}CLI",
                "version": "0.1.0",
                "display_version": True,
                "tagline": f"A test CLI for {language} build validation",
                "description": f"This CLI tests that {language} builds work correctly",
                "icon": "🧪",
                "commands": {
                    "hello": {
                        "desc": "Say hello",
                        "args": [
                            {
                                "name": "name",
                                "desc": "Name to greet",
                                "required": False
                            }
                        ],
                        "options": [
                            {
                                "name": "loud",
                                "short": "l",
                                "type": "bool",
                                "desc": "Say it loudly",
                                "default": False
                            }
                        ]
                    },
                    "version": {
                        "desc": "Show version"
                    }
                }
            }
        }
        
        return GoobitsConfigSchema(**config_data)
    
    def test_python_build(self) -> Dict:
        """Test Python CLI generation and execution."""
        print("🐍 Testing Python CLI build...")
        
        result = {
            "language": "python",
            "success": False,
            "stages": {
                "generation": False,
                "installation": False,
                "execution": False
            },
            "error": None,
            "output": ""
        }
        
        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp(prefix="test_python_")
            self.temp_dirs.append(temp_dir)
            
            # Generate CLI
            config = self.create_test_config("python")
            generator = PythonGenerator()
            cli_code = generator.generate(config, "test_config.yaml")
            
            # Write CLI file
            cli_file = Path(temp_dir) / "cli.py"
            cli_file.write_text(cli_code)
            
            # Create setup.py
            setup_content = f'''
from setuptools import setup

setup(
    name="{config.package_name}",
    version="{config.version}",
    py_modules=["cli"],
    install_requires=[
        "rich-click>=1.0.0",
        "rich>=10.0.0",
    ],
    entry_points={{
        "console_scripts": [
            "{config.command_name}=cli:main",
        ],
    }},
    python_requires=">=3.8",
)
'''
            setup_file = Path(temp_dir) / "setup.py"
            setup_file.write_text(setup_content)
            
            result["stages"]["generation"] = True
            print("   ✅ Generation successful")
            
            # Install CLI
            install_result = subprocess.run([
                "pip", "install", "-e", "."
            ], cwd=temp_dir, capture_output=True, text=True)
            
            if install_result.returncode == 0:
                result["stages"]["installation"] = True
                self.installed_packages.append({"manager": "pip", "name": config.package_name})
                print("   ✅ Installation successful")
                
                # Test CLI execution
                test_result = subprocess.run([
                    config.command_name, "--help"
                ], capture_output=True, text=True)
                
                if test_result.returncode == 0:
                    result["stages"]["execution"] = True
                    result["output"] = test_result.stdout
                    result["success"] = True
                    print("   ✅ Execution successful")
                    
                    # Test hello command
                    hello_result = subprocess.run([
                        config.command_name, "hello", "World"
                    ], capture_output=True, text=True)
                    
                    if hello_result.returncode == 0:
                        print("   ✅ Hello command works")
                    else:
                        print(f"   ⚠️  Hello command failed: {hello_result.stderr}")
                        
                else:
                    result["error"] = f"CLI execution failed: {test_result.stderr}"
                    print(f"   ❌ Execution failed: {test_result.stderr}")
            else:
                result["error"] = f"Installation failed: {install_result.stderr}"
                print(f"   ❌ Installation failed: {install_result.stderr}")
                
        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ Error: {e}")
        
        return result
    
    def test_nodejs_build(self) -> Dict:
        """Test Node.js CLI generation and execution."""
        print("🟢 Testing Node.js CLI build...")
        
        result = {
            "language": "nodejs", 
            "success": False,
            "stages": {
                "generation": False,
                "installation": False,
                "execution": False
            },
            "error": None,
            "output": ""
        }
        
        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp(prefix="test_nodejs_")
            self.temp_dirs.append(temp_dir)
            
            # Generate CLI
            config = self.create_test_config("nodejs")
            generator = NodeJSGenerator()
            cli_code = generator.generate(config, "test_config.yaml")
            
            # Write CLI file
            cli_file = Path(temp_dir) / "cli.js"
            cli_file.write_text(cli_code)
            cli_file.chmod(0o755)
            
            # Create package.json
            package_json = {
                "name": config.package_name,
                "version": config.version,
                "description": config.description,
                "main": "cli.js",
                "bin": {
                    config.command_name: "./cli.js"
                },
                "dependencies": {
                    "commander": "^11.0.0"
                }
            }
            
            package_file = Path(temp_dir) / "package.json"
            package_file.write_text(json.dumps(package_json, indent=2))
            
            result["stages"]["generation"] = True
            print("   ✅ Generation successful")
            
            # Install dependencies
            npm_install = subprocess.run([
                "npm", "install"
            ], cwd=temp_dir, capture_output=True, text=True)
            
            if npm_install.returncode == 0:
                print("   ✅ Dependencies installed")
                
                # Link globally
                link_result = subprocess.run([
                    "npm", "link"
                ], cwd=temp_dir, capture_output=True, text=True)
                
                if link_result.returncode == 0:
                    result["stages"]["installation"] = True
                    self.installed_packages.append({"manager": "npm", "name": config.package_name})
                    print("   ✅ Global link successful")
                    
                    # Test CLI execution
                    test_result = subprocess.run([
                        config.command_name, "--help"
                    ], capture_output=True, text=True)
                    
                    if test_result.returncode == 0:
                        result["stages"]["execution"] = True
                        result["output"] = test_result.stdout
                        result["success"] = True
                        print("   ✅ Execution successful")
                    else:
                        result["error"] = f"CLI execution failed: {test_result.stderr}"
                        print(f"   ❌ Execution failed: {test_result.stderr}")
                else:
                    result["error"] = f"Global link failed: {link_result.stderr}"
                    print(f"   ❌ Global link failed: {link_result.stderr}")
            else:
                result["error"] = f"Dependencies install failed: {npm_install.stderr}"
                print(f"   ❌ Dependencies install failed: {npm_install.stderr}")
                
        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ Error: {e}")
        
        return result
    
    def test_typescript_build(self) -> Dict:
        """Test TypeScript CLI generation and execution."""
        print("🔷 Testing TypeScript CLI build...")
        
        result = {
            "language": "typescript",
            "success": False,
            "stages": {
                "generation": False,
                "compilation": False,
                "installation": False,
                "execution": False
            },
            "error": None,
            "output": ""
        }
        
        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp(prefix="test_typescript_")
            self.temp_dirs.append(temp_dir)
            
            # Generate CLI
            config = self.create_test_config("typescript")
            generator = TypeScriptGenerator()
            cli_code = generator.generate(config, "test_config.yaml")
            
            # Write CLI file
            cli_file = Path(temp_dir) / "cli.ts"
            cli_file.write_text(cli_code)
            
            # Create package.json
            package_json = {
                "name": config.package_name,
                "version": config.version,
                "description": config.description,
                "main": "dist/cli.js",
                "bin": {
                    config.command_name: "./dist/cli.js"
                },
                "scripts": {
                    "build": "tsc",
                    "start": "node dist/cli.js"
                },
                "dependencies": {
                    "commander": "^11.0.0"
                },
                "devDependencies": {
                    "typescript": "^5.0.0",
                    "@types/node": "^20.0.0"
                }
            }
            
            package_file = Path(temp_dir) / "package.json"
            package_file.write_text(json.dumps(package_json, indent=2))
            
            # Create tsconfig.json
            tsconfig = {
                "compilerOptions": {
                    "target": "ES2020",
                    "module": "commonjs",
                    "outDir": "./dist",
                    "rootDir": "./",
                    "strict": True,
                    "esModuleInterop": True,
                    "skipLibCheck": True,
                    "forceConsistentCasingInFileNames": True
                },
                "include": ["*.ts"],
                "exclude": ["node_modules", "dist"]
            }
            
            tsconfig_file = Path(temp_dir) / "tsconfig.json"
            tsconfig_file.write_text(json.dumps(tsconfig, indent=2))
            
            result["stages"]["generation"] = True
            print("   ✅ Generation successful")
            
            # Install dependencies
            npm_install = subprocess.run([
                "npm", "install"
            ], cwd=temp_dir, capture_output=True, text=True)
            
            if npm_install.returncode == 0:
                print("   ✅ Dependencies installed")
                
                # Compile TypeScript
                build_result = subprocess.run([
                    "npm", "run", "build"
                ], cwd=temp_dir, capture_output=True, text=True)
                
                if build_result.returncode == 0:
                    result["stages"]["compilation"] = True
                    print("   ✅ TypeScript compilation successful")
                    
                    # Make compiled CLI executable
                    compiled_cli = Path(temp_dir) / "dist" / "cli.js"
                    if compiled_cli.exists():
                        compiled_cli.chmod(0o755)
                        
                        # Add shebang if missing
                        content = compiled_cli.read_text()
                        if not content.startswith("#!"):
                            compiled_cli.write_text("#!/usr/bin/env node\n" + content)
                        
                        # Link globally
                        link_result = subprocess.run([
                            "npm", "link"
                        ], cwd=temp_dir, capture_output=True, text=True)
                        
                        if link_result.returncode == 0:
                            result["stages"]["installation"] = True
                            self.installed_packages.append({"manager": "npm", "name": config.package_name})
                            print("   ✅ Global link successful")
                            
                            # Test CLI execution
                            test_result = subprocess.run([
                                config.command_name, "--help"
                            ], capture_output=True, text=True)
                            
                            if test_result.returncode == 0:
                                result["stages"]["execution"] = True
                                result["output"] = test_result.stdout
                                result["success"] = True
                                print("   ✅ Execution successful")
                            else:
                                result["error"] = f"CLI execution failed: {test_result.stderr}"
                                print(f"   ❌ Execution failed: {test_result.stderr}")
                        else:
                            result["error"] = f"Global link failed: {link_result.stderr}"
                            print(f"   ❌ Global link failed: {link_result.stderr}")
                    else:
                        result["error"] = "Compiled CLI file not found"
                        print("   ❌ Compiled CLI file not found")
                else:
                    result["error"] = f"TypeScript compilation failed: {build_result.stderr}"
                    print(f"   ❌ TypeScript compilation failed: {build_result.stderr}")
            else:
                result["error"] = f"Dependencies install failed: {npm_install.stderr}"
                print(f"   ❌ Dependencies install failed: {npm_install.stderr}")
                
        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ Error: {e}")
        
        return result
    
    def test_rust_build(self) -> Dict:
        """Test Rust CLI generation and execution."""
        print("🦀 Testing Rust CLI build...")
        
        result = {
            "language": "rust",
            "success": False,
            "stages": {
                "generation": False,
                "compilation": False,
                "installation": False,
                "execution": False
            },
            "error": None,
            "output": ""
        }
        
        try:
            # Check if cargo is available
            if not shutil.which("cargo"):
                result["error"] = "Cargo not available - Rust not installed"
                print("   ❌ Cargo not available - Rust not installed")
                return result
            
            # Create temp directory
            temp_dir = tempfile.mkdtemp(prefix="test_rust_")
            self.temp_dirs.append(temp_dir)
            
            # Generate CLI
            config = self.create_test_config("rust")
            generator = RustGenerator()
            cli_code = generator.generate(config, "test_config.yaml")
            
            # Create src directory and main.rs
            src_dir = Path(temp_dir) / "src"
            src_dir.mkdir()
            main_file = src_dir / "main.rs"
            main_file.write_text(cli_code)
            
            # Create Cargo.toml
            cargo_toml = f'''[package]
name = "{config.package_name}"
version = "{config.version}"
edition = "2021"
description = "{config.description}"
authors = ["{config.author} <{config.email}>"]

[[bin]]
name = "{config.command_name}"
path = "src/main.rs"

[dependencies]
clap = {{ version = "4.0", features = ["derive"] }}
anyhow = "1.0"
'''
            
            cargo_file = Path(temp_dir) / "Cargo.toml"
            cargo_file.write_text(cargo_toml)
            
            result["stages"]["generation"] = True
            print("   ✅ Generation successful")
            
            # Build the project
            build_result = subprocess.run([
                "cargo", "build", "--release"
            ], cwd=temp_dir, capture_output=True, text=True)
            
            if build_result.returncode == 0:
                result["stages"]["compilation"] = True
                print("   ✅ Rust compilation successful")
                
                # Install the binary
                install_result = subprocess.run([
                    "cargo", "install", "--path", "."
                ], cwd=temp_dir, capture_output=True, text=True)
                
                if install_result.returncode == 0:
                    result["stages"]["installation"] = True
                    self.installed_packages.append({"manager": "cargo", "name": config.command_name})
                    print("   ✅ Installation successful")
                    
                    # Test CLI execution
                    test_result = subprocess.run([
                        config.command_name, "--help"
                    ], capture_output=True, text=True)
                    
                    if test_result.returncode == 0:
                        result["stages"]["execution"] = True
                        result["output"] = test_result.stdout
                        result["success"] = True
                        print("   ✅ Execution successful")
                    else:
                        result["error"] = f"CLI execution failed: {test_result.stderr}"
                        print(f"   ❌ Execution failed: {test_result.stderr}")
                else:
                    result["error"] = f"Installation failed: {install_result.stderr}"
                    print(f"   ❌ Installation failed: {install_result.stderr}")
            else:
                result["error"] = f"Rust compilation failed: {build_result.stderr}"
                print(f"   ❌ Rust compilation failed: {build_result.stderr}")
                
        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ Error: {e}")
        
        return result
    
    def run_all_tests(self) -> Dict:
        """Run tests for all languages."""
        print("🧪 Testing CLI builds for all 4 languages")
        print("=" * 60)
        
        # Check prerequisites
        prereqs = self.check_prerequisites()
        print("📋 Prerequisites:")
        for tool, available in prereqs.items():
            status = "✅" if available else "❌"
            print(f"   {status} {tool}")
        print()
        
        # Run tests
        test_results = []
        
        # Test all languages
        test_results.append(self.test_python_build())
        test_results.append(self.test_nodejs_build())
        test_results.append(self.test_typescript_build())
        test_results.append(self.test_rust_build())
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 RESULTS SUMMARY")
        print("=" * 60)
        
        for result in test_results:
            language = result["language"]
            success = result["success"]
            status = "✅ PASS" if success else "❌ FAIL"
            
            print(f"{status} {language.upper()}")
            
            if success:
                print(f"   All stages completed successfully")
            else:
                print(f"   Error: {result['error']}")
                
                # Show which stages passed
                for stage, passed in result["stages"].items():
                    stage_status = "✅" if passed else "❌"
                    print(f"   {stage_status} {stage}")
            print()
        
        # Overall summary
        successful_languages = sum(1 for r in test_results if r["success"])
        total_languages = len(test_results)
        
        print(f"🎯 OVERALL: {successful_languages}/{total_languages} languages passed")
        
        if successful_languages == total_languages:
            print("🎉 SUCCESS: All languages can build working CLIs!")
        elif successful_languages > 0:
            print("⚡ PARTIAL: Some languages working, others need attention")
        else:
            print("🚨 FAILURE: No languages are working")
        
        return {
            "successful_languages": successful_languages,
            "total_languages": total_languages,
            "results": test_results,
            "prerequisites": prereqs
        }


def main():
    """Main test function."""
    tester = LanguageBuildTester()
    
    try:
        results = tester.run_all_tests()
        
        # Exit with appropriate code
        if results["successful_languages"] == results["total_languages"]:
            sys.exit(0)  # All passed
        elif results["successful_languages"] > 0:
            sys.exit(1)  # Partial success
        else:
            sys.exit(2)  # All failed
            
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()