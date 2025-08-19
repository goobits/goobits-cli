/**
 * TypeScript decorator definitions for CLI commands and options
 * Provides a clean, annotation-based approach to command definition
 */

// === Decorator Metadata Keys ===

export const COMMAND_METADATA_KEY = Symbol('command');
export const OPTION_METADATA_KEY = Symbol('option');
export const ARGUMENT_METADATA_KEY = Symbol('argument');
export const VALIDATION_METADATA_KEY = Symbol('validation');

// === Command Decorator Types ===

/** Configuration for @Command decorator */
export interface CommandConfig {
  /** Command name (defaults to method name) */
  name?: string;
  /** Command description */
  description: string;
  /** Command alias */
  alias?: string;
  /** Command icon for help display */
  icon?: string;
  /** Whether this command is the default */
  isDefault?: boolean;
  /** Command lifecycle type */
  lifecycle?: 'standard' | 'managed';
  /** Hide command from help */
  hidden?: boolean;
}

/** Configuration for @Option decorator */
export interface OptionConfig {
  /** Option name (e.g., 'verbose' for --verbose) */
  name?: string;
  /** Short flag (e.g., 'v' for -v) */
  short?: string;
  /** Option description */
  description: string;
  /** Option type */
  type?: 'string' | 'number' | 'boolean' | 'flag';
  /** Default value */
  default?: unknown;
  /** Required option */
  required?: boolean;
  /** Allowed choices */
  choices?: string[];
  /** Environment variable to read from */
  env?: string;
}

/** Configuration for @Argument decorator */
export interface ArgumentConfig {
  /** Argument name (defaults to parameter name) */
  name?: string;
  /** Argument description */
  description: string;
  /** Argument type */
  type?: 'string' | 'number' | 'boolean';
  /** Required argument */
  required?: boolean;
  /** Allowed choices */
  choices?: string[];
  /** Variadic argument (accepts multiple values) */
  variadic?: boolean;
}

/** Configuration for validation decorators */
export interface ValidationConfig {
  /** Custom error message */
  message?: string;
  /** Skip validation in certain environments */
  skipInEnv?: string[];
}

// === Metadata Storage Types ===

/** Stored command metadata */
export interface CommandMetadata extends CommandConfig {
  propertyKey: string | symbol;
  target: object;
}

/** Stored option metadata */
export interface OptionMetadata extends OptionConfig {
  propertyKey: string | symbol;
  parameterIndex: number;
  target: object;
}

/** Stored argument metadata */
export interface ArgumentMetadata extends ArgumentConfig {
  propertyKey: string | symbol;
  parameterIndex: number;
  target: object;
}

/** Stored validation metadata */
export interface ValidationMetadata extends ValidationConfig {
  propertyKey: string | symbol;
  parameterIndex?: number;
  target: object;
  validator: string; // Name of the validation function
}

// === Decorator Function Types ===

/** Command decorator */
export type CommandDecorator = (config: CommandConfig) => MethodDecorator;

/** Option decorator */
export type OptionDecorator = (config: OptionConfig) => ParameterDecorator;

/** Argument decorator */
export type ArgumentDecorator = (config: ArgumentConfig) => ParameterDecorator;

/** Validation decorator factory */
export type ValidationDecorator = (config?: ValidationConfig) => ParameterDecorator;

// === Built-in Validation Decorators ===

/** @IsRequired validation config */
export interface IsRequiredConfig extends ValidationConfig {
  allowEmpty?: boolean;
}

/** @IsEmail validation config */
export interface IsEmailConfig extends ValidationConfig {
  domains?: string[];
}

/** @IsUrl validation config */
export interface IsUrlConfig extends ValidationConfig {
  protocols?: string[];
}

/** @IsPath validation config */
export interface IsPathConfig extends ValidationConfig {
  mustExist?: boolean;
  type?: 'file' | 'directory' | 'any';
}

/** @IsNumber validation config */
export interface IsNumberConfig extends ValidationConfig {
  min?: number;
  max?: number;
  integer?: boolean;
}

/** @IsString validation config */
export interface IsStringConfig extends ValidationConfig {
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
}

/** @IsIn validation config */
export interface IsInConfig extends ValidationConfig {
  values: unknown[];
  caseSensitive?: boolean;
}

// === Metadata Reflection Utilities ===

/** Get command metadata from a class */
export interface MetadataReader {
  getCommandMetadata(target: object): CommandMetadata[];
  getOptionMetadata(target: object): OptionMetadata[];
  getArgumentMetadata(target: object): ArgumentMetadata[];
  getValidationMetadata(target: object): ValidationMetadata[];
}

// === Command Builder Interface ===

/** Interface for classes that can be converted to Commander.js commands */
export interface CommandBuilder {
  /** Build and register commands with Commander.js program */
  buildCommands(program: import('commander').Command): void;
}

// === Export Types ===

export {
  CommandConfig,
  OptionConfig,
  ArgumentConfig,
  ValidationConfig,
  CommandMetadata,
  OptionMetadata,
  ArgumentMetadata,
  ValidationMetadata,
  CommandDecorator,
  OptionDecorator,
  ArgumentDecorator,
  ValidationDecorator,
  MetadataReader,
  CommandBuilder,
};