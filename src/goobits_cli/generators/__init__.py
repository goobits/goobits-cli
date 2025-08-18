"""Generator infrastructure for multi-language CLI code generation."""



from abc import ABC, abstractmethod

from typing import List, Optional

from ..schemas import GoobitsConfigSchema, ConfigSchema, CLISchema

from typing import Union





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





# Re-export for easier access

__all__ = ['BaseGenerator']