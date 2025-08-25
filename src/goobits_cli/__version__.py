"""Version information for goobits-cli."""



import tomllib

from pathlib import Path



def _get_version() -> str:

    """Read version from pyproject.toml"""

    try:

        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

        with open(pyproject_path, "rb") as f:

            data = tomllib.load(f)

        return str(data["project"]["version"])

    except Exception:

        # Fallback version if pyproject.toml can't be read

        return "3.0.0-beta.1"



__version__ = _get_version()