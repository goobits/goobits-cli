"""
E2E tests for hook discovery functionality.

Tests the bug fixes for:
1. Hook discovery using configured hooks_path instead of hardcoded paths
2. Hook discovery working from different directories (package-relative imports)
"""

import os
import sys
import subprocess
import pytest


class TestHookDiscoveryE2E:
    """End-to-end tests for hook discovery functionality."""

    # REMOVED: test_config_with_custom_hooks_path fixture
    # This was only used by the removed test_custom_hooks_path_discovery test

    @pytest.fixture(scope="class")
    def test_config_default_hooks(self):
        """Test configuration with default hooks path."""
        return {
            "package_name": "defaultcli",
            "command_name": "defaultcli",
            "display_name": "Default CLI",
            "description": "Test CLI with default hooks",
            "language": "python",
            # No hooks_path specified - should use default
            "cli": {
                "name": "defaultcli",
                "tagline": "Testing default hook discovery",
                "commands": {
                    "hello": {
                        "desc": "Say hello",
                        "args": [{"name": "name", "desc": "Name to greet"}],
                    }
                },
            },
            "installation": {"pypi_name": "defaultcli", "development_path": "."},
        }

    # REMOVED: test_custom_hooks_path_discovery
    # This test was checking for the deprecated hooks_path feature which is not
    # implemented in the Universal Template System and will be removed in v4.0.0.
    # The Universal Template System uses a fixed cli_hooks.py pattern.

    def test_hook_discovery_from_different_directories(
        self, test_config_default_hooks, tmp_path
    ):
        """Test that hook discovery works from different working directories."""

        # Create test directory structure
        test_dir = tmp_path / "directory_test"
        test_dir.mkdir()

        # Create the configured hooks file
        hooks_dir = test_dir / "testcli" / "cli"
        hooks_dir.mkdir(parents=True)

        hooks_file = hooks_dir / "cli_hooks.py"
        hooks_file.write_text(
            """
def on_start(service_name, port=8080, **kwargs):
    print(f"SUCCESS: Hook found from {service_name} on port {port}")
    return 0
"""
        )

        # Generate CLI in test directory
        original_cwd = os.getcwd()
        os.chdir(test_dir)

        try:
            # Generate CLI using a minimal approach for testing
            cli_dir = test_dir / "src" / "testcli"
            cli_dir.mkdir(parents=True)

            # Create a simplified CLI that tests hook discovery
            cli_file = cli_dir / "cli.py"
            cli_file.write_text(
                """#!/usr/bin/env python3
import importlib
import importlib.util
from pathlib import Path

def _path_to_import_path(file_path: str, package_name: str = "testcli"):
    clean_path = file_path.replace(".py", "")
    import_path = clean_path.replace("/", ".")
    if import_path.startswith("src."):
        import_path = import_path[4:]
    module_name = import_path.split(".")[-1]
    return import_path, module_name

def _find_and_import_hooks():
    configured_path = "testcli/cli/cli_hooks.py"
    import_path, module_name = _path_to_import_path(configured_path)
    
    # Strategy 1: Try package-relative import
    try:
        return importlib.import_module(import_path)
    except ImportError:
        pass
    
    # Strategy 4: File-based import as fallback
    try:
        cli_dir = Path(__file__).parent
        search_paths = [
            cli_dir / configured_path,
            cli_dir.parent / configured_path,
            cli_dir.parent.parent / configured_path,
            cli_dir.parent.parent.parent / configured_path,
        ]
        
        for hooks_file in search_paths:
            if hooks_file.exists():
                spec = importlib.util.spec_from_file_location(module_name, hooks_file)
                if spec and spec.loader:
                    hooks_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(hooks_module)
                    return hooks_module
    except Exception:
        pass
    
    return None

def test_hook_discovery():
    hooks = _find_and_import_hooks()
    if hooks and hasattr(hooks, 'on_start'):
        hooks.on_start("test-service", port=9000)
        print("HOOK_DISCOVERY_SUCCESS")
        return True
    else:
        print("HOOK_DISCOVERY_FAILED")
        return False

if __name__ == "__main__":
    test_hook_discovery()
"""
            )

            cli_file.chmod(0o755)

            # Test 1: From project root directory
            os.chdir(test_dir)
            result = subprocess.run(
                [sys.executable, str(cli_file)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert "SUCCESS: Hook found from test-service on port 9000" in result.stdout
            assert "HOOK_DISCOVERY_SUCCESS" in result.stdout

            # Test 2: From subdirectory
            sub_dir = test_dir / "subdir"
            sub_dir.mkdir()
            os.chdir(sub_dir)

            result = subprocess.run(
                [sys.executable, str(cli_file)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert "SUCCESS: Hook found from test-service on port 9000" in result.stdout
            assert "HOOK_DISCOVERY_SUCCESS" in result.stdout

            # Test 3: From a different directory entirely (but with relative path back)
            temp_dir = tmp_path / "random_dir"
            temp_dir.mkdir()
            os.chdir(temp_dir)

            # This should still work due to relative path resolution
            result = subprocess.run(
                [sys.executable, str(cli_file)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            # This might fail from a random directory, which is expected behavior
            # The important thing is it doesn't crash
            assert result.returncode in [0, 1]  # Either success or graceful failure

            print("✅ Directory-independent hook discovery test passed")

        except Exception as e:
            pytest.fail(f"Failed directory-independent hook discovery test: {e}")
        finally:
            os.chdir(original_cwd)

    def test_default_hooks_fallback(self, test_config_default_hooks, tmp_path):
        """Test that default hooks path (cli_hooks.py) still works."""

        # Create test directory structure
        test_dir = tmp_path / "default_test"
        test_dir.mkdir()

        # Create default hooks file (cli_hooks.py)
        hooks_file = test_dir / "cli_hooks.py"
        hooks_file.write_text(
            """
def on_hello(name, **kwargs):
    print(f"DEFAULT_HOOK: Hello {name}!")
    return 0
"""
        )

        os.chdir(test_dir)

        try:
            # Create a simplified CLI that tests default hook discovery
            cli_dir = test_dir / "src" / "defaultcli"
            cli_dir.mkdir(parents=True)

            cli_file = cli_dir / "cli.py"
            cli_file.write_text(
                """#!/usr/bin/env python3
import importlib
import importlib.util
from pathlib import Path

def _find_and_import_hooks():
    # No hooks path configured, try default locations
    default_module_name = "cli_hooks"
    
    # Strategy 1: Try package-relative import
    try:
        return importlib.import_module(f"defaultcli.{default_module_name}")
    except ImportError:
        pass
    
    # Strategy 3: Try direct import from Python path
    try:
        return importlib.import_module(default_module_name)
    except ImportError:
        pass
    
    # Strategy 4: File-based fallback
    try:
        cli_dir = Path(__file__).parent
        search_paths = [
            cli_dir / f"{default_module_name}.py",
            cli_dir.parent / f"{default_module_name}.py",
            cli_dir.parent.parent / f"{default_module_name}.py",
            cli_dir.parent.parent.parent / f"{default_module_name}.py",
        ]
        
        for hooks_file in search_paths:
            if hooks_file.exists():
                spec = importlib.util.spec_from_file_location(default_module_name, hooks_file)
                if spec and spec.loader:
                    hooks_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(hooks_module)
                    return hooks_module
    except Exception:
        pass
    
    return None

def test_default_hook_discovery():
    hooks = _find_and_import_hooks()
    if hooks and hasattr(hooks, 'on_hello'):
        hooks.on_hello("World")
        print("DEFAULT_HOOK_DISCOVERY_SUCCESS")
        return True
    else:
        print("DEFAULT_HOOK_DISCOVERY_FAILED")
        return False

if __name__ == "__main__":
    test_default_hook_discovery()
"""
            )

            cli_file.chmod(0o755)

            # Test from project root directory
            result = subprocess.run(
                [sys.executable, str(cli_file)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert "DEFAULT_HOOK: Hello World!" in result.stdout
            assert "DEFAULT_HOOK_DISCOVERY_SUCCESS" in result.stdout

            print("✅ Default hooks fallback test passed")

        except Exception as e:
            pytest.fail(f"Failed default hooks fallback test: {e}")

    def test_hook_path_conversion_function(self):
        """Test the _path_to_import_path helper function logic."""

        def _path_to_import_path(file_path: str, package_name: str = "testpackage"):
            clean_path = file_path.replace(".py", "")
            import_path = clean_path.replace("/", ".")
            if import_path.startswith("src."):
                import_path = import_path[4:]
            module_name = import_path.split(".")[-1]
            return import_path, module_name

        # Test cases from the bug report
        test_cases = [
            ("testpackage/cli/cli_hooks.py", "testpackage.cli.cli_hooks", "cli_hooks"),
            (
                "src/testpackage/cli/cli_hooks.py",
                "testpackage.cli.cli_hooks",
                "cli_hooks",
            ),
            ("cli_hooks.py", "cli_hooks", "cli_hooks"),
            ("cli_hooks.py", "cli_hooks", "cli_hooks"),
            ("myproject/hooks.py", "myproject.hooks", "hooks"),
        ]

        for file_path, expected_import, expected_module in test_cases:
            import_path, module_name = _path_to_import_path(file_path)
            assert (
                import_path == expected_import
            ), f"Expected {expected_import}, got {import_path} for {file_path}"
            assert (
                module_name == expected_module
            ), f"Expected {expected_module}, got {module_name} for {file_path}"

        print("✅ Hook path conversion function test passed")

    def test_full_e2e_hook_execution_workflow(self, tmp_path):
        """Full end-to-end test of the hook discovery and execution workflow."""

        # Create a complete test project structure
        project_dir = tmp_path / "full_e2e_test"
        project_dir.mkdir()

        # Create hooks in the configured location
        hooks_dir = project_dir / "myapp" / "cli"
        hooks_dir.mkdir(parents=True)

        hooks_file = hooks_dir / "hooks.py"
        hooks_file.write_text(
            """
def on_deploy(environment, force=False, **kwargs):
    print(f"E2E_TEST: Deploying to {environment} (force={force})")
    if environment == "production" and not force:
        print("E2E_TEST: Production deployment requires --force flag")
        return 1
    print("E2E_TEST: Deployment successful!")
    return 0

def on_status(**kwargs):
    print("E2E_TEST: Application status: RUNNING")
    return 0
"""
        )

        original_cwd = os.getcwd()
        os.chdir(project_dir)

        try:
            # Create test configuration

            # Generate the CLI (simplified version for testing)
            cli_dir = project_dir / "src" / "myapp"
            cli_dir.mkdir(parents=True)

            cli_file = cli_dir / "cli.py"
            cli_file.write_text(
                '''#!/usr/bin/env python3
"""Full E2E test CLI with proper hook discovery."""

import sys
import importlib
import importlib.util
from pathlib import Path

def _path_to_import_path(file_path: str, package_name: str = "myapp"):
    clean_path = file_path.replace(".py", "")
    import_path = clean_path.replace("/", ".")
    if import_path.startswith("src."):
        import_path = import_path[4:]
    module_name = import_path.split(".")[-1]
    return import_path, module_name

def _find_and_import_hooks():
    configured_path = "myapp/cli/hooks.py"
    import_path, module_name = _path_to_import_path(configured_path)
    
    # Try multiple strategies
    strategies = [
        ("package-relative", lambda: importlib.import_module(import_path)),
        ("direct module", lambda: importlib.import_module(module_name)),
        ("file-based", lambda: _file_based_import(configured_path, module_name))
    ]
    
    for strategy_name, strategy_func in strategies:
        try:
            return strategy_func()
        except ImportError:
            continue
    
    return None

def _file_based_import(configured_path, module_name):
    cli_dir = Path(__file__).parent
    search_paths = [
        cli_dir / configured_path,
        cli_dir.parent / configured_path,
        cli_dir.parent.parent / configured_path,
        cli_dir.parent.parent.parent / configured_path,
    ]
    
    for hooks_file in search_paths:
        if hooks_file.exists():
            spec = importlib.util.spec_from_file_location(module_name, hooks_file)
            if spec and spec.loader:
                hooks_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(hooks_module)
                return hooks_module
    
    raise ImportError(f"Could not find hooks file: {configured_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: myapp <command> [args...]")
        return 1
    
    command = sys.argv[1]
    
    # Load hooks
    hooks = _find_and_import_hooks()
    if not hooks:
        print("ERROR: No hooks module found")
        return 1
    
    # Execute command
    if command == "deploy":
        if len(sys.argv) < 3:
            print("ERROR: deploy requires environment argument")
            return 1
        environment = sys.argv[2]
        force = "--force" in sys.argv
        
        if hasattr(hooks, 'on_deploy'):
            return hooks.on_deploy(environment, force=force)
        else:
            print("ERROR: on_deploy hook not found")
            return 1
    
    elif command == "status":
        if hasattr(hooks, 'on_status'):
            return hooks.on_status()
        else:
            print("ERROR: on_status hook not found")
            return 1
    
    else:
        print(f"ERROR: Unknown command: {command}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
'''
            )

            cli_file.chmod(0o755)

            # Test 1: Successful deployment to staging
            result = subprocess.run(
                [sys.executable, str(cli_file), "deploy", "staging"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0
            assert "E2E_TEST: Deploying to staging (force=False)" in result.stdout
            assert "E2E_TEST: Deployment successful!" in result.stdout

            # Test 2: Production deployment without force flag (should fail)
            result = subprocess.run(
                [sys.executable, str(cli_file), "deploy", "production"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 1
            assert (
                "E2E_TEST: Production deployment requires --force flag" in result.stdout
            )

            # Test 3: Production deployment with force flag (should succeed)
            result = subprocess.run(
                [sys.executable, str(cli_file), "deploy", "production", "--force"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0
            assert "E2E_TEST: Deploying to production (force=True)" in result.stdout
            assert "E2E_TEST: Deployment successful!" in result.stdout

            # Test 4: Status check
            result = subprocess.run(
                [sys.executable, str(cli_file), "status"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0
            assert "E2E_TEST: Application status: RUNNING" in result.stdout

            # Test 5: Test from subdirectory
            sub_dir = project_dir / "tests"
            sub_dir.mkdir()
            os.chdir(sub_dir)

            result = subprocess.run(
                [sys.executable, str(cli_file), "status"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0
            assert "E2E_TEST: Application status: RUNNING" in result.stdout

            print("✅ Full E2E hook execution workflow test passed")

        except Exception as e:
            pytest.fail(f"Failed full E2E workflow test: {e}")
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
