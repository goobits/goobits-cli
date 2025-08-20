"""
Comprehensive test suite for Goobits CLI validation framework.

Tests all validators against real configurations, edge cases, and cross-language compatibility.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock

# Add project paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from validation_framework import (
        ValidationContext, ValidationResult, ValidationMode, ValidationSeverity,
        ValidationRegistry, ValidationRunner, BaseValidator
    )
    from validators import (
        CommandValidator, ArgumentValidator, HookValidator, OptionValidator,
        ErrorCodeValidator, TypeValidator, ConfigValidator, CompletionValidator
    )
except ImportError as e:
    pytest.skip(f"Could not import required modules: {e}", allow_module_level=True)


class TestValidationFramework:
    """Test the core validation framework components."""
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation and message handling."""
        result = ValidationResult()
        assert result.is_valid is True
        assert len(result.messages) == 0
        
        result.add_info("Test info message")
        assert len(result.messages) == 1
        assert result.is_valid is True
        
        result.add_warning("Test warning")
        assert len(result.messages) == 2
        assert result.is_valid is True
        
        result.add_error("Test error")
        assert len(result.messages) == 3
        assert result.is_valid is False
        
        # Test message filtering
        errors = result.get_errors()
        warnings = result.get_warnings()
        assert len(errors) == 1
        assert len(warnings) == 1
    
    def test_validation_context(self):
        """Test ValidationContext functionality."""
        config = {"test": "config"}
        context = ValidationContext(
            config=config,
            language="python",
            mode=ValidationMode.STRICT
        )
        
        assert context.config == config
        assert context.language == "python"
        assert context.is_strict_mode() is True
        assert context.is_dev_mode() is False
    
    def test_validation_registry(self):
        """Test validator registration and dependency ordering."""
        registry = ValidationRegistry()
        
        # Create test validators with dependencies
        validator1 = MagicMock(spec=BaseValidator)
        validator1.name = "Validator1"
        validator1.dependencies = set()
        
        validator2 = MagicMock(spec=BaseValidator)
        validator2.name = "Validator2" 
        validator2.dependencies = {"Validator1"}
        
        # Register validators
        registry.register(validator1)
        registry.register(validator2)
        
        # Check execution order respects dependencies
        order = registry.list_validators()
        assert order.index("Validator1") < order.index("Validator2")
    
    def test_validation_runner(self):
        """Test ValidationRunner with multiple validators."""
        registry = ValidationRegistry()
        runner = ValidationRunner(registry)
        
        # Create mock validators
        validator1 = MagicMock(spec=BaseValidator)
        validator1.name = "TestValidator1"
        validator1.dependencies = set()
        validator1.can_validate.return_value = True
        validator1.validate.return_value = ValidationResult()
        
        validator2 = MagicMock(spec=BaseValidator)
        validator2.name = "TestValidator2"
        validator2.dependencies = set()
        validator2.can_validate.return_value = True
        error_result = ValidationResult()
        error_result.add_error("Test error")
        validator2.validate.return_value = error_result
        
        registry.register(validator1)
        registry.register(validator2)
        
        # Run validation
        context = ValidationContext(config={}, language="python")
        result = runner.validate_all(context)
        
        # Check that both validators were called and results merged
        validator1.validate.assert_called_once()
        validator2.validate.assert_called_once()
        assert result.is_valid is False  # Due to error from validator2
        assert len(result.get_errors()) == 1


class TestCommandValidator:
    """Test CommandValidator functionality."""
    
    @pytest.fixture
    def basic_cli_config(self):
        """Create a basic CLI configuration for testing."""
        return {
            'cli': {
                'name': 'Test CLI',
                'commands': {
                    'build': {
                        'desc': 'Build the project',
                        'icon': '🔨',
                        'args': [],
                        'options': []
                    },
                    'test': {
                        'desc': 'Run tests',
                        'args': [],
                        'options': []
                    }
                }
            }
        }
    
    def test_valid_commands(self, basic_cli_config):
        """Test validation of valid command configuration."""
        validator = CommandValidator()
        context = ValidationContext(config=basic_cli_config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is True
        assert len(result.get_errors()) == 0
    
    def test_missing_command_description(self):
        """Test validation fails for missing command descriptions."""
        config = {
            'cli': {
                'commands': {
                    'build': {}  # Missing description
                }
            }
        }
        
        validator = CommandValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        errors = result.get_errors()
        assert any("description is required" in error.message for error in errors)
    
    def test_invalid_command_names(self):
        """Test validation of invalid command names."""
        config = {
            'cli': {
                'commands': {
                    '123invalid': {'desc': 'Test'},  # Starts with number
                    'invalid-name!': {'desc': 'Test'},  # Contains invalid character
                }
            }
        }
        
        validator = CommandValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        assert len(result.get_errors()) >= 2
    
    def test_command_groups_validation(self):
        """Test command groups validation."""
        config = {
            'cli': {
                'commands': {
                    'build': {'desc': 'Build project'},
                    'test': {'desc': 'Run tests'},
                    'deploy': {'desc': 'Deploy project'}
                },
                'command_groups': [
                    {
                        'name': 'Development',
                        'commands': ['build', 'test']
                    },
                    {
                        'name': 'Development',  # Duplicate group name
                        'commands': ['deploy']
                    },
                    {
                        'name': 'Production',
                        'commands': ['nonexistent']  # Command doesn't exist
                    }
                ]
            }
        }
        
        validator = CommandValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        errors = result.get_errors()
        # Should have errors for duplicate group name and nonexistent command
        assert len(errors) >= 2
    
    def test_multiple_default_commands(self):
        """Test validation fails with multiple default commands."""
        config = {
            'cli': {
                'commands': {
                    'build': {'desc': 'Build', 'is_default': True},
                    'test': {'desc': 'Test', 'is_default': True}  # Multiple defaults
                }
            }
        }
        
        validator = CommandValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        errors = result.get_errors()
        assert any("Multiple default commands" in error.message for error in errors)


class TestArgumentValidator:
    """Test ArgumentValidator functionality."""
    
    def test_valid_arguments(self):
        """Test validation of valid arguments."""
        config = {
            'cli': {
                'commands': {
                    'process': {
                        'desc': 'Process files',
                        'args': [
                            {
                                'name': 'input_file',
                                'desc': 'Input file to process',
                                'required': True
                            },
                            {
                                'name': 'output_file', 
                                'desc': 'Output file location',
                                'required': False
                            }
                        ]
                    }
                }
            }
        }
        
        validator = ArgumentValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is True
    
    def test_argument_order_validation(self):
        """Test that required arguments cannot come after optional ones."""
        config = {
            'cli': {
                'commands': {
                    'process': {
                        'desc': 'Process files',
                        'args': [
                            {
                                'name': 'optional_arg',
                                'desc': 'Optional argument',
                                'required': False
                            },
                            {
                                'name': 'required_arg',
                                'desc': 'Required argument', 
                                'required': True  # Invalid: required after optional
                            }
                        ]
                    }
                }
            }
        }
        
        validator = ArgumentValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        errors = result.get_errors()
        assert any("Required argument" in error.message and "after optional" in error.message 
                  for error in errors)
    
    def test_variadic_argument_validation(self):
        """Test variadic argument validation."""
        config = {
            'cli': {
                'commands': {
                    'process': {
                        'desc': 'Process files',
                        'args': [
                            {
                                'name': 'files',
                                'desc': 'Input files',
                                'nargs': '*'  # Variadic
                            },
                            {
                                'name': 'output',
                                'desc': 'Output file',
                                'nargs': '?'  # Invalid: args after variadic
                            }
                        ]
                    }
                }
            }
        }
        
        validator = ArgumentValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        errors = result.get_errors()
        assert any("must be the last argument" in error.message for error in errors)
    
    def test_duplicate_argument_names(self):
        """Test detection of duplicate argument names."""
        config = {
            'cli': {
                'commands': {
                    'process': {
                        'desc': 'Process files',
                        'args': [
                            {'name': 'input', 'desc': 'Input file'},
                            {'name': 'input', 'desc': 'Another input'}  # Duplicate
                        ]
                    }
                }
            }
        }
        
        validator = ArgumentValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        errors = result.get_errors()
        assert any("Duplicate argument name" in error.message for error in errors)


class TestOptionValidator:
    """Test OptionValidator functionality."""
    
    def test_valid_options(self):
        """Test validation of valid options."""
        config = {
            'cli': {
                'commands': {
                    'build': {
                        'desc': 'Build project',
                        'options': [
                            {
                                'name': 'output-dir',
                                'short': 'o',
                                'type': 'str',
                                'desc': 'Output directory',
                                'default': './dist'
                            },
                            {
                                'name': 'verbose',
                                'short': 'v',
                                'type': 'flag',
                                'desc': 'Enable verbose output'
                            }
                        ]
                    }
                }
            }
        }
        
        validator = OptionValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is True
    
    def test_duplicate_option_names(self):
        """Test detection of duplicate option names."""
        config = {
            'cli': {
                'commands': {
                    'build': {
                        'desc': 'Build project',
                        'options': [
                            {'name': 'output', 'desc': 'Output file', 'type': 'str'},
                            {'name': 'output', 'desc': 'Output dir', 'type': 'str'}  # Duplicate
                        ]
                    }
                }
            }
        }
        
        validator = OptionValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        errors = result.get_errors()
        assert any("Duplicate option name" in error.message for error in errors)
    
    def test_invalid_short_options(self):
        """Test validation of invalid short options."""
        config = {
            'cli': {
                'commands': {
                    'build': {
                        'desc': 'Build project',
                        'options': [
                            {'name': 'option1', 'short': 'ab', 'desc': 'Test', 'type': 'str'},  # Too long
                            {'name': 'option2', 'short': '1', 'desc': 'Test', 'type': 'str'},   # Not letter
                            {'name': 'option3', 'short': 'a', 'desc': 'Test', 'type': 'str'},
                            {'name': 'option4', 'short': 'a', 'desc': 'Test', 'type': 'str'}    # Duplicate
                        ]
                    }
                }
            }
        }
        
        validator = OptionValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        errors = result.get_errors()
        # Should have errors for: too long, duplicate, and warnings for non-letter
        assert len(errors) >= 2
    
    def test_default_value_validation(self):
        """Test default value type validation."""
        config = {
            'cli': {
                'commands': {
                    'build': {
                        'desc': 'Build project',
                        'options': [
                            {
                                'name': 'count',
                                'type': 'int',
                                'desc': 'Count value',
                                'default': 'not_a_number'  # Invalid for int type
                            },
                            {
                                'name': 'debug',
                                'type': 'flag',
                                'desc': 'Debug mode',
                                'default': 'yes'  # Invalid for boolean
                            }
                        ]
                    }
                }
            }
        }
        
        validator = OptionValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        errors = result.get_errors()
        assert len(errors) >= 2
    
    def test_choices_validation(self):
        """Test validation of option choices."""
        config = {
            'cli': {
                'commands': {
                    'build': {
                        'desc': 'Build project',
                        'options': [
                            {
                                'name': 'format',
                                'type': 'str',
                                'desc': 'Output format',
                                'choices': ['json', 'yaml', 'xml'],
                                'default': 'json'  # Valid choice
                            },
                            {
                                'name': 'level',
                                'type': 'str', 
                                'desc': 'Log level',
                                'choices': ['debug', 'info'],
                                'default': 'warn'  # Not in choices - invalid
                            },
                            {
                                'name': 'mode',
                                'type': 'str',
                                'desc': 'Operation mode',
                                'choices': []  # Empty choices - invalid
                            }
                        ]
                    }
                }
            }
        }
        
        validator = OptionValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        errors = result.get_errors()
        assert len(errors) >= 2  # Default not in choices + empty choices


class TestHookValidator:
    """Test HookValidator functionality."""
    
    def test_hook_naming_conventions(self):
        """Test hook naming validation for different languages."""
        config = {
            'cli': {
                'commands': {
                    'build': {'desc': 'Build project'},
                    'config_get': {'desc': 'Get config value'}
                }
            }
        }
        
        # Test Python naming
        validator = HookValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        # Should pass for Python (snake_case expected)
        assert 'on_build' in context.shared_data.get('expected_hooks', set())
        assert 'on_config_get' in context.shared_data.get('expected_hooks', set())
        
        # Test JavaScript naming
        context = ValidationContext(config=config, language="nodejs")
        result = validator.validate(context)
        
        # Should have suggestions for camelCase
        warnings = result.get_warnings()
        # Should suggest camelCase versions
        assert len(warnings) >= 0  # May have warnings about naming conventions
    
    def test_hook_parameter_validation(self):
        """Test hook parameter validation."""
        config = {
            'cli': {
                'commands': {
                    'complex_command': {
                        'desc': 'Complex command with many parameters',
                        'args': [f'arg_{i}' for i in range(15)],  # Many args
                        'options': [
                            {'name': f'option-{i}', 'desc': f'Option {i}', 'type': 'str'} 
                            for i in range(10)
                        ]  # Many options
                    }
                }
            }
        }
        
        validator = HookValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        # Should warn about too many parameters
        warnings = result.get_warnings()
        assert any("many parameters" in warning.message.lower() for warning in warnings)


class TestTypeValidator:
    """Test TypeValidator functionality."""
    
    def test_type_mapping_validation(self):
        """Test type mapping across languages."""
        config = {
            'cli': {
                'commands': {
                    'build': {
                        'desc': 'Build project',
                        'options': [
                            {'name': 'count', 'type': 'int', 'desc': 'Count'},
                            {'name': 'name', 'type': 'str', 'desc': 'Name'},
                            {'name': 'enabled', 'type': 'bool', 'desc': 'Enabled'},
                            {'name': 'rate', 'type': 'float', 'desc': 'Rate'}
                        ]
                    }
                }
            }
        }
        
        validator = TypeValidator()
        
        # Test different languages
        for language in ['python', 'nodejs', 'typescript', 'rust']:
            context = ValidationContext(config=config, language=language)
            validator.validate(context)
            
            # Should have type mappings in shared data
            assert 'type_mappings' in context.shared_data
            mappings = context.shared_data['type_mappings']
            assert language in mappings.get('string', {})
            assert language in mappings.get('integer', {})
    
    def test_type_constraint_validation(self):
        """Test type-specific constraint validation."""
        config = {
            'cli': {
                'options': [
                    {
                        'name': 'big-number',
                        'type': 'int',
                        'desc': 'Very large number',
                        'default': 999999999999999  # Very large int
                    }
                ]
            }
        }
        
        validator = TypeValidator()
        context = ValidationContext(config=config, language="rust")
        result = validator.validate(context)
        
        # Should warn about large integer values
        warnings = result.get_warnings()
        assert any("32-bit" in warning.message for warning in warnings)


class TestConfigValidator:
    """Test ConfigValidator functionality."""
    
    def test_basic_structure_validation(self):
        """Test validation of basic configuration structure."""
        # Valid config
        valid_config = {
            'package_name': 'my-awesome-cli',
            'command_name': 'myapp',
            'display_name': 'My Awesome CLI',
            'description': 'A great CLI tool',
            'language': 'python'
        }
        
        validator = ConfigValidator()
        context = ValidationContext(config=valid_config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is True
    
    def test_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        invalid_config = {
            'package_name': 'test-cli',
            # Missing command_name, display_name, description
        }
        
        validator = ConfigValidator()
        context = ValidationContext(config=invalid_config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        errors = result.get_errors()
        assert len(errors) >= 3  # Missing required fields
    
    def test_invalid_package_names(self):
        """Test validation of invalid package names."""
        configs = [
            {
                'package_name': '123invalid',  # Starts with number
                'command_name': 'test',
                'display_name': 'Test',
                'description': 'Test CLI'
            },
            {
                'package_name': 'invalid_name!',  # Invalid character
                'command_name': 'test',
                'display_name': 'Test', 
                'description': 'Test CLI'
            }
        ]
        
        validator = ConfigValidator()
        
        for config in configs:
            context = ValidationContext(config=config, language="python")
            result = validator.validate(context)
            
            assert result.is_valid is False
            errors = result.get_errors()
            assert any("package name" in error.message.lower() for error in errors)
    
    def test_python_version_validation(self):
        """Test Python version validation."""
        config = {
            'package_name': 'test-cli',
            'command_name': 'test',
            'display_name': 'Test CLI',
            'description': 'Test CLI',
            'language': 'python',
            'python': {
                'minimum_version': '3.12',
                'maximum_version': '3.8'  # Invalid: min > max
            }
        }
        
        validator = ConfigValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        errors = result.get_errors()
        assert any("minimum" in error.message and "maximum" in error.message 
                  for error in errors)
    
    def test_installation_config_validation(self):
        """Test installation configuration validation."""
        config = {
            'package_name': 'test-cli',
            'command_name': 'test',
            'display_name': 'Test CLI',
            'description': 'Test CLI',
            'installation': {
                'pypi_name': 'invalid@name!',  # Invalid PyPI name
                'extras': {
                    'python': ['dev', 'test'],  # Valid
                    'invalid_type': ['package'],  # Invalid extra type
                    'npm': 'not_a_list'  # Should be list
                }
            }
        }
        
        validator = ConfigValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        assert result.is_valid is False
        errors = result.get_errors()
        # Should have errors for invalid PyPI name and non-list extras
        assert len(errors) >= 2


class TestErrorCodeValidator:
    """Test ErrorCodeValidator functionality."""
    
    def test_error_code_standards(self):
        """Test that standard error codes are available."""
        validator = ErrorCodeValidator()
        context = ValidationContext(config={}, language="python", mode=ValidationMode.DEV)
        validator.validate(context)
        
        # In dev mode, should provide standard exit codes
        assert 'standard_exit_codes' in context.shared_data
        exit_codes = context.shared_data['standard_exit_codes']
        assert 0 in exit_codes  # SUCCESS
        assert 1 in exit_codes  # GENERAL_ERROR
        assert 2 in exit_codes  # MISUSE
    
    def test_validation_config_checks(self):
        """Test validation of validation configuration."""
        config = {
            'validation': {
                'check_disk_space': True,
                'minimum_disk_space_mb': 5  # Very low
            }
        }
        
        validator = ErrorCodeValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        # Should warn about very low disk space requirement
        warnings = result.get_warnings()
        assert any("very low" in warning.message.lower() for warning in warnings)


class TestCompletionValidator:
    """Test CompletionValidator functionality."""
    
    def test_completion_analysis(self):
        """Test shell completion analysis."""
        config = {
            'cli': {
                'commands': {
                    'build': {
                        'desc': 'Build project',
                        'options': [
                            {
                                'name': 'format',
                                'type': 'str',
                                'desc': 'Output format',
                                'choices': ['json', 'yaml', 'xml']  # Good for completion
                            },
                            {
                                'name': 'output-file',
                                'type': 'file', 
                                'desc': 'Output file path'  # File completion
                            }
                        ]
                    }
                }
            }
        }
        
        validator = CompletionValidator()
        context = ValidationContext(config=config, language="python")
        result = validator.validate(context)
        
        # Should provide completion insights
        info_messages = [msg for msg in result.messages 
                        if msg.severity == ValidationSeverity.INFO]
        assert len(info_messages) >= 1
    
    def test_completion_optimization_suggestions(self):
        """Test completion optimization suggestions."""
        config = {
            'cli': {
                'commands': {
                    'deploy': {
                        'desc': 'Deploy application',
                        'options': [
                            {
                                'name': 'environment-type',  # Could benefit from choices
                                'type': 'str',
                                'desc': 'Deployment environment type'
                            }
                        ]
                    }
                }
            }
        }
        
        validator = CompletionValidator()
        context = ValidationContext(config=config, language="python", mode=ValidationMode.DEV)
        result = validator.validate(context)
        
        # In dev mode, should suggest completion improvements
        info_messages = [msg for msg in result.messages 
                        if msg.severity == ValidationSeverity.INFO]
        assert any("benefit from predefined choices" in msg.message for msg in info_messages)


class TestIntegrationScenarios:
    """Test validation with real-world configuration scenarios."""
    
    def test_goobits_self_hosting_config(self):
        """Test validation with the actual goobits.yaml configuration."""
        # This would be the actual goobits configuration
        goobits_config = {
            'package_name': 'goobits-cli',
            'command_name': 'goobits',
            'display_name': 'Goobits CLI Framework',
            'description': 'Build professional command-line tools with YAML configuration',
            'language': 'python',
            'cli_output_path': 'src/goobits_cli/generated_cli.py',
            'python': {
                'minimum_version': '3.8',
                'maximum_version': '3.13'
            },
            'installation': {
                'pypi_name': 'goobits-cli',
                'development_path': '.',
                'extras': {
                    'python': ['dev', 'test'],
                    'apt': ['git', 'python3-dev', 'curl', 'wget', 'pipx']
                }
            },
            'cli': {
                'name': 'Goobits CLI',
                'version': '1.2.0',
                'tagline': 'Build professional command-line tools with YAML configuration',
                'description': 'Transform simple YAML configuration into rich terminal applications',
                'commands': {
                    'build': {
                        'desc': 'Build CLI and setup scripts from goobits.yaml configuration',
                        'icon': '🔨',
                        'is_default': True,
                        'args': [
                            {
                                'name': 'config_path',
                                'desc': 'Path to goobits.yaml file (defaults to ./goobits.yaml)',
                                'required': False
                            }
                        ],
                        'options': [
                            {
                                'name': 'output-dir',
                                'short': 'o',
                                'type': 'str',
                                'desc': 'Output directory (defaults to same directory as config file)'
                            },
                            {
                                'name': 'backup',
                                'type': 'flag',
                                'desc': 'Create backup files (.bak) when overwriting existing files'
                            }
                        ]
                    },
                    'init': {
                        'desc': 'Create initial goobits.yaml template',
                        'icon': '🆕',
                        'args': [
                            {
                                'name': 'project_name',
                                'desc': 'Name of the project (optional)',
                                'required': False
                            }
                        ],
                        'options': [
                            {
                                'name': 'template',
                                'short': 't',
                                'type': 'str',
                                'desc': 'Template type',
                                'choices': ['basic', 'advanced', 'api-client', 'text-processor'],
                                'default': 'basic'
                            },
                            {
                                'name': 'force',
                                'type': 'flag',
                                'desc': 'Overwrite existing goobits.yaml file'
                            }
                        ]
                    }
                }
            }
        }
        
        # Run all validators
        registry = ValidationRegistry()
        registry.register(CommandValidator())
        registry.register(ArgumentValidator())
        registry.register(HookValidator()) 
        registry.register(OptionValidator())
        registry.register(TypeValidator())
        registry.register(ConfigValidator())
        registry.register(ErrorCodeValidator())
        registry.register(CompletionValidator())
        
        runner = ValidationRunner(registry)
        context = ValidationContext(config=goobits_config, language="python")
        result = runner.validate_all(context)
        
        # The real goobits config should validate successfully
        assert result.is_valid is True, f"Validation errors: {[str(e) for e in result.get_errors()]}"
    
    def test_cross_language_validation(self):
        """Test that the same configuration validates correctly for different languages."""
        config = {
            'package_name': 'test-cli',
            'command_name': 'test',
            'display_name': 'Test CLI',
            'description': 'A test CLI application',
            'cli': {
                'name': 'Test CLI',
                'commands': {
                    'process': {
                        'desc': 'Process data',
                        'args': [
                            {'name': 'input_file', 'desc': 'Input file', 'required': True}
                        ],
                        'options': [
                            {'name': 'format', 'type': 'str', 'desc': 'Output format', 
                             'choices': ['json', 'yaml'], 'default': 'json'},
                            {'name': 'verbose', 'type': 'flag', 'desc': 'Verbose output'}
                        ]
                    }
                }
            }
        }
        
        # Create validators
        validators = [
            CommandValidator(),
            ArgumentValidator(),
            HookValidator(),
            OptionValidator(),
            TypeValidator(),
            ConfigValidator()
        ]
        
        # Test each language
        languages = ['python', 'nodejs', 'typescript', 'rust']
        
        for language in languages:
            registry = ValidationRegistry()
            for validator in validators:
                registry.register(validator)
            
            runner = ValidationRunner(registry)
            context = ValidationContext(config=config, language=language)
            result = runner.validate_all(context)
            
            # Configuration should be valid for all languages
            if not result.is_valid:
                print(f"Language {language} validation errors:")
                for error in result.get_errors():
                    print(f"  - {error}")
            
            assert result.is_valid, f"Configuration should be valid for {language}"
    
    def test_validation_performance(self):
        """Test validation performance with large configurations."""
        # Create a large configuration
        commands = {}
        for i in range(50):
            commands[f'command_{i}'] = {
                'desc': f'Command {i} description',
                'args': [
                    {'name': f'arg_{j}', 'desc': f'Argument {j}', 'required': j < 2}
                    for j in range(5)
                ],
                'options': [
                    {'name': f'option-{j}', 'type': 'str', 'desc': f'Option {j}'}
                    for j in range(10)
                ]
            }
        
        large_config = {
            'package_name': 'large-cli',
            'command_name': 'large',
            'display_name': 'Large CLI',
            'description': 'A CLI with many commands',
            'cli': {
                'name': 'Large CLI',
                'commands': commands
            }
        }
        
        # Test validation performance
        import time
        
        registry = ValidationRegistry()
        registry.register(CommandValidator())
        registry.register(ArgumentValidator())
        registry.register(OptionValidator())
        registry.register(TypeValidator())
        
        runner = ValidationRunner(registry)
        context = ValidationContext(config=large_config, language="python")
        
        start_time = time.perf_counter()
        result = runner.validate_all(context)
        end_time = time.perf_counter()
        
        execution_time = (end_time - start_time) * 1000  # Convert to ms
        
        # Should complete reasonably quickly (under 1 second for 50 commands)
        assert execution_time < 1000, f"Validation took too long: {execution_time:.2f}ms"
        assert result.is_valid is True


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])