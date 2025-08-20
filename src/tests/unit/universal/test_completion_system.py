"""
Test suite for the dynamic completion system.

⚠️  MOSTLY FRAMEWORK-ONLY FEATURE: Advanced completion exists in framework but is minimally integrated.
    Users who run 'goobits build' get basic static completion only.
    
    Integration Status:
    - Framework: 70% complete (tested here)
    - User Integration: 10% complete (basic static completion)
    - Generated CLIs: Only command/option name completion
    
    These tests validate the framework implementation. Advanced dynamic completion
    (file paths, API endpoints, contextual suggestions) is not yet user-accessible.

Tests the DynamicCompletionRegistry, providers, and integration components.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, AsyncMock

from goobits_cli.universal.completion.registry import (
    DynamicCompletionRegistry, 
    CompletionProvider, 
    CompletionContext,
    get_completion_registry
)
from goobits_cli.universal.completion.providers import (
    FilePathCompletionProvider,
    EnvironmentVariableProvider,
    ConfigKeyProvider,
    HistoryProvider,
    setup_default_providers
)
from goobits_cli.universal.completion.integration import (
    InteractiveCompletionIntegrator,
    setup_completion_for_language
)


class MockCompletionProvider(CompletionProvider):
    """Mock completion provider for testing."""
    
    def __init__(self, priority: int = 50, test_completions: list = None):
        super().__init__(priority)
        self.test_completions = test_completions or ['test1', 'test2', 'test3']
    
    def can_provide(self, context: CompletionContext) -> bool:
        return context.current_word.startswith('test')
    
    async def provide_completions(self, context: CompletionContext) -> list:
        return [c for c in self.test_completions if c.startswith(context.current_word)]


class TestCompletionContext:
    """Test CompletionContext functionality."""
    
    def test_completion_context_creation(self):
        """Test creating completion context."""
        context = CompletionContext(
            current_command='test',
            current_word='tes',
            args=['test', 'arg1'],
            language='python'
        )
        
        assert context.current_command == 'test'
        assert context.current_word == 'tes' 
        assert context.args == ['test', 'arg1']
        assert context.language == 'python'
        assert isinstance(context.metadata, dict)
        assert isinstance(context.env, dict)


class TestDynamicCompletionRegistry:
    """Test DynamicCompletionRegistry functionality."""
    
    def setup_method(self):
        """Setup test registry."""
        self.registry = DynamicCompletionRegistry()
    
    def test_registry_initialization(self):
        """Test registry initializes properly."""
        assert self.registry.is_enabled()
        assert len(self.registry.get_providers()) == 0
        assert self.registry.get_statistics()['enabled']
    
    def test_provider_registration(self):
        """Test provider registration."""
        provider = MockCompletionProvider(priority=100)
        self.registry.register_provider(provider)
        
        providers = self.registry.get_providers()
        assert len(providers) == 1
        assert providers[0] == provider
    
    def test_provider_priority_ordering(self):
        """Test providers are ordered by priority."""
        provider1 = MockCompletionProvider(priority=30)
        provider2 = MockCompletionProvider(priority=100)
        provider3 = MockCompletionProvider(priority=50)
        
        self.registry.register_provider(provider1)
        self.registry.register_provider(provider2)
        self.registry.register_provider(provider3)
        
        providers = self.registry.get_providers()
        priorities = [p.get_priority() for p in providers]
        assert priorities == [100, 50, 30]  # Highest first
    
    def test_provider_unregistration(self):
        """Test provider unregistration."""
        provider = MockCompletionProvider()
        self.registry.register_provider(provider)
        assert len(self.registry.get_providers()) == 1
        
        self.registry.unregister_provider(provider)
        assert len(self.registry.get_providers()) == 0
    
    @pytest.mark.asyncio
    async def test_get_completions(self):
        """Test getting completions."""
        provider = MockCompletionProvider(test_completions=['test1', 'test2', 'testing'])
        self.registry.register_provider(provider)
        
        completions = await self.registry.get_completions(
            current_word='test',
            full_command='test command',
            language='python'
        )
        
        assert 'test1' in completions
        assert 'test2' in completions
        assert 'testing' in completions
    
    @pytest.mark.asyncio
    async def test_completion_caching(self):
        """Test completion result caching."""
        provider = MockCompletionProvider()
        self.registry.register_provider(provider)
        
        # First call
        completions1 = await self.registry.get_completions('test', 'test cmd', 'python')
        
        # Second call should use cache
        completions2 = await self.registry.get_completions('test', 'test cmd', 'python')
        
        assert completions1 == completions2
        
        # Clear cache and verify
        self.registry.clear_cache()
        stats = self.registry.get_statistics()
        assert stats['cache_size'] == 0
    
    def test_registry_enable_disable(self):
        """Test enabling/disabling registry."""
        assert self.registry.is_enabled()
        
        self.registry.disable()
        assert not self.registry.is_enabled()
        
        self.registry.enable()
        assert self.registry.is_enabled()
    
    @pytest.mark.asyncio
    async def test_disabled_registry(self):
        """Test that disabled registry returns no completions."""
        provider = MockCompletionProvider()
        self.registry.register_provider(provider)
        self.registry.disable()
        
        completions = await self.registry.get_completions('test', 'test cmd', 'python')
        assert completions == []


class TestFilePathCompletionProvider:
    """Test FilePathCompletionProvider."""
    
    def setup_method(self):
        """Setup test provider."""
        self.provider = FilePathCompletionProvider()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test files
        (self.temp_dir / 'test1.txt').touch()
        (self.temp_dir / 'test2.py').touch()
        (self.temp_dir / 'subdir').mkdir()
        (self.temp_dir / 'subdir' / 'nested.txt').touch()
    
    def test_can_provide_for_paths(self):
        """Test provider recognizes path contexts."""
        # Path-like input
        context = CompletionContext(current_word='/path/to/file')
        assert self.provider.can_provide(context)
        
        context = CompletionContext(current_word='./relative')
        assert self.provider.can_provide(context)
        
        context = CompletionContext(current_word='~/home')
        assert self.provider.can_provide(context)
        
        # File commands
        context = CompletionContext(current_command='cat', current_word='test')
        assert self.provider.can_provide(context)
    
    @pytest.mark.asyncio
    async def test_directory_completion(self):
        """Test completing directory contents."""
        context = CompletionContext(
            current_word='',
            cwd=self.temp_dir
        )
        
        completions = await self.provider.provide_completions(context)
        
        assert any('test1.txt' in c for c in completions)
        assert any('test2.py' in c for c in completions)
        assert any('subdir/' in c for c in completions)
    
    @pytest.mark.asyncio
    async def test_file_filtering(self):
        """Test file type filtering."""
        context = CompletionContext(
            current_word='test',
            cwd=self.temp_dir
        )
        
        completions = await self.provider.provide_completions(context)
        
        # Should include files starting with 'test'
        matching = [c for c in completions if c.startswith('test')]
        assert len(matching) >= 2


class TestEnvironmentVariableProvider:
    """Test EnvironmentVariableProvider."""
    
    def setup_method(self):
        """Setup test provider."""
        self.provider = EnvironmentVariableProvider()
    
    def test_can_provide_for_variables(self):
        """Test provider recognizes environment variable contexts."""
        # Variable syntax
        context = CompletionContext(current_word='$PATH')
        assert self.provider.can_provide(context)
        
        context = CompletionContext(current_word='${HOME')
        assert self.provider.can_provide(context)
        
        # Environment commands
        context = CompletionContext(current_command='env')
        assert self.provider.can_provide(context)
    
    @pytest.mark.asyncio
    async def test_variable_completion(self):
        """Test completing environment variables."""
        context = CompletionContext(
            current_word='$PAT',
            env={'PATH': '/usr/bin', 'PYTHONPATH': '/usr/lib/python'}
        )
        
        completions = await self.provider.provide_completions(context)
        
        assert '$PATH' in completions
        # Should not include PYTHONPATH as it doesn't start with 'PAT'


class TestConfigKeyProvider:
    """Test ConfigKeyProvider."""
    
    def setup_method(self):
        """Setup test provider."""
        self.provider = ConfigKeyProvider()
    
    def test_can_provide_for_config(self):
        """Test provider recognizes config contexts."""
        context = CompletionContext(
            config={'name': 'test', 'version': '1.0'}
        )
        assert self.provider.can_provide(context)
        
        context = CompletionContext(current_command='config')
        assert self.provider.can_provide(context)
    
    @pytest.mark.asyncio
    async def test_config_key_completion(self):
        """Test completing configuration keys."""
        context = CompletionContext(
            current_word='na',
            config={'name': 'test', 'version': '1.0', 'namespace': 'app'}
        )
        
        completions = await self.provider.provide_completions(context)
        
        assert 'name' in completions
        assert 'namespace' in completions
        assert 'version' not in completions  # Doesn't start with 'na'


class TestHistoryProvider:
    """Test HistoryProvider."""
    
    def setup_method(self):
        """Setup test provider."""
        self.provider = HistoryProvider()
    
    def test_can_provide_with_history(self):
        """Test provider works when history is available."""
        context = CompletionContext(history=['cmd1', 'cmd2'])
        assert self.provider.can_provide(context)
        
        context = CompletionContext(history=[])
        assert not self.provider.can_provide(context)
    
    @pytest.mark.asyncio
    async def test_history_completion(self):
        """Test completing from command history."""
        context = CompletionContext(
            current_word='cmd',
            history=['cmd1 arg1', 'cmd2 arg2', 'other command', 'cmd1 different']
        )
        
        completions = await self.provider.provide_completions(context)
        
        assert 'cmd1 arg1' in completions
        assert 'cmd2 arg2' in completions
        assert 'cmd1 different' in completions
        assert 'other command' not in completions


class TestInteractiveCompletionIntegrator:
    """Test InteractiveCompletionIntegrator."""
    
    def setup_method(self):
        """Setup test integrator."""
        self.integrator = InteractiveCompletionIntegrator('python')
    
    @pytest.mark.asyncio
    async def test_get_completions_for_interactive(self):
        """Test getting completions for interactive input."""
        # Mock the registry to return test completions
        with patch.object(self.integrator.registry, 'get_completions', 
                         AsyncMock(return_value=['test1', 'test2'])):
            
            completions = await self.integrator.get_completions_for_interactive('test input')
            
            assert completions == ['test1', 'test2']
    
    def test_create_completion_function(self):
        """Test creating readline-compatible completion function."""
        completion_func = self.integrator.create_completion_function()
        
        assert callable(completion_func)
        
        # Test the function (this would normally interact with readline)
        # We can't easily test the actual readline integration without mocking
        assert completion_func is not None


class TestProviderSetup:
    """Test provider setup utilities."""
    
    def test_setup_default_providers(self):
        """Test setting up default providers."""
        providers = setup_default_providers()
        
        assert len(providers) == 4  # File, Env, Config, History
        
        # Check types
        provider_types = [type(p).__name__ for p in providers]
        assert 'FilePathCompletionProvider' in provider_types
        assert 'EnvironmentVariableProvider' in provider_types
        assert 'ConfigKeyProvider' in provider_types
        assert 'HistoryProvider' in provider_types
    
    def test_setup_completion_for_language(self):
        """Test language-specific completion setup."""
        integrator = setup_completion_for_language('python')
        
        assert isinstance(integrator, InteractiveCompletionIntegrator)
        assert integrator.language == 'python'


class TestGlobalRegistry:
    """Test global registry functionality."""
    
    def test_global_registry_singleton(self):
        """Test that global registry is a singleton."""
        registry1 = get_completion_registry()
        registry2 = get_completion_registry()
        
        assert registry1 is registry2


if __name__ == '__main__':
    pytest.main([__file__])