"""

Plugin system for Goobits CLI Framework.



Provides a secure, extensible plugin architecture with marketplace integration,

version management, and cross-language support.

"""



from .manager import PluginManager, PluginInfo, PluginRegistry



__all__ = [

    'PluginManager',

    'PluginInfo', 

    'PluginRegistry'

]