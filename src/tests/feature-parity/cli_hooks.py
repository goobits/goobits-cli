"""Hook implementations for the test CLI"""

import os
import sys
from pathlib import Path


def on_hello(name, greeting="Hello", verbose=False, config=None, **kwargs):
    """Say hello command"""
    print(f"{greeting} {name}")
    return 0


def on_config_get(key, verbose=False, config=None, **kwargs):
    """Get a config value"""
    # Simple mock config
    default_config = {
        "theme": os.environ.get("TEST_CLI_THEME", "default"),
        "api_key": "",
        "timeout": 30,
    }

    if key in default_config:
        print(f"{key}: {default_config[key]}")
        return 0
    else:
        print(f"Config key '{key}' not found", file=sys.stderr)
        return 1


def on_config_set(key, value, verbose=False, config=None, **kwargs):
    """Set a config value"""
    print(f"Setting {key} to {value}")
    return 0


def on_config_list(verbose=False, config=None, **kwargs):
    """List all config values"""
    default_config = {"theme": "default", "api_key": "", "timeout": 30}

    for key, value in default_config.items():
        print(f"{key}: {value}")
    return 0


def on_config_reset(force=False, verbose=False, config=None, **kwargs):
    """Reset config to defaults"""
    if not force:
        print(
            "Are you sure you want to reset the configuration? (y/N): ",
            end="",
            flush=True,
        )
        response = input().strip().lower()
        if response != "y":
            print("Reset cancelled")
            return 0

    print("Configuration reset to defaults")
    return 0


def on_fail(code=1, verbose=False, config=None, **kwargs):
    """Command that always fails"""
    print(f"Command failed with exit code {code}", file=sys.stderr)
    raise SystemExit(int(code))


def on_echo(words=None, text=None, verbose=False, config=None, **kwargs):
    """Echo arguments"""
    if words is None and text is not None:
        words = text if isinstance(text, list) else [str(text)]
    if words:
        print(" ".join(words))
    return 0


def on_file_create(path, content=None, verbose=False, config=None, **kwargs):
    """Create a file"""
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if content:
            file_path.write_text(content)
        else:
            file_path.touch()

        print(f"Created file: {path}")
        return 0
    except PermissionError:
        print(f"Permission denied: {path}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error creating file: {str(e)}", file=sys.stderr)
        return 1


def on_file_delete(path, verbose=False, config=None, **kwargs):
    """Delete a file"""
    try:
        file_path = Path(path)
        if not file_path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            return 1

        file_path.unlink()
        print(f"Deleted file: {path}")
        return 0
    except PermissionError:
        print(f"Permission denied: {path}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error deleting file: {str(e)}", file=sys.stderr)
        return 1


def on_config(verbose=False, config=None, **kwargs):
    """Config command group"""
    return 0


def on_file(verbose=False, config=None, **kwargs):
    """File command group"""
    return 0


def on_get(key=None, **kwargs):
    return on_config_get(key=key, **kwargs)


def on_set(key=None, value=None, **kwargs):
    return on_config_set(key=key, value=value, **kwargs)


def on_list(**kwargs):
    return on_config_list(**kwargs)


def on_reset(force=False, **kwargs):
    return on_config_reset(force=force, **kwargs)


def on_create(path=None, content=None, **kwargs):
    return on_file_create(path=path, content=content, **kwargs)


def on_delete(path=None, **kwargs):
    return on_file_delete(path=path, **kwargs)


def on_greet(
    name,
    message="Hello",
    style="casual",
    count=1,
    uppercase=False,
    language="en",
    **kwargs,
):
    text = f"{message}, {name}!"
    if uppercase:
        text = text.upper()
    for _ in range(max(1, int(count))):
        print(text)
    return 0


def on_info(format="text", verbose=False, sections="all", **kwargs):
    if format == "json":
        print('{"info":"CLI Information"}')
    else:
        print("CLI Information")
    return 0
