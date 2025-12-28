"""
Renderer Registry for the Universal Template System.

This module implements the Factory pattern for renderer instantiation,
satisfying the Dependency Inversion Principle (DIP) by allowing
consumers to depend on abstractions rather than concrete classes.
"""

from typing import Callable, Dict, Optional, Type

from .interface import LanguageRenderer


class RendererRegistry:
    """
    Registry for language-specific renderers.

    Implements the Factory pattern to decouple renderer consumers
    from concrete renderer implementations.

    Usage:
        registry = RendererRegistry()
        registry.register("python", PythonRenderer)
        renderer = registry.get("python")
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._renderers: Dict[str, Type[LanguageRenderer]] = {}
        self._factories: Dict[str, Callable[[], LanguageRenderer]] = {}
        self._instances: Dict[str, LanguageRenderer] = {}

    def register(
        self,
        language: str,
        renderer_class: Type[LanguageRenderer],
    ) -> None:
        """
        Register a renderer class for a language.

        Args:
            language: Language identifier (e.g., 'python', 'nodejs')
            renderer_class: Renderer class implementing LanguageRenderer
        """
        self._renderers[language] = renderer_class

    def register_factory(
        self,
        language: str,
        factory: Callable[[], LanguageRenderer],
    ) -> None:
        """
        Register a factory function for lazy instantiation.

        Args:
            language: Language identifier
            factory: Callable that returns a LanguageRenderer instance
        """
        self._factories[language] = factory

    def get(self, language: str, **kwargs) -> LanguageRenderer:
        """
        Get a renderer instance for the specified language.

        Args:
            language: Target language
            **kwargs: Arguments passed to renderer constructor

        Returns:
            LanguageRenderer instance

        Raises:
            ValueError: If no renderer is registered for the language
        """
        # Check for cached instance (singleton per language)
        if language in self._instances and not kwargs:
            return self._instances[language]

        # Try factory first
        if language in self._factories:
            instance = self._factories[language]()
            if not kwargs:
                self._instances[language] = instance
            return instance

        # Try direct class instantiation
        if language in self._renderers:
            instance = self._renderers[language](**kwargs)
            if not kwargs:
                self._instances[language] = instance
            return instance

        available = list(self._renderers.keys()) + list(self._factories.keys())
        raise ValueError(
            f"No renderer registered for language '{language}'. "
            f"Available: {available if available else 'none'}"
        )

    def has(self, language: str) -> bool:
        """
        Check if a renderer is registered for the language.

        Args:
            language: Language to check

        Returns:
            True if a renderer is registered
        """
        return language in self._renderers or language in self._factories

    def available_languages(self) -> list:
        """
        Get list of available languages.

        Returns:
            List of registered language identifiers
        """
        languages = set(self._renderers.keys()) | set(self._factories.keys())
        return sorted(languages)

    def clear(self) -> None:
        """Clear all registered renderers and cached instances."""
        self._renderers.clear()
        self._factories.clear()
        self._instances.clear()


# Global default registry instance
_default_registry: Optional[RendererRegistry] = None


def get_default_registry() -> RendererRegistry:
    """
    Get the default global registry, creating if needed.

    Returns:
        The default RendererRegistry instance
    """
    global _default_registry
    if _default_registry is None:
        _default_registry = RendererRegistry()
        _register_default_renderers(_default_registry)
    return _default_registry


def _register_default_renderers(registry: RendererRegistry) -> None:
    """
    Register the default renderers with lazy loading.

    Args:
        registry: Registry to populate
    """

    def python_factory():
        from .python_renderer import PythonRenderer

        return PythonRenderer()

    def nodejs_factory():
        from .nodejs_renderer import NodeJSRenderer

        return NodeJSRenderer()

    def typescript_factory():
        from .typescript_renderer import TypeScriptRenderer

        return TypeScriptRenderer()

    def rust_factory():
        from .rust_renderer import RustRenderer

        return RustRenderer()

    registry.register_factory("python", python_factory)
    registry.register_factory("nodejs", nodejs_factory)
    registry.register_factory("typescript", typescript_factory)
    registry.register_factory("rust", rust_factory)


def get_renderer(language: str, **kwargs) -> LanguageRenderer:
    """
    Convenience function to get a renderer from the default registry.

    Args:
        language: Target language
        **kwargs: Arguments passed to renderer constructor

    Returns:
        LanguageRenderer instance
    """
    return get_default_registry().get(language, **kwargs)


__all__ = [
    "RendererRegistry",
    "get_default_registry",
    "get_renderer",
]
