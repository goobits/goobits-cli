"""Generator infrastructure for multi-language CLI code generation."""

import json
import tomllib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Union

from ..schemas import GoobitsConfigSchema, ConfigSchema





class BaseGenerator(ABC):

    """Abstract base class for language-specific CLI generators."""

    

    @abstractmethod

    def generate(self, config: Union[ConfigSchema, GoobitsConfigSchema], 

                 config_filename: str, version: Optional[str] = None) -> str:

        """

        Generate CLI code for the target language.

        

        Args:

            config: The configuration object (ConfigSchema or GoobitsConfigSchema)

            config_filename: Name of the configuration file (e.g., "goobits.yaml")

            version: Optional version string to embed in generated code

            

        Returns:

            Generated CLI code as a string

        """

        pass

    

    @abstractmethod

    def get_output_files(self) -> List[str]:

        """

        Return list of files this generator creates.

        

        Returns:

            List of file paths relative to the output directory

        """

        pass

    

    @abstractmethod

    def get_default_output_path(self, package_name: str) -> str:

        """

        Get the default output path for the generated CLI file.

        

        Args:

            package_name: The package name

            

        Returns:

            Default output path with {package_name} placeholder

        """

        pass

    
    def generate_to_directory(self, config: Union[ConfigSchema, GoobitsConfigSchema], 
                              output_directory: str, config_filename: str = "goobits.yaml", 
                              version: Optional[str] = None) -> dict:
        """
        Generate CLI files and write them to the specified output directory.
        
        Default implementation that subclasses can override for more efficient handling.
        
        Args:
            config: The configuration object
            output_directory: Directory where files should be written  
            config_filename: Name of the configuration file (default: "goobits.yaml")
            version: Optional version string
            
        Returns:
            Dictionary mapping file paths to their contents
            
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement generate_to_directory() method"
        )

    

    def _extract_config_metadata(self, config: Union[ConfigSchema, GoobitsConfigSchema]) -> dict:

        """

        Extract metadata from configuration object.

        

        Args:

            config: The configuration object

            

        Returns:

            Dictionary with metadata fields

        """

        if hasattr(config, 'package_name'):  # GoobitsConfigSchema

            return {

                'cli_config': config.cli,

                'package_name': config.package_name,

                'command_name': config.command_name,

                'display_name': config.display_name,

                'installation': config.installation,

                'hooks_path': config.hooks_path,

                # Add additional metadata fields

                'author': getattr(config, 'author', ''),

                'email': getattr(config, 'email', ''),

                'license': getattr(config, 'license', 'MIT'),

                'homepage': getattr(config, 'homepage', ''),

                'repository': getattr(config, 'repository', ''),

                'keywords': getattr(config, 'keywords', []),

            }

        else:  # ConfigSchema

            cli = config.cli

            return {

                'cli_config': cli,

                'package_name': cli.name if cli else "",

                'command_name': cli.name if cli else "",

                'display_name': cli.name if cli else "",

                'installation': None,

                'hooks_path': None,

            }

    def _read_version_from_project_file(self, project_dir: Union[str, Path], language: str = "python") -> Optional[str]:
        """
        Read version from language-specific project files.
        
        Args:
            project_dir: Directory containing the project files
            language: Target language ("python", "nodejs", "typescript", "rust")
            
        Returns:
            Version string if found, None otherwise
        """
        project_path = Path(project_dir)
        
        try:
            if language == "python":
                # Try pyproject.toml first
                pyproject_path = project_path / "pyproject.toml"
                if pyproject_path.exists():
                    with open(pyproject_path, "rb") as f:
                        data = tomllib.load(f)
                        return data.get("project", {}).get("version")
                
                # Fallback to setup.py (less common)
                setup_py = project_path / "setup.py"
                if setup_py.exists():
                    # This is complex to parse, skip for now
                    pass
                    
            elif language in ["nodejs", "typescript"]:
                # Read from package.json
                package_json = project_path / "package.json"
                if package_json.exists():
                    with open(package_json, "r") as f:
                        data = json.load(f)
                        return data.get("version")
                        
            elif language == "rust":
                # Read from Cargo.toml
                cargo_toml = project_path / "Cargo.toml"
                if cargo_toml.exists():
                    with open(cargo_toml, "rb") as f:
                        data = tomllib.load(f)
                        return data.get("package", {}).get("version")
                        
        except Exception:
            # If file reading fails, return None
            pass
            
        return None

    def _get_dynamic_version(self, version: Optional[str], cli_config: Optional[ConfigSchema], 
                            language: str = "python", project_dir: str = ".") -> str:
        """
        Get version dynamically from multiple sources in order of preference.
        
        Args:
            version: Explicitly provided version
            cli_config: CLI configuration that might contain version
            language: Target language for project file detection
            project_dir: Directory to search for project files
            
        Returns:
            Version string (never None, falls back to '1.0.0')
        """
        # 1. Use explicitly provided version
        if version:
            return version
            
        # 2. Use CLI config version if available
        if cli_config and hasattr(cli_config, 'version') and cli_config.version:
            return cli_config.version
            
        # 3. Try to read from project file
        project_version = self._read_version_from_project_file(project_dir, language)
        if project_version:
            return project_version
            
        # 4. Final fallback
        return '1.0.0'



# Re-export for easier access

__all__ = ['BaseGenerator']