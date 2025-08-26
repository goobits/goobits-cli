"""

Dynamic Completion Registry for Goobits CLI Framework.



Provides intelligent, context-aware completion that adapts to user input,

command context, and available options across all supported languages.

"""

import os


from abc import ABC, abstractmethod

from dataclasses import dataclass, field

from typing import List, Dict, Any, Set, Callable

from pathlib import Path

import logging


logger = logging.getLogger(__name__)


@dataclass
class CompletionContext:
    """Context information for intelligent completion."""

    # Current command being typed

    current_command: str = ""

    # Partial word being completed

    current_word: str = ""

    # All arguments provided so far

    args: List[str] = field(default_factory=list)

    # Current working directory

    cwd: Path = field(default_factory=lambda: Path.cwd())

    # Environment variables

    env: Dict[str, str] = field(default_factory=dict)

    # Command history

    history: List[str] = field(default_factory=list)

    # Available commands and options

    available_commands: Set[str] = field(default_factory=set)

    available_options: Set[str] = field(default_factory=set)

    # Context-specific metadata

    metadata: Dict[str, Any] = field(default_factory=dict)

    # Language context (python, nodejs, typescript, rust)

    language: str = "python"

    # Configuration context

    config: Dict[str, Any] = field(default_factory=dict)


class CompletionProvider(ABC):
    """Abstract base class for completion providers."""

    def __init__(self, priority: int = 50):
        """Initialize provider with priority (higher = more important)."""

        self.priority = priority

        self.enabled = True

    @abstractmethod
    def can_provide(self, context: CompletionContext) -> bool:
        """Check if this provider can handle the current context."""

        pass

    @abstractmethod
    async def provide_completions(self, context: CompletionContext) -> List[str]:
        """Provide completion suggestions for the given context."""

        pass

    def get_priority(self) -> int:
        """Get provider priority."""

        return self.priority

    def is_enabled(self) -> bool:
        """Check if provider is enabled."""

        return self.enabled

    def enable(self) -> None:
        """Enable the provider."""

        self.enabled = True

    def disable(self) -> None:
        """Disable the provider."""

        self.enabled = False


class DynamicCompletionRegistry:
    """

    Registry for dynamic completion providers with context analysis.



    Features:

    - Multi-language support (Python, Node.js, TypeScript, Rust)

    - Context-aware completion suggestions

    - Plugin-based provider architecture

    - Intelligent caching and performance optimization

    - Cross-platform compatibility

    """

    def __init__(self):
        """Initialize the completion registry."""

        self._providers: List[CompletionProvider] = []

        self._context_analyzers: Dict[str, Callable] = {}

        self._completion_cache: Dict[str, List[str]] = {}

        self._cache_max_size = 1000

        self._enabled = True

        # Language-specific completion strategies

        self._language_strategies = {
            "python": self._python_completion_strategy,
            "nodejs": self._nodejs_completion_strategy,
            "typescript": self._typescript_completion_strategy,
            "rust": self._rust_completion_strategy,
        }

        # Initialize built-in context analyzers

        self._setup_context_analyzers()

    def _get_provider_priority(self, provider: CompletionProvider) -> int:
        """Get provider priority for sorting."""
        return provider.get_priority()

    def register_provider(self, provider: CompletionProvider) -> None:
        """Register a completion provider."""

        if provider not in self._providers:

            self._providers.append(provider)

            # Sort by priority (highest first)

            self._providers.sort(key=self._get_provider_priority, reverse=True)

            logger.debug(
                f"Registered completion provider: {provider.__class__.__name__}"
            )

    def unregister_provider(self, provider: CompletionProvider) -> None:
        """Unregister a completion provider."""

        if provider in self._providers:

            self._providers.remove(provider)

            logger.debug(
                f"Unregistered completion provider: {provider.__class__.__name__}"
            )

    def register_context_analyzer(self, name: str, analyzer: Callable) -> None:
        """Register a context analyzer function."""

        self._context_analyzers[name] = analyzer

        logger.debug(f"Registered context analyzer: {name}")

    async def get_completions(
        self, current_word: str, full_command: str, language: str = "python"
    ) -> List[str]:
        """

        Get completion suggestions for the current context.



        Args:

            current_word: The partial word being completed

            full_command: The full command line so far

            language: Target language (python, nodejs, typescript, rust)



        Returns:

            List of completion suggestions

        """

        if not self._enabled:

            return []

        # Check cache first

        cache_key = f"{language}:{current_word}:{full_command}"

        if cache_key in self._completion_cache:

            return self._completion_cache[cache_key]

        try:

            # Build context

            context = await self._build_context(current_word, full_command, language)

            # Get completions from all applicable providers

            all_completions = []

            for provider in self._providers:

                if provider.is_enabled() and provider.can_provide(context):

                    try:

                        completions = await provider.provide_completions(context)

                        all_completions.extend(completions)

                    except Exception as e:

                        logger.warning(
                            f"Provider {provider.__class__.__name__} failed: {e}"
                        )

            # Apply language-specific filtering and ranking

            strategy = self._language_strategies.get(
                language, self._default_completion_strategy
            )

            filtered_completions = strategy(context, all_completions)

            # Remove duplicates while preserving order

            unique_completions = []

            seen = set()

            for completion in filtered_completions:

                if completion not in seen:

                    unique_completions.append(completion)

                    seen.add(completion)

            # Cache results

            self._cache_completion(cache_key, unique_completions)

            return unique_completions

        except Exception as e:

            logger.error(f"Error getting completions: {e}")

            return []

    async def _build_context(
        self, current_word: str, full_command: str, language: str
    ) -> CompletionContext:
        """Build completion context from current input."""

        # Parse command line

        args = full_command.split()

        current_command = args[0] if args else ""

        # Get environment context

        env = dict(os.environ)

        # Build base context

        context = CompletionContext(
            current_command=current_command,
            current_word=current_word,
            args=args,
            cwd=Path.cwd(),
            env=env,
            language=language,
        )

        # Apply context analyzers

        for name, analyzer in self._context_analyzers.items():

            try:

                analyzer(context)

            except Exception as e:

                logger.warning(f"Context analyzer {name} failed: {e}")

        return context

    def _setup_context_analyzers(self) -> None:
        """Setup built-in context analyzers."""

        def command_analyzer(context: CompletionContext) -> None:
            """Analyze command structure and options."""

            # Extract available commands from help or config

            # This would be populated from the CLI configuration

            pass

        def file_analyzer(context: CompletionContext) -> None:
            """Analyze file system context."""

            # Set file-related metadata

            context.metadata["is_file_context"] = any(
                arg.startswith("-f") or arg.startswith("--file") for arg in context.args
            )

        def config_analyzer(context: CompletionContext) -> None:
            """Analyze configuration context."""

            # Load configuration if available

            config_files = [
                context.cwd / "goobits.yaml",
                context.cwd / ".goobits.yml",
                Path.home() / ".goobits" / "config.yaml",
            ]

            for config_file in config_files:

                if config_file.exists():

                    try:

                        import yaml

                        with open(config_file) as f:

                            context.config = yaml.safe_load(f) or {}

                        break

                    except Exception:

                        pass

        self.register_context_analyzer("command", command_analyzer)

        self.register_context_analyzer("file", file_analyzer)

        self.register_context_analyzer("config", config_analyzer)

    def _python_completion_strategy(
        self, context: CompletionContext, completions: List[str]
    ) -> List[str]:
        """Python-specific completion filtering and ranking."""

        # Prioritize Python-specific patterns

        python_priority = []

        other_completions = []

        for completion in completions:

            if (
                completion.endswith(".py")
                or completion.startswith("--")
                or completion in ["install", "build", "test", "lint"]
            ):

                python_priority.append(completion)

            else:

                other_completions.append(completion)

        return python_priority + other_completions

    def _nodejs_completion_strategy(
        self, context: CompletionContext, completions: List[str]
    ) -> List[str]:
        """Node.js-specific completion filtering and ranking."""

        # Prioritize Node.js patterns

        nodejs_priority = []

        other_completions = []

        for completion in completions:

            if (
                completion.endswith(".js")
                or completion.endswith(".json")
                or completion in ["install", "start", "test", "build"]
            ):

                nodejs_priority.append(completion)

            else:

                other_completions.append(completion)

        return nodejs_priority + other_completions

    def _typescript_completion_strategy(
        self, context: CompletionContext, completions: List[str]
    ) -> List[str]:
        """TypeScript-specific completion filtering and ranking."""

        # Prioritize TypeScript patterns

        ts_priority = []

        other_completions = []

        for completion in completions:

            if (
                completion.endswith(".ts")
                or completion.endswith(".tsx")
                or completion.endswith(".d.ts")
                or completion in ["compile", "type-check", "build"]
            ):

                ts_priority.append(completion)

            else:

                other_completions.append(completion)

        return ts_priority + other_completions

    def _rust_completion_strategy(
        self, context: CompletionContext, completions: List[str]
    ) -> List[str]:
        """Rust-specific completion filtering and ranking."""

        # Prioritize Rust patterns

        rust_priority = []

        other_completions = []

        for completion in completions:

            if (
                completion.endswith(".rs")
                or completion == "Cargo.toml"
                or completion in ["build", "test", "check", "clippy", "fmt"]
            ):

                rust_priority.append(completion)

            else:

                other_completions.append(completion)

        return rust_priority + other_completions

    def _default_completion_strategy(
        self, context: CompletionContext, completions: List[str]
    ) -> List[str]:
        """Default completion strategy for unknown languages."""

        return completions

    def _cache_completion(self, key: str, completions: List[str]) -> None:
        """Cache completion results with size management."""

        if len(self._completion_cache) >= self._cache_max_size:

            # Remove oldest entries (simple FIFO)

            oldest_keys = list(self._completion_cache.keys())[
                : self._cache_max_size // 2
            ]

            for old_key in oldest_keys:

                del self._completion_cache[old_key]

        self._completion_cache[key] = completions

    def clear_cache(self) -> None:
        """Clear the completion cache."""

        self._completion_cache.clear()

    def enable(self) -> None:
        """Enable the completion registry."""

        self._enabled = True

    def disable(self) -> None:
        """Disable the completion registry."""

        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if the registry is enabled."""

        return self._enabled

    def get_providers(self) -> List[CompletionProvider]:
        """Get all registered providers."""

        return self._providers.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""

        return {
            "providers_count": len(self._providers),
            "enabled_providers": len([p for p in self._providers if p.is_enabled()]),
            "cache_size": len(self._completion_cache),
            "cache_max_size": self._cache_max_size,
            "analyzers_count": len(self._context_analyzers),
            "enabled": self._enabled,
        }


# Global registry instance

_global_registry = DynamicCompletionRegistry()


def get_completion_registry() -> DynamicCompletionRegistry:
    """Get the global completion registry instance."""

    return _global_registry
