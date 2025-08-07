"""
Tests for enhanced Rust interactive mode functionality.

This module tests the advanced Rust-specific interactive features including:
- Enhanced command parsing with Result error handling
- Expression evaluation and compilation
- History management with persistence
- Tab completion for Rust ecosystem
- Documentation integration
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

try:
    from ..universal.interactive.rust_utils import (
        RustCommandParser, 
        RustCompletionProvider, 
        RustHistoryManager, 
        RustExpressionEvaluator, 
        RustDocumentationHelper,
        RustInteractiveEngine,
        RustCommand,
        CargoInfo
    )
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from goobits_cli.universal.interactive.rust_utils import (
        RustCommandParser, 
        RustCompletionProvider, 
        RustHistoryManager, 
        RustExpressionEvaluator, 
        RustDocumentationHelper,
        RustInteractiveEngine,
        RustCommand,
        CargoInfo
    )


class TestRustCommandParser:
    """Test Rust-specific command parsing with proper error handling."""
    
    def test_parse_simple_command(self):
        """Test parsing a simple command."""
        parser = RustCommandParser()
        
        command_schema = {
            'arguments': [],
            'options': []
        }
        
        command, error = parser.parse_command("build", command_schema)
        
        assert error is None
        assert command.name == "build"
        assert command.args == []
        assert command.options == {}
        assert command.flags == []
    
    def test_parse_command_with_arguments(self):
        """Test parsing command with positional arguments."""
        parser = RustCommandParser()
        
        command_schema = {
            'arguments': [
                {'name': 'input', 'required': True, 'rust_type': 'String'},
                {'name': 'output', 'required': False, 'rust_type': 'String'}
            ],
            'options': []
        }
        
        command, error = parser.parse_command("process file.txt result.txt", command_schema)
        
        assert error is None
        assert command.name == "process"
        assert command.args == ["file.txt", "result.txt"]
    
    def test_parse_command_with_options(self):
        """Test parsing command with options."""
        parser = RustCommandParser()
        
        command_schema = {
            'arguments': [],
            'options': [
                {'name': 'verbose', 'type': 'flag'},
                {'name': 'count', 'rust_type': 'i32'}
            ]
        }
        
        command, error = parser.parse_command("run --verbose --count 42", command_schema)
        
        assert error is None
        assert command.name == "run"
        assert "verbose" in command.flags
        assert command.options["count"] == 42
    
    def test_parse_command_type_conversion_error(self):
        """Test error handling for type conversion failures."""
        parser = RustCommandParser()
        
        command_schema = {
            'arguments': [],
            'options': [
                {'name': 'count', 'rust_type': 'i32'}
            ]
        }
        
        command, error = parser.parse_command("run --count invalid", command_schema)
        
        assert command is None
        assert "Invalid value for --count" in error
    
    def test_parse_command_missing_required_argument(self):
        """Test error handling for missing required arguments."""
        parser = RustCommandParser()
        
        command_schema = {
            'arguments': [
                {'name': 'input', 'required': True}
            ],
            'options': []
        }
        
        command, error = parser.parse_command("process", command_schema)
        
        assert command is None
        assert "requires at least 1 arguments" in error


class TestRustCompletionProvider:
    """Test advanced tab completion for Rust CLI commands."""
    
    @pytest.fixture
    def cli_schema(self):
        """Sample CLI schema for testing."""
        return {
            'commands': {
                'build': {
                    'options': [
                        {'name': 'release', 'type': 'flag'},
                        {'name': 'target', 'type': 'string'}
                    ],
                    'arguments': []
                },
                'test': {
                    'options': [
                        {'name': 'package', 'type': 'string'},
                        {'name': 'verbose', 'short': 'v', 'type': 'flag'}
                    ],
                    'arguments': []
                }
            }
        }
    
    @pytest.fixture
    def completion_provider(self, cli_schema):
        """Create completion provider for testing."""
        return RustCompletionProvider(cli_schema)
    
    def test_complete_command_names(self, completion_provider):
        """Test completion of command names."""
        completions = completion_provider.get_completions("b", "b")
        
        assert "build" in completions
        assert "help" in completions  # Built-in command
    
    def test_complete_option_names(self, completion_provider):
        """Test completion of option names."""
        completions = completion_provider.get_completions("--", "build --")
        
        assert "--release" in completions
        assert "--target" in completions
    
    def test_complete_short_options(self, completion_provider):
        """Test completion of short option names."""
        completions = completion_provider.get_completions("-", "test -")
        
        assert "-v" in completions
    
    def test_path_completion(self, completion_provider):
        """Test file and directory path completion."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.rs"
            test_file.write_text("// Test file")
            
            # Mock path completion to use temp directory
            with patch.object(Path, 'iterdir') as mock_iterdir:
                mock_iterdir.return_value = [test_file]
                
                completions = completion_provider._complete_paths("test", "file")
                assert any("test.rs" in comp for comp in completions)


class TestRustHistoryManager:
    """Test history management with persistence and search."""
    
    def test_history_initialization(self):
        """Test history manager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = Path(temp_dir) / "test_history.txt"
            manager = RustHistoryManager(str(history_file))
            
            assert manager.history_file == history_file
            assert manager.history == []
    
    def test_add_entry_deduplication(self):
        """Test smart deduplication when adding history entries."""
        manager = RustHistoryManager()
        
        manager.add_entry("cargo build")
        manager.add_entry("cargo test")
        manager.add_entry("cargo build")  # Duplicate
        
        assert len(manager.history) == 2
        assert manager.history[-1] == "cargo build"  # Most recent
    
    def test_search_history_regex(self):
        """Test history search with regex patterns."""
        manager = RustHistoryManager()
        
        manager.add_entry("cargo build --release")
        manager.add_entry("cargo test --verbose")
        manager.add_entry("rustc main.rs")
        
        results = manager.search_history("cargo.*build")
        
        assert len(results) == 1
        assert results[0][1] == "cargo build --release"
    
    def test_search_history_case_insensitive(self):
        """Test case-insensitive history search."""
        manager = RustHistoryManager()
        
        manager.add_entry("Cargo Build")
        
        results = manager.search_history("cargo", case_sensitive=False)
        
        assert len(results) == 1
        assert results[0][1] == "Cargo Build"
    
    def test_history_persistence(self):
        """Test history saving and loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = Path(temp_dir) / "test_history.txt"
            
            # Save history
            manager1 = RustHistoryManager(str(history_file))
            manager1.add_entry("cargo build")
            manager1.add_entry("cargo test")
            manager1.save_history()
            
            # Load history in new manager
            manager2 = RustHistoryManager(str(history_file))
            
            assert len(manager2.history) == 2
            assert "cargo build" in manager2.history
            assert "cargo test" in manager2.history


class TestRustExpressionEvaluator:
    """Test Rust expression evaluation and compilation."""
    
    @pytest.fixture
    def evaluator(self):
        """Create expression evaluator for testing."""
        return RustExpressionEvaluator()
    
    @patch('subprocess.run')
    def test_evaluate_simple_expression(self, mock_run, evaluator):
        """Test evaluating a simple Rust expression."""
        # Mock successful compilation
        mock_compile_result = Mock()
        mock_compile_result.returncode = 0
        mock_compile_result.stderr = ""
        
        # Mock successful execution
        mock_exec_result = Mock()
        mock_exec_result.returncode = 0
        mock_exec_result.stdout = "42\n"
        mock_exec_result.stderr = ""
        
        mock_run.side_effect = [mock_compile_result, mock_exec_result]
        
        result = evaluator.evaluate_expression("println!(\"{}\", 2 + 40);")
        
        assert result['success'] is True
        assert "42" in result['output']
    
    @patch('subprocess.run')
    def test_evaluate_expression_compilation_error(self, mock_run, evaluator):
        """Test handling compilation errors."""
        # Mock compilation failure
        mock_compile_result = Mock()
        mock_compile_result.returncode = 1
        mock_compile_result.stderr = "error: expected semicolon"
        
        mock_run.return_value = mock_compile_result
        
        result = evaluator.evaluate_expression("let x = 42")
        
        assert result['success'] is False
        assert "expected semicolon" in result['error']
    
    def test_generate_program_simple_expression(self, evaluator):
        """Test program generation for simple expressions."""
        program = evaluator._generate_program("2 + 2")
        
        assert "fn main()" in program
        assert "println!(\"{}\", (2 + 2));" in program
    
    def test_generate_program_statement(self, evaluator):
        """Test program generation for statements."""
        program = evaluator._generate_program("let x = 42; println!(\"{}\", x);")
        
        assert "fn main()" in program
        assert "let x = 42; println!(\"{}\", x);" in program
        assert not "println!(\"{}\", (" in program  # Should not wrap in println
    
    @patch('subprocess.run')
    def test_validate_syntax(self, mock_run, evaluator):
        """Test syntax validation without execution."""
        # Mock successful syntax check
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        
        mock_run.return_value = mock_result
        
        result = evaluator.validate_syntax("let x: i32 = 42;")
        
        assert result['valid'] is True
        assert result['errors'] == ""


class TestRustDocumentationHelper:
    """Test documentation integration and help system."""
    
    @pytest.fixture
    def doc_helper(self):
        """Create documentation helper for testing."""
        return RustDocumentationHelper()
    
    def test_search_documentation(self, doc_helper):
        """Test searching documentation for standard library items."""
        results = doc_helper.search_documentation("Vec")
        
        assert len(results) > 0
        assert any(result['name'] == 'Vec' for result in results)
        
        vec_result = next(result for result in results if result['name'] == 'Vec')
        assert "array" in vec_result['description'].lower()
    
    def test_get_function_signature(self, doc_helper):
        """Test getting function signatures."""
        signature = doc_helper.get_function_signature("println!")
        
        assert signature is not None
        assert "println!" in signature
        assert "Print to stdout" in signature
    
    @patch('subprocess.run')
    def test_get_std_doc(self, mock_run, doc_helper):
        """Test getting detailed standard library documentation."""
        # Mock rustc --explain output
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Vec<T> is a growable array type..."
        
        mock_run.return_value = mock_result
        
        doc = doc_helper.get_std_doc("Vec")
        
        assert doc is not None
        assert "growable array" in doc


class TestRustInteractiveEngine:
    """Test the complete enhanced interactive engine."""
    
    @pytest.fixture
    def cli_config(self):
        """Sample CLI configuration for testing."""
        return {
            'root_command': {
                'name': 'test-cli',
                'subcommands': [
                    {
                        'name': 'build',
                        'description': 'Build the project',
                        'arguments': [],
                        'options': []
                    }
                ]
            }
        }
    
    @pytest.fixture
    def engine(self, cli_config):
        """Create interactive engine for testing."""
        return RustInteractiveEngine(cli_config)
    
    def test_engine_initialization(self, engine):
        """Test proper initialization of the interactive engine."""
        assert engine.rust_parser is not None
        assert engine.completion_provider is not None
        assert engine.history_manager is not None
        assert engine.expression_evaluator is not None
        assert engine.documentation_helper is not None
    
    def test_rust_specific_commands_registered(self, engine):
        """Test that Rust-specific commands are registered."""
        assert 'cargo' in engine.commands
        assert 'eval' in engine.commands
        assert 'doc' in engine.commands
        assert 'validate' in engine.commands
        assert 'search-history' in engine.commands
        assert 'crate' in engine.commands
    
    def test_handle_eval_command(self, engine):
        """Test handling of expression evaluation commands."""
        with patch.object(engine.expression_evaluator, 'evaluate_expression') as mock_eval:
            mock_eval.return_value = {
                'success': True,
                'output': '42\n',
                'error': '',
                'compile_time': 0.5
            }
            
            # Should not raise exception
            engine.handle_eval_command(['2 + 40'])
            
            mock_eval.assert_called_once_with('2 + 40', True)
    
    def test_handle_doc_command(self, engine):
        """Test handling of documentation commands."""
        with patch.object(engine.documentation_helper, 'search_documentation') as mock_search:
            mock_search.return_value = [
                {'name': 'Vec', 'description': 'Dynamic array type'}
            ]
            
            # Should not raise exception
            engine.handle_doc_command(['Vec'])
            
            mock_search.assert_called_once_with('Vec')
    
    def test_handle_validate_command(self, engine):
        """Test handling of syntax validation commands."""
        with patch.object(engine.expression_evaluator, 'validate_syntax') as mock_validate:
            mock_validate.return_value = {'valid': True, 'errors': ''}
            
            # Should not raise exception
            engine.handle_validate_command(['let x = 42;'])
            
            mock_validate.assert_called_once_with('let x = 42;')
    
    def test_enhanced_completions(self, engine):
        """Test that enhanced completions work correctly."""
        completions = engine.get_completions("ca", "ca")
        
        assert "cargo" in completions
    
    def test_cargo_integration(self, engine):
        """Test integration with cargo commands."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            # Should not raise exception
            engine.handle_cargo_command(['check'])
            
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args[0] == 'cargo'
            assert args[1] == 'check'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])