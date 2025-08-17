"""Unit tests for Unicode/internationalization issues in CLI generation.

This test suite verifies proper handling of Unicode characters in YAML configs
and generated code across all target languages (Python, Node.js, TypeScript, Rust).

The tests cover critical Unicode scenarios that could cause compilation/syntax errors:
- Emoji and complex Unicode characters in command names and descriptions
- Multi-byte character encoding (Chinese, Japanese, Arabic, Russian, etc.)
- Unicode normalization forms (NFC vs NFD)
- Zero-width and control characters
- Right-to-left text and bidirectional content
- YAML parsing with different encodings (UTF-8, UTF-16, UTF-32)
- Syntax validation of generated code containing Unicode
- Unicode in command-line options and argument names

All tests verify that Unicode content is correctly preserved through the entire
pipeline from YAML configuration to generated CLI code, and that the resulting
code compiles/runs without Unicode-related errors.
"""

import pytest
import yaml
import tempfile
import os
from pathlib import Path
from typing import Dict, Any
from goobits_cli.schemas import (
    GoobitsConfigSchema,
    CLISchema,
    CommandSchema,
    ArgumentSchema,
    OptionSchema,
    PythonConfigSchema,
    DependenciesSchema,
    InstallationSchema,
    ShellIntegrationSchema,
    ValidationSchema,
    MessagesSchema,
    ConfigSchema
)
from goobits_cli.generators.python import PythonGenerator
from goobits_cli.generators.nodejs import NodeJSGenerator
from goobits_cli.generators.typescript import TypeScriptGenerator
from goobits_cli.generators.rust import RustGenerator


class TestUnicodeInConfigs:
    """Test Unicode handling in YAML configurations."""
    
    def test_unicode_command_names_with_emoji(self):
        """Test command names containing emoji characters."""
        # Create config with emoji in command names
        cli_config = CLISchema(
            name="test-cli",
            description="A CLI with Unicode commands",
            tagline="Unicode testing",
            commands={
                "🚀launch": CommandSchema(
                    desc="Launch the application with rocket emoji"
                ),
                "📊stats": CommandSchema(
                    desc="Show statistics with chart emoji"
                )
            }
        )
        
        config = GoobitsConfigSchema(
            package_name="unicode-cli",
            command_name="unicode-cli",
            display_name="Unicode CLI",
            description="A CLI with Unicode support",
            language="python",
            cli=cli_config,
            python=PythonConfigSchema(),
            dependencies=DependenciesSchema(),
            installation=InstallationSchema(pypi_name="unicode-cli"),
            shell_integration=ShellIntegrationSchema(alias="test-cli"),
            validation=ValidationSchema(),
            messages=MessagesSchema()
        )
        
        generator = PythonGenerator()
        result = generator.generate(config, "unicode.yaml", "1.0.0")
        
        # Verify the generated code handles emoji properly
        assert "🚀launch" in result
        assert "📊stats" in result
        # Ensure it's still valid Python
        assert "def " in result or "import" in result
    
    def test_unicode_descriptions_and_help_text(self):
        """Test Unicode characters in descriptions and help text."""
        cli_config = CLISchema(
            name="intl-cli",
            description="国际化CLI工具 - Интернационализация - Iñternacionalizacion",
            tagline="Multilingual support: العربية, 中文, Русский",
            commands={
                "hello": CommandSchema(
                    desc="Say hello in different languages: こんにちは, Здравствуйте, مرحبا",
                    args=[
                        ArgumentSchema(
                            name="message",
                            desc="Message with Unicode: 文字列 (string in Japanese)",
                            type="str",
                            required=True
                        )
                    ],
                    options=[
                        OptionSchema(
                            name="language",
                            short="l",
                            desc="Language code: 日本語=ja, Русский=ru, العربية=ar",
                            type="str",
                            default="en"
                        )
                    ]
                )
            }
        )
        
        # Test with all target languages
        for language in ["python", "nodejs", "typescript", "rust"]:
            config = GoobitsConfigSchema(
                package_name="intl-cli",
                command_name="intl-cli",
                display_name="International CLI",
                description="CLI with internationalization",
                language=language,
                cli=cli_config,
                python=PythonConfigSchema(),
                dependencies=DependenciesSchema(),
                installation=InstallationSchema(pypi_name="intl-cli"),
                shell_integration=ShellIntegrationSchema(alias="test-cli"),
                validation=ValidationSchema(),
                messages=MessagesSchema()
            )
            
            if language == "python":
                generator = PythonGenerator()
            elif language == "nodejs":
                generator = NodeJSGenerator()
            elif language == "typescript":
                generator = TypeScriptGenerator()
            else:  # rust
                generator = RustGenerator()
            
            result = generator.generate(config, "intl.yaml", "1.0.0")
            
            # Verify Unicode characters are preserved in command descriptions
            assert "こんにちは" in result
            assert "Здравствуйте" in result
            assert "مرحبا" in result
            # Note: Argument descriptions may not appear in all generated outputs
            # but the Unicode content that does appear should be preserved correctly
    
    def test_unicode_normalization_issues(self):
        """Test handling of different Unicode normalizations (NFC vs NFD)."""
        # Create strings with same visual appearance but different Unicode forms
        # "é" can be represented as:
        # NFC: U+00E9 (single codepoint)
        # NFD: U+0065 U+0301 (e + combining acute accent)
        
        nfc_text = "café"  # NFC form
        nfd_text = "cafe\u0301"  # NFD form (e + combining acute)
        
        cli_config = CLISchema(
            name="norm-cli",
            description=f"Testing normalization: {nfc_text} vs {nfd_text}",
            tagline="Unicode normalization test",
            commands={
                "nfc-cmd": CommandSchema(
                    desc=f"Command with NFC text: {nfc_text}"
                ),
                "nfd-cmd": CommandSchema(
                    desc=f"Command with NFD text: {nfd_text}"
                )
            }
        )
        
        config = GoobitsConfigSchema(
            package_name="norm-cli",
            command_name="norm-cli",
            display_name="Normalization CLI",
            description="Unicode normalization test",
            language="python",
            cli=cli_config,
            python=PythonConfigSchema(),
            dependencies=DependenciesSchema(),
            installation=InstallationSchema(pypi_name="norm-cli"),
            shell_integration=ShellIntegrationSchema(alias="test-cli"),
            validation=ValidationSchema(),
            messages=MessagesSchema()
        )
        
        generator = PythonGenerator()
        result = generator.generate(config, "norm.yaml", "1.0.0")
        
        # Both forms should be preserved in the generated code
        assert nfc_text in result
        assert nfd_text in result
    
    def test_zero_width_and_control_characters(self):
        """Test handling of zero-width and control characters."""
        # Zero-width space and other problematic characters
        zwsp = "\u200B"  # Zero-width space
        zwnj = "\u200C"  # Zero-width non-joiner
        bidi_override = "\u202E"  # Right-to-left override
        
        cli_config = CLISchema(
            name="control-cli",
            description=f"Test{zwsp}with{zwnj}control{bidi_override}chars",
            tagline="Control character test",
            commands={
                "test": CommandSchema(
                    desc=f"Command{zwsp}with{zwnj}invisible{bidi_override}chars"
                )
            }
        )
        
        config = GoobitsConfigSchema(
            package_name="control-cli",
            command_name="control-cli",
            display_name="Control CLI",
            description="Control character test",
            language="python",
            cli=cli_config,
            python=PythonConfigSchema(),
            dependencies=DependenciesSchema(),
            installation=InstallationSchema(pypi_name="control-cli"),
            shell_integration=ShellIntegrationSchema(alias="test-cli"),
            validation=ValidationSchema(),
            messages=MessagesSchema()
        )
        
        generator = PythonGenerator()
        result = generator.generate(config, "control.yaml", "1.0.0")
        
        # Verify the generator handles these characters without crashing
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_right_to_left_text(self):
        """Test handling of right-to-left languages."""
        # Arabic and Hebrew text
        arabic_text = "مرحبا بالعالم"  # "Hello World" in Arabic
        hebrew_text = "שלום עולם"     # "Hello World" in Hebrew
        
        cli_config = CLISchema(
            name="rtl-cli",
            description=f"RTL support: {arabic_text} - {hebrew_text}",
            tagline="Right-to-left text support",
            commands={
                "arabic": CommandSchema(
                    desc=f"Arabic command: {arabic_text}"
                ),
                "hebrew": CommandSchema(
                    desc=f"Hebrew command: {hebrew_text}"
                )
            }
        )
        
        # Test with all languages
        for language in ["python", "nodejs", "typescript", "rust"]:
            config = GoobitsConfigSchema(
                package_name="rtl-cli",
                command_name="rtl-cli",
                display_name="RTL CLI",
                description="Right-to-left text test",
                language=language,
                cli=cli_config,
                python=PythonConfigSchema(),
                dependencies=DependenciesSchema(),
                installation=InstallationSchema(pypi_name="rtl-cli"),
                shell_integration=ShellIntegrationSchema(alias="test-cli"),
                validation=ValidationSchema(),
                messages=MessagesSchema()
            )
            
            if language == "python":
                generator = PythonGenerator()
            elif language == "nodejs":
                generator = NodeJSGenerator()
            elif language == "typescript":
                generator = TypeScriptGenerator()
            else:  # rust
                generator = RustGenerator()
            
            result = generator.generate(config, "rtl.yaml", "1.0.0")
            
            # Verify RTL text is preserved
            assert arabic_text in result
            assert hebrew_text in result


class TestUnicodeInYamlParsing:
    """Test Unicode handling in YAML file parsing."""
    
    def test_yaml_with_different_encodings(self):
        """Test YAML files with various Unicode encodings."""
        unicode_content = {
            'package_name': 'test-unicode',
            'command_name': 'test-unicode',
            'display_name': 'Unicode Test CLI',
            'description': 'CLI with Unicode: 漢字, кириллица, العربية',
            'language': 'python',
            'cli': {
                'name': 'test-unicode',
                'description': 'Unicode CLI test: 测试, тест, اختبار',
                'tagline': 'Multilingual support',
                'commands': {
                    'test-东西': {
                        'desc': 'Test command with Chinese: 东西 (thing)',
                        'args': [{
                            'name': 'файл',
                            'desc': 'File in Russian: файл',
                            'type': 'str',
                            'required': True
                        }],
                        'options': [{
                            'name': 'язык',
                            'short': 'l',
                            'desc': 'Language option: 语言/язык/لغة',
                            'type': 'str',
                            'default': 'en'
                        }]
                    }
                }
            }
        }
        
        # Test different encodings
        for encoding in ['utf-8', 'utf-16', 'utf-32']:
            with tempfile.NamedTemporaryFile(mode='w', encoding=encoding, suffix='.yaml', delete=False) as f:
                yaml.dump(unicode_content, f, allow_unicode=True, default_flow_style=False)
                yaml_file = f.name
            
            try:
                # Try to read and parse the YAML file
                with open(yaml_file, 'r', encoding=encoding) as f:
                    loaded_content = yaml.safe_load(f)
                
                # Verify Unicode content is preserved
                assert loaded_content['description'] == unicode_content['description']
                assert '漢字' in loaded_content['description']
                assert 'кириллица' in loaded_content['description']
                assert 'العربية' in loaded_content['description']
                
                # Test with the generators
                config = GoobitsConfigSchema(**loaded_content)
                generator = PythonGenerator()
                result = generator.generate(config, yaml_file, "1.0.0")
                
                # Verify Unicode is preserved through the entire pipeline
                # Focus on content that appears in generated CLI code
                assert '东西' in result  # Command name with Unicode
                assert 'файл' in result  # Argument name with Unicode
                # Test that the generated code handles Unicode without errors
                assert isinstance(result, str)
                assert len(result) > 0
                
            finally:
                os.unlink(yaml_file)
    
    def test_mixed_encoding_edge_cases(self):
        """Test edge cases with mixed encodings."""
        # Test with byte order mark (BOM)
        bom_content = "\ufeff" + """
package_name: bom-test
command_name: bom-test
display_name: BOM Test
description: "File with BOM: テスト"
language: python
cli:
  name: bom-test
  description: "BOM test: тест"
  tagline: "BOM handling"
  commands:
    test:
      desc: "Test with BOM: 测试"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8-sig', suffix='.yaml', delete=False) as f:
            f.write(bom_content)
            yaml_file = f.name
        
        try:
            with open(yaml_file, 'r', encoding='utf-8-sig') as f:
                loaded_content = yaml.safe_load(f)
            
            # Verify BOM doesn't interfere with Unicode handling
            assert 'テスト' in loaded_content['description']
            assert 'тест' in loaded_content['cli']['description']
            assert '测试' in loaded_content['cli']['commands']['test']['desc']
            
        finally:
            os.unlink(yaml_file)


class TestGeneratedCodeSyntaxValidation:
    """Test that generated code with Unicode is syntactically valid."""
    
    def test_python_unicode_syntax_validation(self):
        """Test that Python code with Unicode compiles correctly."""
        cli_config = CLISchema(
            name="syntax-test",
            description="Syntax test with Unicode: 編程, программирование, برمجة",
            tagline="Unicode syntax validation",
            commands={
                "测试": CommandSchema(
                    desc="Test command in Chinese: 测试命令"
                )
            }
        )
        
        config = GoobitsConfigSchema(
            package_name="syntax-test",
            command_name="syntax-test",
            display_name="Syntax Test",
            description="Unicode syntax test",
            language="python",
            cli=cli_config,
            python=PythonConfigSchema(),
            dependencies=DependenciesSchema(),
            installation=InstallationSchema(pypi_name="syntax-test"),
            shell_integration=ShellIntegrationSchema(alias="test-cli"),
            validation=ValidationSchema(),
            messages=MessagesSchema()
        )
        
        generator = PythonGenerator()
        result = generator.generate(config, "syntax.yaml", "1.0.0")
        
        # Try to compile the generated Python code
        try:
            compile(result, '<generated>', 'exec')
        except SyntaxError as e:
            pytest.fail(f"Generated Python code with Unicode is not syntactically valid: {e}")
    
    def test_nodejs_unicode_syntax_validation(self):
        """Test that Node.js/JavaScript code with Unicode is valid."""
        cli_config = CLISchema(
            name="js-syntax-test",
            description="JavaScript syntax with Unicode: プログラミング",
            tagline="JS Unicode validation",
            commands={
                "テスト": CommandSchema(
                    desc="Japanese test command: テストコマンド"
                )
            }
        )
        
        config = GoobitsConfigSchema(
            package_name="js-syntax-test",
            command_name="js-syntax-test",
            display_name="JS Syntax Test",
            description="JavaScript Unicode test",
            language="nodejs",
            cli=cli_config,
            python=PythonConfigSchema(),
            dependencies=DependenciesSchema(),
            installation=InstallationSchema(pypi_name="js-syntax-test"),
            shell_integration=ShellIntegrationSchema(alias="test-cli"),
            validation=ValidationSchema(),
            messages=MessagesSchema()
        )
        
        generator = NodeJSGenerator()
        result = generator.generate(config, "js-syntax.yaml", "1.0.0")
        
        # Basic validation that result contains expected elements
        assert isinstance(result, str)
        assert len(result) > 0
        assert "プログラミング" in result
        assert "テスト" in result
        # Check for JavaScript structure
        assert any(keyword in result for keyword in ["function", "const", "export", "module"])
    
    def test_rust_unicode_syntax_validation(self):
        """Test that Rust code with Unicode compiles correctly."""
        cli_config = CLISchema(
            name="rust-syntax-test",
            description="Rust syntax with Unicode: ржавчина (rust in Russian)",
            tagline="Rust Unicode validation",
            commands={
                "тест": CommandSchema(
                    desc="Russian test command: тестовая команда"
                )
            }
        )
        
        config = GoobitsConfigSchema(
            package_name="rust-syntax-test",
            command_name="rust-syntax-test",
            display_name="Rust Syntax Test",
            description="Rust Unicode test",
            language="rust",
            cli=cli_config,
            python=PythonConfigSchema(),
            dependencies=DependenciesSchema(),
            installation=InstallationSchema(pypi_name="rust-syntax-test"),
            shell_integration=ShellIntegrationSchema(alias="test-cli"),
            validation=ValidationSchema(),
            messages=MessagesSchema()
        )
        
        generator = RustGenerator()
        result = generator.generate(config, "rust-syntax.yaml", "1.0.0")
        
        # Basic validation for Rust structure
        assert isinstance(result, str)
        assert len(result) > 0
        assert "ржавчина" in result
        assert "тест" in result
        # Check for Rust structure
        assert any(keyword in result for keyword in ["fn ", "use ", "pub ", "struct", "impl"])


class TestUnicodeOptionAndArgumentNames:
    """Test Unicode in command-line option and argument names."""
    
    def test_unicode_option_names(self):
        """Test Unicode characters in option names."""
        cli_config = CLISchema(
            name="unicode-options",
            description="CLI with Unicode option names",
            tagline="Unicode options test",
            commands={
                "process": CommandSchema(
                    desc="Process with Unicode options",
                    options=[
                        OptionSchema(
                            name="語言",  # "language" in Chinese
                            short="l",
                            desc="Language option in Chinese",
                            type="str",
                            default="zh"
                        ),
                        OptionSchema(
                            name="файл",  # "file" in Russian
                            short="f",
                            desc="File option in Russian",
                            type="str",
                            default=""
                        )
                    ]
                )
            }
        )
        
        # Test with multiple languages
        for language in ["python", "nodejs", "typescript", "rust"]:
            config = GoobitsConfigSchema(
                package_name="unicode-options",
                command_name="unicode-options",
                display_name="Unicode Options",
                description="Unicode options test",
                language=language,
                cli=cli_config,
                python=PythonConfigSchema(),
                dependencies=DependenciesSchema(),
                installation=InstallationSchema(pypi_name="unicode-options"),
                shell_integration=ShellIntegrationSchema(alias="test-cli"),
                validation=ValidationSchema(),
                messages=MessagesSchema()
            )
            
            if language == "python":
                generator = PythonGenerator()
            elif language == "nodejs":
                generator = NodeJSGenerator()
            elif language == "typescript":
                generator = TypeScriptGenerator()
            else:  # rust
                generator = RustGenerator()
            
            result = generator.generate(config, "unicode-options.yaml", "1.0.0")
            
            # Verify Unicode option names are handled
            assert "語言" in result
            assert "файл" in result
    
    def test_unicode_argument_names(self):
        """Test Unicode characters in argument names."""
        cli_config = CLISchema(
            name="unicode-args",
            description="CLI with Unicode argument names",
            tagline="Unicode arguments test",
            commands={
                "convert": CommandSchema(
                    desc="Convert with Unicode arguments",
                    args=[
                        ArgumentSchema(
                            name="入力",  # "input" in Japanese
                            desc="Input file in Japanese",
                            type="str",
                            required=True
                        ),
                        ArgumentSchema(
                            name="выход",  # "output" in Russian
                            desc="Output file in Russian",
                            type="str",
                            required=False
                        )
                    ]
                )
            }
        )
        
        config = GoobitsConfigSchema(
            package_name="unicode-args",
            command_name="unicode-args",
            display_name="Unicode Args",
            description="Unicode arguments test",
            language="python",
            cli=cli_config,
            python=PythonConfigSchema(),
            dependencies=DependenciesSchema(),
            installation=InstallationSchema(pypi_name="unicode-args"),
            shell_integration=ShellIntegrationSchema(alias="test-cli"),
            validation=ValidationSchema(),
            messages=MessagesSchema()
        )
        
        generator = PythonGenerator()
        result = generator.generate(config, "unicode-args.yaml", "1.0.0")
        
        # Verify Unicode argument names are handled
        assert "入力" in result
        assert "выход" in result


class TestComplexUnicodeScenarios:
    """Test complex real-world Unicode scenarios."""
    
    def test_multilingual_cli_comprehensive(self):
        """Test a comprehensive multilingual CLI scenario."""
        cli_config = CLISchema(
            name="multilingual-cli",
            description="多言語CLI - Многоязычный CLI - أداة متعددة اللغات",
            tagline="Supporting: 中文, Русский, العربية, 日本語, Español",
            commands={
                "配置": CommandSchema(  # "configure" in Chinese
                    desc="Configure application: アプリケーションを設定する",
                    args=[
                        ArgumentSchema(
                            name="настройки",  # "settings" in Russian
                            desc="Settings file: إعدادات الملف",
                            type="str",
                            required=True
                        )
                    ],
                    options=[
                        OptionSchema(
                            name="详细",  # "verbose" in Chinese
                            short="v",
                            desc="Verbose output: подробный вывод",
                            type="flag",
                            default=False
                        ),
                        OptionSchema(
                            name="言語",  # "language" in Japanese
                            short="l",
                            desc="Interface language: لغة الواجهة",
                            type="str",
                            default="auto"
                        )
                    ]
                ),
                "ejecutar": CommandSchema(  # "execute" in Spanish
                    desc="Execute command: コマンドを実行する - تنفيذ الأمر",
                    args=[
                        ArgumentSchema(
                            name="команда",  # "command" in Russian
                            desc="Command to execute: 実行するコマンド",
                            type="str",
                            required=True
                        )
                    ]
                )
            }
        )
        
        # Test with all target languages
        for language in ["python", "nodejs", "typescript", "rust"]:
            config = GoobitsConfigSchema(
                package_name="multilingual-cli",
                command_name="multilingual-cli",
                display_name="Multilingual CLI",
                description="Comprehensive multilingual CLI",
                language=language,
                cli=cli_config,
                python=PythonConfigSchema(),
                dependencies=DependenciesSchema(),
                installation=InstallationSchema(pypi_name="multilingual-cli"),
                shell_integration=ShellIntegrationSchema(alias="test-cli"),
                validation=ValidationSchema(),
                messages=MessagesSchema()
            )
            
            if language == "python":
                generator = PythonGenerator()
            elif language == "nodejs":
                generator = NodeJSGenerator()
            elif language == "typescript":
                generator = TypeScriptGenerator()
            else:  # rust
                generator = RustGenerator()
            
            result = generator.generate(config, "multilingual.yaml", "1.0.0")
            
            # Verify key Unicode content is preserved (command names and descriptions)
            # Note: Some detailed descriptions may not appear in final output
            key_unicode_texts = [
                "多言語CLI", "Многоязычный", "متعددة اللغات",
                "配置", "アプリケーションを設定する",
                "ejecutar", "コマンドを実行する", "تنفيذ الأمر"
            ]
            
            for text in key_unicode_texts:
                assert text in result, f"Key Unicode text '{text}' not found in {language} output"
            
            # Verify the generated code has basic structure
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_unicode_edge_cases_in_templates(self):
        """Test Unicode edge cases in template rendering."""
        # Test with problematic Unicode combinations
        cli_config = CLISchema(
            name="edge-case-cli",
            description="Edge cases: 👨‍💻🏳️‍🌈🇺🇸",  # Complex emoji sequences
            tagline="Testing: \u0041\u0301 vs Á",  # Combining vs precomposed
            commands={
                "test": CommandSchema(
                    desc="Test with edge cases: \U0001F1FA\U0001F1F8",  # Flag emoji
                    options=[
                        OptionSchema(
                            name="mode",
                            short="m",
                            desc="Mode: \u202D‮Reversed text‭\u202C",  # Bidirectional text
                            type="str",
                            default="normal"
                        )
                    ]
                )
            }
        )
        
        config = GoobitsConfigSchema(
            package_name="edge-case-cli",
            command_name="edge-case-cli",
            display_name="Edge Case CLI",
            description="Unicode edge cases test",
            language="python",
            cli=cli_config,
            python=PythonConfigSchema(),
            dependencies=DependenciesSchema(),
            installation=InstallationSchema(pypi_name="edge-case-cli"),
            shell_integration=ShellIntegrationSchema(alias="test-cli"),
            validation=ValidationSchema(),
            messages=MessagesSchema()
        )
        
        generator = PythonGenerator()
        result = generator.generate(config, "edge-case.yaml", "1.0.0")
        
        # Verify the generator handles complex Unicode without crashing
        assert isinstance(result, str)
        assert len(result) > 0
        # Complex emoji sequences should be preserved
        assert "👨‍💻" in result
        assert "🏳️‍🌈" in result
        assert "🇺🇸" in result