"""

Plugin system for Goobits CLI Framework.



Provides a secure, extensible plugin architecture with marketplace integration,

version management, and cross-language support.

"""



from .manager import PluginManager, PluginInfo, PluginRegistry

from .integration import setup_plugin_integration



def integrate_plugin_system(config_dict, language):

    """

    Integrate plugin system into CLI configuration.

    

    Args:

        config_dict: CLI configuration dictionary

        language: Target language (python, nodejs, typescript, rust)

        

    Returns:

        Enhanced configuration with plugin system support

    """

    # Create plugin integrator for the target language

    setup_plugin_integration(language)

    

    # Get enabled plugins

    plugin_manager = PluginManager()

    enabled_plugins = plugin_manager.list_plugins(status='enabled')

    

    # Add plugin configuration to CLI config

    if not config_dict.get('cli'):

        config_dict['cli'] = {}

    

    # Add plugin system configuration

    config_dict['cli']['plugin_system'] = {

        'enabled': True,

        'language': language,

        'plugins_dir': str(plugin_manager.plugins_dir),

        'enabled_plugins': [plugin.name for plugin in enabled_plugins],

        'plugin_discovery': True

    }

    

    # Add plugin loading capabilities to the CLI

    config_dict['cli']['features'] = config_dict['cli'].get('features', {})

    config_dict['cli']['features']['plugins'] = True

    

    return config_dict



__all__ = [

    'PluginManager',

    'PluginInfo', 

    'PluginRegistry',

    'integrate_plugin_system'

]