/**
 * Plugin system types for extensible CLI functionality
 */

import { Command } from 'commander';

// === Core Plugin Types ===

/** Plugin metadata */
export interface PluginMetadata {
  /** Plugin name */
  readonly name: string;
  /** Plugin version */
  readonly version: string;
  /** Plugin description */
  readonly description?: string;
  /** Plugin author */
  readonly author?: string;
  /** Plugin homepage */
  readonly homepage?: string;
  /** Plugin repository */
  readonly repository?: string;
  /** Plugin license */
  readonly license?: string;
  /** Plugin keywords */
  readonly keywords?: readonly string[];
  /** Minimum CLI version required */
  readonly minCliVersion?: string;
  /** Maximum CLI version supported */
  readonly maxCliVersion?: string;
  /** Plugin dependencies */
  readonly dependencies?: Record<string, string>;
}

/** Plugin initialization context */
export interface PluginContext {
  /** CLI version */
  readonly cliVersion: string;
  /** CLI name */
  readonly cliName: string;
  /** Environment */
  readonly environment: 'development' | 'production' | 'test';
  /** Plugin configuration */
  readonly config: Record<string, unknown>;
  /** Logger instance */
  readonly logger: PluginLogger;
  /** Event emitter */
  readonly events: PluginEventEmitter;
}

/** Plugin logger interface */
export interface PluginLogger {
  debug(message: string, ...args: unknown[]): void;
  info(message: string, ...args: unknown[]): void;
  warn(message: string, ...args: unknown[]): void;
  error(message: string, ...args: unknown[]): void;
}

/** Plugin event emitter */
export interface PluginEventEmitter {
  on(event: string, listener: (...args: unknown[]) => void): void;
  off(event: string, listener: (...args: unknown[]) => void): void;
  emit(event: string, ...args: unknown[]): void;
  once(event: string, listener: (...args: unknown[]) => void): void;
}

// === Plugin Interface ===

/** Base plugin interface */
export interface Plugin {
  /** Plugin metadata */
  readonly metadata: PluginMetadata;

  /** Initialize the plugin */
  initialize?(context: PluginContext): Promise<void> | void;

  /** Register commands with the CLI */
  register?(program: Command, context: PluginContext): Promise<void> | void;

  /** Cleanup when plugin is unloaded */
  cleanup?(): Promise<void> | void;
}

/** Plugin with lifecycle hooks */
export interface LifecyclePlugin extends Plugin {
  /** Called before command execution */
  beforeCommand?(commandName: string, args: unknown[], context: PluginContext): Promise<void> | void;

  /** Called after command execution */
  afterCommand?(commandName: string, result: unknown, context: PluginContext): Promise<void> | void;

  /** Called when command fails */
  onCommandError?(commandName: string, error: Error, context: PluginContext): Promise<void> | void;
}

/** Plugin with configuration validation */
export interface ConfigurablePlugin extends Plugin {
  /** Validate plugin configuration */
  validateConfig?(config: Record<string, unknown>): Promise<ValidationResult> | ValidationResult;

  /** Get default configuration */
  getDefaultConfig?(): Record<string, unknown>;

  /** Get configuration schema */
  getConfigSchema?(): Record<string, unknown>;
}

// === Plugin Manager ===

/** Plugin loading options */
export interface PluginLoadOptions {
  /** Plugin configuration */
  config?: Record<string, unknown>;
  /** Enable plugin */
  enabled?: boolean;
  /** Plugin priority (higher = loaded first) */
  priority?: number;
  /** Plugin environment restrictions */
  environments?: ('development' | 'production' | 'test')[];
}

/** Plugin information */
export interface PluginInfo {
  /** Plugin instance */
  readonly plugin: Plugin;
  /** Plugin options */
  readonly options: PluginLoadOptions;
  /** Load timestamp */
  readonly loadedAt: Date;
  /** Initialization status */
  readonly initialized: boolean;
  /** Plugin errors */
  readonly errors: readonly Error[];
}

/** Plugin manager interface */
export interface PluginManager {
  /** Load a plugin from a module path */
  loadPlugin(modulePath: string, options?: PluginLoadOptions): Promise<void>;

  /** Load a plugin instance */
  addPlugin(plugin: Plugin, options?: PluginLoadOptions): Promise<void>;

  /** Unload a plugin */
  unloadPlugin(pluginName: string): Promise<void>;

  /** Get plugin information */
  getPlugin(pluginName: string): PluginInfo | undefined;

  /** List all loaded plugins */
  listPlugins(): readonly PluginInfo[];

  /** Enable a plugin */
  enablePlugin(pluginName: string): Promise<void>;

  /** Disable a plugin */
  disablePlugin(pluginName: string): Promise<void>;

  /** Initialize all plugins */
  initializePlugins(context: PluginContext): Promise<void>;

  /** Register all plugin commands */
  registerPluginCommands(program: Command, context: PluginContext): Promise<void>;

  /** Execute lifecycle hooks */
  executeHook(
    hookName: 'beforeCommand' | 'afterCommand' | 'onCommandError',
    ...args: unknown[]
  ): Promise<void>;

  /** Cleanup all plugins */
  cleanup(): Promise<void>;
}

// === Plugin Discovery ===

/** Plugin discovery source */
export interface PluginSource {
  /** Source name */
  readonly name: string;
  /** Source description */
  readonly description?: string;
  /** Discover available plugins */
  discover(): Promise<PluginDescriptor[]>;
}

/** Plugin descriptor from discovery */
export interface PluginDescriptor {
  /** Plugin name */
  readonly name: string;
  /** Plugin version */
  readonly version: string;
  /** Plugin location (path, URL, etc.) */
  readonly location: string;
  /** Plugin source */
  readonly source: string;
  /** Plugin metadata */
  readonly metadata?: Partial<PluginMetadata>;
}

/** File system plugin source */
export interface FileSystemPluginSource extends PluginSource {
  /** Directory to search */
  readonly directory: string;
  /** File patterns to match */
  readonly patterns?: readonly string[];
  /** Recursive search */
  readonly recursive?: boolean;
}

/** NPM plugin source */
export interface NpmPluginSource extends PluginSource {
  /** Package name prefix */
  readonly prefix: string;
  /** NPM registry URL */
  readonly registry?: string;
  /** Search keywords */
  readonly keywords?: readonly string[];
}

/** URL plugin source */
export interface UrlPluginSource extends PluginSource {
  /** Base URL */
  readonly baseUrl: string;
  /** Plugin manifest URL */
  readonly manifestUrl?: string;
}

// === Plugin Configuration ===

/** Plugin configuration schema */
export interface PluginConfigSchema {
  /** Schema type */
  readonly type: 'object';
  /** Schema properties */
  readonly properties: Record<string, PluginConfigProperty>;
  /** Required properties */
  readonly required?: readonly string[];
  /** Additional properties allowed */
  readonly additionalProperties?: boolean;
}

/** Plugin configuration property */
export interface PluginConfigProperty {
  /** Property type */
  readonly type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  /** Property description */
  readonly description?: string;
  /** Default value */
  readonly default?: unknown;
  /** Possible values */
  readonly enum?: readonly unknown[];
  /** Minimum value (for numbers) */
  readonly minimum?: number;
  /** Maximum value (for numbers) */
  readonly maximum?: number;
  /** Minimum length (for strings/arrays) */
  readonly minLength?: number;
  /** Maximum length (for strings/arrays) */
  readonly maxLength?: number;
  /** Pattern (for strings) */
  readonly pattern?: string;
  /** Items schema (for arrays) */
  readonly items?: PluginConfigProperty;
  /** Properties schema (for objects) */
  readonly properties?: Record<string, PluginConfigProperty>;
}

// === Plugin Events ===

/** Plugin event types */
export type PluginEventType =
  | 'plugin:loaded'
  | 'plugin:unloaded'
  | 'plugin:enabled'
  | 'plugin:disabled'
  | 'plugin:error'
  | 'plugin:initialized'
  | 'command:before'
  | 'command:after'
  | 'command:error';

/** Plugin event data */
export interface PluginEvent {
  /** Event type */
  readonly type: PluginEventType;
  /** Plugin name */
  readonly pluginName: string;
  /** Event timestamp */
  readonly timestamp: Date;
  /** Event data */
  readonly data?: unknown;
  /** Error (for error events) */
  readonly error?: Error;
}

// === Plugin Utilities ===

/** Plugin validation result */
export interface PluginValidationResult {
  /** Validation passed */
  readonly valid: boolean;
  /** Validation errors */
  readonly errors: readonly string[];
  /** Validation warnings */
  readonly warnings: readonly string[];
}

/** Plugin dependency info */
export interface PluginDependency {
  /** Dependency name */
  readonly name: string;
  /** Version range */
  readonly version: string;
  /** Dependency type */
  readonly type: 'plugin' | 'npm' | 'system';
  /** Optional dependency */
  readonly optional?: boolean;
}

/** Plugin compatibility check */
export interface PluginCompatibility {
  /** Compatible with current CLI version */
  readonly compatible: boolean;
  /** Compatibility issues */
  readonly issues: readonly string[];
  /** Compatibility warnings */
  readonly warnings: readonly string[];
}

// === Built-in Plugin Types ===

/** Command plugin - adds new commands */
export interface CommandPlugin extends Plugin {
  /** Commands provided by this plugin */
  readonly commands: readonly string[];
}

/** Middleware plugin - intercepts command execution */
export interface MiddlewarePlugin extends LifecyclePlugin {
  /** Middleware priority (higher = runs first) */
  readonly priority?: number;
}

/** Configuration plugin - modifies CLI configuration */
export interface ConfigurationPlugin extends Plugin {
  /** Modify CLI configuration */
  modifyConfig?(config: Record<string, unknown>): Promise<Record<string, unknown>> | Record<string, unknown>;
}

/** Theme plugin - customizes CLI appearance */
export interface ThemePlugin extends Plugin {
  /** Theme name */
  readonly themeName: string;
  /** Apply theme */
  applyTheme?(context: PluginContext): Promise<void> | void;
}

// === Export Everything ===

export {
  Plugin,
  LifecyclePlugin,
  ConfigurablePlugin,
  PluginManager,
  PluginSource,
  PluginDescriptor,
  PluginValidationResult,
  PluginCompatibility,
  CommandPlugin,
  MiddlewarePlugin,
  ConfigurationPlugin,
  ThemePlugin,
};