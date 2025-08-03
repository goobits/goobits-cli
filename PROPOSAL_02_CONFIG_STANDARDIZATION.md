# Configuration Standardization Proposal for Goobits Ecosystem

> **📋 Status: PROPOSED - Not yet implemented**  
> This proposal is under consideration and has not been implemented.

**Date**: 2025-01-31  
**Author**: Configuration Standardization Team  
**Status**: Proposed  
**Target Release**: goobits-cli v2.0.0  

## Executive Summary

This proposal outlines a comprehensive plan to standardize configuration management across all goobits-based projects (STT, TTT, TTS, Matilda, and future projects). The goal is to provide a consistent, user-friendly configuration experience while reducing code duplication and maintenance overhead.

## Current State Analysis

### Problem Statement

Currently, each goobits project implements its own configuration system:

| Project | Format | Location Strategy | API Key Management | Config Commands | Setup Wizard |
|---------|--------|-------------------|-------------------|-----------------|--------------|
| STT | JSON | Single file | JWT/auth tokens | None | No |
| TTT | YAML | Multi-location | Config + env vars | get/set/list | No |
| TTS | TOML/JSON | Dual system | Dedicated functions | show/get/set/edit | No |
| Matilda | JSONC | Multi-location | Auto-generated | config (launches wizard) | Yes |

This fragmentation creates several issues:
1. **User Confusion**: Different commands and formats across tools
2. **Maintenance Burden**: Duplicate code for similar functionality
3. **Inconsistent Experience**: Users must learn different systems
4. **Limited Reusability**: Each project reimplements common features

## Proposed Solution

### 1. Extend goobits.yaml with `app_config` Section

Add a new `app_config` section to goobits.yaml that defines the application's configuration schema:

```yaml
app_config:
  # Configuration file format (always YAML for consistency)
  format: "yaml"
  
  # Configuration file locations (in priority order)
  locations:
    - "~/.config/{command_name}/config.yaml"  # User config
    - "./.{command_name}.yaml"                # Project override
    - "${COMMAND_NAME_UPPER}_CONFIG"          # Env var override
  
  # Auto-generate default config if missing
  auto_generate: true
  
  # Configuration schema definition
  schema:
    # Define your configuration structure here
    api_keys:
      type: "object"
      sensitive: true  # Hide in config show
      properties:
        openai:
          type: "string"
          env_var: "OPENAI_API_KEY"
          validation: "regex:^sk-[a-zA-Z0-9]{32,}$"
          setup_prompt: "Enter your OpenAI API key"
```

### 2. Standardized Configuration Commands

All goobits projects will automatically get these configuration commands:

```bash
# View configuration
{command} config show                    # Show config (secrets hidden)
{command} config show --show-secrets     # Show with secrets visible

# Get/Set values with dot notation
{command} config get api_keys.openai
{command} config set logging.level debug
{command} config set models.default "gpt-4"

# Interactive setup
{command} setup                          # Launch setup wizard

# Advanced features
{command} config edit                    # Open in $EDITOR
{command} config reset                   # Reset to defaults
{command} config reset api_keys          # Reset specific section
{command} config validate                # Validate against schema
{command} config migrate                 # Migrate from old format
```

### 3. Shared Configuration Infrastructure

Create reusable components in goobits-cli:

#### A. Configuration Manager Class

```python
# goobits_cli/config/manager.py
class GoobitsConfigManager:
    """Unified configuration management for all goobits projects"""
    
    def __init__(self, schema: dict, command_name: str):
        self.schema = schema
        self.command_name = command_name
        self.config_paths = self._resolve_paths()
        self._config_cache = None
    
    def load(self) -> dict:
        """Load configuration with fallbacks and env overrides"""
    
    def save(self, config: dict):
        """Save configuration with validation"""
    
    def get(self, key: str, default=None):
        """Get value with dot notation support"""
    
    def set(self, key: str, value: Any):
        """Set value with schema validation"""
    
    def reset(self, key: Optional[str] = None):
        """Reset to defaults"""
    
    def validate(self) -> List[str]:
        """Validate current config against schema"""
```

#### B. Interactive Setup Wizard Generator

```python
# goobits_cli/config/setup_wizard.py
class SetupWizardGenerator:
    """Generate interactive setup based on schema"""
    
    def generate_wizard(self, schema: dict) -> Callable:
        """Create a setup function from schema definition"""
        
    def create_prompts(self, schema: dict) -> List[Question]:
        """Convert schema to questionary prompts"""
```

#### C. Configuration CLI Generator

```python
# goobits_cli/config/cli_generator.py
def generate_config_commands(schema: dict) -> click.Group:
    """Generate config subcommands from schema"""
    
    @click.group()
    def config():
        """Manage configuration"""
        pass
    
    # Auto-generate commands based on schema
    config.add_command(generate_show_command(schema))
    config.add_command(generate_get_command(schema))
    config.add_command(generate_set_command(schema))
    # ... etc
    
    return config
```

### 4. Schema Definition Features

The schema supports rich field definitions. The schema is designed to be extensible - each project can add its own specific configuration sections while benefiting from the shared infrastructure:

```yaml
schema:
  # Simple field
  backend:
    type: "string"
    default: "cloud"
    choices: ["cloud", "local", "ollama"]
    description: "Compute backend to use"
    setup_prompt: "Which backend should be the default?"
  
  # Nested object
  models:
    type: "object"
    properties:
      default:
        type: "string"
        default: "whisper-1"
        validation: "exists_in:available_models"
      aliases:
        type: "object"
        additional_properties: true
  
  # Sensitive data
  api_keys:
    type: "object"
    sensitive: true  # Hide in config show
    properties:
      openai:
        type: "string"
        env_var: "OPENAI_API_KEY"
        validation: "custom:validate_openai_key"
  
  # Auto-generated values
  auth_token:
    type: "string"
    sensitive: true
    auto_generate: true  # Generate UUID on first run
  
  # Dynamic choices
  audio_device:
    type: "string"
    setup_prompt: "Select audio input device"
    setup_choices_command: "list_audio_devices"  # Call function for choices
```

### 5. Migration Strategy

#### Phase 1: Infrastructure (goobits-cli v2.0.0)
1. Add `app_config` to goobits schema
2. Implement `GoobitsConfigManager` class
3. Create config command generators
4. Update CLI template to include config commands

#### Phase 2: Project Migration (2-4 weeks per project)
1. **STT**: Migrate from JSON to YAML
   - Create migration script for existing configs
   - Update code to use `GoobitsConfigManager`
   - Remove custom config handling

2. **TTT**: Enhance existing YAML system
   - Minimal changes needed (already YAML)
   - Replace custom `ConfigManager` with shared one
   - Add setup wizard

3. **TTS**: Migrate from TOML/JSON dual system
   - Merge TOML and JSON configs into single YAML
   - Migration script for user configs
   - Leverage existing validation logic

4. **Matilda**: Migrate from JSONC
   - Convert JSONC to YAML
   - Preserve existing setup wizard UX
   - Maintain auto-generation features

#### Phase 3: Documentation & Polish
1. Update all project READMEs
2. Create migration guides
3. Add config management tutorial
4. Implement config import/export features

## Benefits

### For Users
1. **Consistency**: Same commands work across all tools
2. **Discoverability**: `{command} config --help` shows all options
3. **Safety**: Validation prevents configuration errors
4. **Flexibility**: Environment variables, project overrides supported
5. **Migration**: Automatic migration from old formats

### For Developers
1. **DRY Principle**: Configuration logic defined once
2. **Maintainability**: Updates to config system benefit all projects
3. **Type Safety**: Schema validation catches errors early
4. **Extensibility**: Easy to add new configuration options
5. **Testing**: Shared config infrastructure can be thoroughly tested

## Implementation Timeline

| Week | Tasks |
|------|-------|
| 1-2 | Update goobits-cli schema and implement ConfigManager |
| 3-4 | Create config CLI generators and setup wizard |
| 5-6 | Update CLI template and test with sample project |
| 7-8 | Migrate STT project |
| 9-10 | Migrate TTT and TTS projects |
| 11-12 | Migrate Matilda project |
| 13-14 | Documentation and polish |

## Example: STT with New System

Here's how STT's goobits.yaml would look:

```yaml
# Existing sections...
package_name: "goobits-stt"
command_name: "stt"

# New app_config section
app_config:
  format: "yaml"
  auto_generate: true
  locations:
    - "~/.config/stt/config.yaml"
    - "./.stt.yaml"
    - "${STT_CONFIG}"
  
  schema:
    api_keys:
      type: "object"
      sensitive: true
      properties:
        openai:
          type: "string"
          env_var: "OPENAI_API_KEY"
          setup_prompt: "Enter OpenAI API key for cloud transcription"
    
    whisper:
      type: "object"
      properties:
        model:
          type: "string"
          default: "base"
          choices: ["tiny", "base", "small", "medium", "large"]
          setup_prompt: "Select Whisper model size"
        language:
          type: "string"
          default: "en"
          description: "Language code for transcription"
    
    audio:
      type: "object"
      properties:
        device:
          type: "string"
          default: "default"
          setup_prompt: "Select audio input device"
          setup_choices_command: "get_audio_devices"
        sample_rate:
          type: "integer"
          default: 16000
          validation: "in:[8000,16000,44100,48000]"
```

This automatically provides:

```bash
$ stt setup
🎤 Welcome to STT Setup!

This wizard will help you configure STT for first use.
Press Enter to continue...

[Step 1/3] API Keys
? Enter OpenAI API key for cloud transcription: ********

[Step 2/3] Whisper Configuration  
? Select Whisper model size: (Use arrow keys)
  ○ tiny (39M, fastest)
❯ ● base (74M, balanced)
  ○ small (244M, good quality)
  ○ medium (769M, better quality)
  ○ large (1550M, best quality)

[Step 3/3] Audio Settings
? Select audio input device:
❯ ● Default - Built-in Microphone
  ○ USB Audio Device
  ○ Bluetooth Headset

✅ Configuration saved to ~/.config/stt/config.yaml

You're all set! Try: stt listen
```

## Backwards Compatibility

1. **Grace Period**: Old config files continue to work for 6 months
2. **Auto-Migration**: First run detects old format and offers migration
3. **Environment Variables**: Existing env vars continue to work
4. **Command Aliases**: Old commands map to new ones with deprecation warnings
5. **Format Detection**: Automatically detect JSON/TOML/JSONC and convert to YAML
6. **Location Preservation**: Check existing config locations before new ones

## Future Enhancements

1. **Config Profiles**: Switch between multiple configurations
2. **Config Sync**: Share configs across machines (opt-in)
3. **Schema Versioning**: Handle schema evolution gracefully
4. **Plugin System**: Allow projects to extend base schema
5. **Web UI**: Optional web-based configuration interface

## Security Considerations

1. **Sensitive Data**: Fields marked `sensitive: true` are automatically:
   - Hidden in `config show` unless `--show-secrets` is used
   - Excluded from logs and error messages
   - Stored with restricted file permissions (0600)

2. **Validation**: All inputs are validated against the schema to prevent:
   - Code injection through config values
   - Invalid data types that could cause runtime errors
   - Out-of-range values for numeric fields

3. **Environment Variables**: Secure handling of env var overrides:
   - Only specified env vars are loaded (no arbitrary env access)
   - Validation applied to env var values
   - Clear precedence rules (env vars override file config)

## Conclusion

This standardization will significantly improve the user experience across the goobits ecosystem while reducing maintenance burden. The phased approach ensures smooth migration with minimal disruption to existing users.

## Approval

- [ ] Technical Lead
- [ ] Project Maintainers (STT, TTT, TTS, Matilda)
- [ ] Documentation Team
- [ ] QA Team

## References

- [Current goobits.yaml Schema](../src/goobits_cli/schemas.py)
- [TTT ConfigManager Implementation](../../ttt/src/ttt/config/manager.py)
- [Matilda Config Loader](../../matilda/src/core/config.py)
- [Rich-Click Documentation](https://github.com/ewels/rich-click)
- [Questionary Documentation](https://github.com/tmbo/questionary)