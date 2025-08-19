/**
 * TypeScript decorator implementations for CLI commands and options
 * Provides clean, annotation-based command definition with comprehensive error handling
 */

import 'reflect-metadata';
import { Command } from 'commander';
import {
  CommandConfig,
  OptionConfig,
  ArgumentConfig,
  ValidationConfig,
  CommandMetadata,
  OptionMetadata,
  ArgumentMetadata,
  ValidationMetadata,
  MetadataReader,
  CommandBuilder,
  COMMAND_METADATA_KEY,
  OPTION_METADATA_KEY,
  ARGUMENT_METADATA_KEY,
  VALIDATION_METADATA_KEY,
  IsRequiredConfig,
  IsEmailConfig,
  IsUrlConfig,
  IsPathConfig,
  IsNumberConfig,
  IsStringConfig,
  IsInConfig,
} from '../types/decorators';

// Import comprehensive error handling
import type {
  CLIError,
  Result,
  ValidationError,
  SystemError,
  ErrorContext,
} from '../types/errors';
import {
  CLIErrorCode,
  ErrorSeverity,
  createValidationError,
  createSystemError,
  success,
  failure,
  asyncResult,
  syncResult,
  isSuccess,
  isFailure,
} from './errors.js';

// === Metadata Storage ===

/** Global metadata storage */
class MetadataStorage {
  private static instance: MetadataStorage;
  
  private commands = new Map<object, CommandMetadata[]>();
  private options = new Map<object, OptionMetadata[]>();
  private arguments = new Map<object, ArgumentMetadata[]>();
  private validations = new Map<object, ValidationMetadata[]>();

  static getInstance(): MetadataStorage {
    if (!MetadataStorage.instance) {
      MetadataStorage.instance = new MetadataStorage();
    }
    return MetadataStorage.instance;
  }

  addCommand(target: object, metadata: CommandMetadata): void {
    if (!this.commands.has(target)) {
      this.commands.set(target, []);
    }
    this.commands.get(target)!.push(metadata);
  }

  addOption(target: object, metadata: OptionMetadata): void {
    if (!this.options.has(target)) {
      this.options.set(target, []);
    }
    this.options.get(target)!.push(metadata);
  }

  addArgument(target: object, metadata: ArgumentMetadata): void {
    if (!this.arguments.has(target)) {
      this.arguments.set(target, []);
    }
    this.arguments.get(target)!.push(metadata);
  }

  addValidation(target: object, metadata: ValidationMetadata): void {
    if (!this.validations.has(target)) {
      this.validations.set(target, []);
    }
    this.validations.get(target)!.push(metadata);
  }

  getCommands(target: object): CommandMetadata[] {
    return this.commands.get(target) || [];
  }

  getOptions(target: object): OptionMetadata[] {
    return this.options.get(target) || [];
  }

  getArguments(target: object): ArgumentMetadata[] {
    return this.arguments.get(target) || [];
  }

  getValidations(target: object): ValidationMetadata[] {
    return this.validations.get(target) || [];
  }
}

// === Core Decorators ===

/**
 * Mark a method as a CLI command
 * @param config Command configuration
 */
export function Command(config: CommandConfig): MethodDecorator {
  return function (target: object, propertyKey: string | symbol, descriptor: PropertyDescriptor): void {
    const metadata: CommandMetadata = {
      ...config,
      propertyKey,
      target,
    };
    
    MetadataStorage.getInstance().addCommand(target, metadata);
    
    // Store metadata using reflect-metadata as well for compatibility
    Reflect.defineMetadata(COMMAND_METADATA_KEY, metadata, target, propertyKey);
  };
}

/**
 * Mark a parameter as a CLI option
 * @param config Option configuration
 */
export function Option(config: OptionConfig): ParameterDecorator {
  return function (target: object, propertyKey: string | symbol | undefined, parameterIndex: number): void {
    if (!propertyKey) return;
    
    const metadata: OptionMetadata = {
      ...config,
      propertyKey,
      parameterIndex,
      target,
    };
    
    MetadataStorage.getInstance().addOption(target, metadata);
    
    // Store in reflect-metadata
    const existingOptions = Reflect.getMetadata(OPTION_METADATA_KEY, target, propertyKey) || [];
    existingOptions.push(metadata);
    Reflect.defineMetadata(OPTION_METADATA_KEY, existingOptions, target, propertyKey);
  };
}

/**
 * Mark a parameter as a CLI argument
 * @param config Argument configuration
 */
export function Argument(config: ArgumentConfig): ParameterDecorator {
  return function (target: object, propertyKey: string | symbol | undefined, parameterIndex: number): void {
    if (!propertyKey) return;
    
    const metadata: ArgumentMetadata = {
      ...config,
      propertyKey,
      parameterIndex,
      target,
    };
    
    MetadataStorage.getInstance().addArgument(target, metadata);
    
    // Store in reflect-metadata
    const existingArgs = Reflect.getMetadata(ARGUMENT_METADATA_KEY, target, propertyKey) || [];
    existingArgs.push(metadata);
    Reflect.defineMetadata(ARGUMENT_METADATA_KEY, existingArgs, target, propertyKey);
  };
}

// === Validation Decorators ===

/**
 * Base validation decorator factory
 */
function createValidationDecorator(validatorName: string, config: ValidationConfig = {}): ParameterDecorator {
  return function (target: object, propertyKey: string | symbol | undefined, parameterIndex: number): void {
    if (!propertyKey) return;
    
    const metadata: ValidationMetadata = {
      ...config,
      propertyKey,
      parameterIndex,
      target,
      validator: validatorName,
    };
    
    MetadataStorage.getInstance().addValidation(target, metadata);
    
    // Store in reflect-metadata
    const existingValidations = Reflect.getMetadata(VALIDATION_METADATA_KEY, target, propertyKey) || [];
    existingValidations.push(metadata);
    Reflect.defineMetadata(VALIDATION_METADATA_KEY, existingValidations, target, propertyKey);
  };
}

/**
 * Validate that a parameter is required and not empty
 */
export function IsRequired(config: IsRequiredConfig = {}): ParameterDecorator {
  return createValidationDecorator('isRequired', config);
}

/**
 * Validate that a parameter is a valid email address
 */
export function IsEmail(config: IsEmailConfig = {}): ParameterDecorator {
  return createValidationDecorator('isEmail', config);
}

/**
 * Validate that a parameter is a valid URL
 */
export function IsUrl(config: IsUrlConfig = {}): ParameterDecorator {
  return createValidationDecorator('isUrl', config);
}

/**
 * Validate that a parameter is a valid file system path
 */
export function IsPath(config: IsPathConfig = {}): ParameterDecorator {
  return createValidationDecorator('isPath', config);
}

/**
 * Validate that a parameter is a valid number
 */
export function IsNumber(config: IsNumberConfig = {}): ParameterDecorator {
  return createValidationDecorator('isNumber', config);
}

/**
 * Validate that a parameter is a valid string
 */
export function IsString(config: IsStringConfig = {}): ParameterDecorator {
  return createValidationDecorator('isString', config);
}

/**
 * Validate that a parameter is one of the allowed values
 */
export function IsIn(config: IsInConfig): ParameterDecorator {
  return createValidationDecorator('isIn', config);
}

// === Validation Result Type ===

/** Detailed validation result with type-safe error information */
export interface ValidationResult {
  readonly isValid: boolean;
  readonly error?: ValidationError;
  readonly warnings?: readonly string[];
}

// === Enhanced Validation Functions ===

const validators = {
  isRequired: (value: unknown, config: IsRequiredConfig, paramName: string): ValidationResult => {
    if (value === undefined || value === null) {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' is required but was not provided`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'required',
              expectedType: 'non-null',
            },
          }
        ),
      };
    }
    
    if (typeof value === 'string' && !config.allowEmpty && value.trim() === '') {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' cannot be empty`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'non-empty',
              expectedType: 'non-empty string',
            },
          }
        ),
      };
    }
    
    return { isValid: true };
  },

  isEmail: (value: unknown, config: IsEmailConfig, paramName: string): ValidationResult => {
    if (typeof value !== 'string') {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' must be a string`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'type',
              expectedType: 'string',
            },
          }
        ),
      };
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' must be a valid email address`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'email-format',
              expectedType: 'email',
            },
          }
        ),
      };
    }
    
    if (config.domains) {
      const domain = value.split('@')[1];
      if (!config.domains.includes(domain)) {
        return {
          isValid: false,
          error: createValidationError(
            `Parameter '${paramName}' must use an allowed domain`,
            {
              parameterName: paramName,
              metadata: {
                value,
                rule: 'allowed-domains',
                allowedValues: config.domains,
              },
            }
          ),
        };
      }
    }
    
    return { isValid: true };
  },

  isUrl: (value: unknown, config: IsUrlConfig, paramName: string): ValidationResult => {
    if (typeof value !== 'string') {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' must be a string`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'type',
              expectedType: 'string',
            },
          }
        ),
      };
    }
    
    try {
      const url = new URL(value);
      if (config.protocols && !config.protocols.includes(url.protocol.slice(0, -1))) {
        return {
          isValid: false,
          error: createValidationError(
            `Parameter '${paramName}' must use an allowed protocol`,
            {
              parameterName: paramName,
              metadata: {
                value,
                rule: 'allowed-protocols',
                allowedValues: config.protocols,
              },
            }
          ),
        };
      }
      
      return { isValid: true };
    } catch (error) {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' must be a valid URL`,
          {
            parameterName: paramName,
            cause: error instanceof Error ? error : new Error(String(error)),
            metadata: {
              value,
              rule: 'url-format',
              expectedType: 'URL',
            },
          }
        ),
      };
    }
  },

  isPath: async (value: unknown, config: IsPathConfig, paramName: string): Promise<ValidationResult> => {
    if (typeof value !== 'string') {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' must be a string`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'type',
              expectedType: 'string',
            },
          }
        ),
      };
    }
    
    if (config.mustExist) {
      const { existsSync, statSync } = await import('fs');
      if (!existsSync(value)) {
        return {
          isValid: false,
          error: createValidationError(
            `Path '${value}' does not exist`,
            {
              parameterName: paramName,
              filePath: value,
              metadata: {
                value,
                rule: 'path-exists',
                operation: 'access',
              },
            }
          ),
        };
      }
      
      if (config.type) {
        try {
          const stat = statSync(value);
          if (config.type === 'file' && !stat.isFile()) {
            return {
              isValid: false,
              error: createValidationError(
                `Path '${value}' exists but is not a file`,
                {
                  parameterName: paramName,
                  filePath: value,
                  metadata: {
                    value,
                    rule: 'file-type',
                    expectedType: 'file',
                  },
                }
              ),
            };
          }
          if (config.type === 'directory' && !stat.isDirectory()) {
            return {
              isValid: false,
              error: createValidationError(
                `Path '${value}' exists but is not a directory`,
                {
                  parameterName: paramName,
                  filePath: value,
                  metadata: {
                    value,
                    rule: 'file-type',
                    expectedType: 'directory',
                  },
                }
              ),
            };
          }
        } catch (error) {
          return {
            isValid: false,
            error: createValidationError(
              `Failed to check path type for '${value}'`,
              {
                parameterName: paramName,
                filePath: value,
                cause: error instanceof Error ? error : new Error(String(error)),
                metadata: {
                  value,
                  rule: 'path-stat',
                  operation: 'stat',
                },
              }
            ),
          };
        }
      }
    }
    
    return { isValid: true };
  },

  isNumber: (value: unknown, config: IsNumberConfig, paramName: string): ValidationResult => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (typeof num !== 'number' || isNaN(num)) {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' must be a valid number`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'type',
              expectedType: 'number',
            },
          }
        ),
      };
    }
    
    if (config.integer && !Number.isInteger(num)) {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' must be an integer`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'integer',
              expectedType: 'integer',
            },
          }
        ),
      };
    }
    
    if (config.min !== undefined && num < config.min) {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' must be at least ${config.min}`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'minimum',
              min: config.min,
            },
          }
        ),
      };
    }
    
    if (config.max !== undefined && num > config.max) {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' must be at most ${config.max}`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'maximum',
              max: config.max,
            },
          }
        ),
      };
    }
    
    return { isValid: true };
  },

  isString: (value: unknown, config: IsStringConfig, paramName: string): ValidationResult => {
    if (typeof value !== 'string') {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' must be a string`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'type',
              expectedType: 'string',
            },
          }
        ),
      };
    }
    
    if (config.minLength !== undefined && value.length < config.minLength) {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' must be at least ${config.minLength} characters long`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'min-length',
              minLength: config.minLength,
            },
          }
        ),
      };
    }
    
    if (config.maxLength !== undefined && value.length > config.maxLength) {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' must be at most ${config.maxLength} characters long`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'max-length',
              maxLength: config.maxLength,
            },
          }
        ),
      };
    }
    
    if (config.pattern && !config.pattern.test(value)) {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' does not match the required pattern`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'pattern',
              pattern: config.pattern.source,
            },
          }
        ),
      };
    }
    
    return { isValid: true };
  },

  isIn: (value: unknown, config: IsInConfig, paramName: string): ValidationResult => {
    const isValidValue = (() => {
      if (config.caseSensitive === false && typeof value === 'string') {
        const lowerValues = config.values.map(v => 
          typeof v === 'string' ? v.toLowerCase() : v
        );
        return lowerValues.includes(value.toLowerCase());
      }
      
      return config.values.includes(value);
    })();
    
    if (!isValidValue) {
      return {
        isValid: false,
        error: createValidationError(
          `Parameter '${paramName}' must be one of the allowed values`,
          {
            parameterName: paramName,
            metadata: {
              value,
              rule: 'allowed-values',
              allowedValues: config.values,
            },
          }
        ),
      };
    }
    
    return { isValid: true };
  },
};

// === Metadata Reader Implementation ===

export class DefaultMetadataReader implements MetadataReader {
  getCommandMetadata(target: object): CommandMetadata[] {
    return MetadataStorage.getInstance().getCommands(target);
  }

  getOptionMetadata(target: object): OptionMetadata[] {
    return MetadataStorage.getInstance().getOptions(target);
  }

  getArgumentMetadata(target: object): ArgumentMetadata[] {
    return MetadataStorage.getInstance().getArguments(target);
  }

  getValidationMetadata(target: object): ValidationMetadata[] {
    return MetadataStorage.getInstance().getValidations(target);
  }
}

// === Command Builder Implementation ===

export class DecoratorCommandBuilder implements CommandBuilder {
  private reader: MetadataReader;

  constructor(reader: MetadataReader = new DefaultMetadataReader()) {
    this.reader = reader;
  }

  buildCommands(program: Command, instance: object): void {
    const commands = this.reader.getCommandMetadata(instance);
    
    for (const commandMeta of commands) {
      const cmd = program
        .command(commandMeta.name || String(commandMeta.propertyKey))
        .description(commandMeta.description);

      if (commandMeta.alias) {
        cmd.alias(commandMeta.alias);
      }

      if (commandMeta.isDefault) {
        cmd.isDefault(true);
      }

      if (commandMeta.hidden) {
        cmd.hideCommand();
      }

      // Add arguments
      const args = this.reader.getArgumentMetadata(instance)
        .filter(arg => arg.propertyKey === commandMeta.propertyKey)
        .sort((a, b) => a.parameterIndex - b.parameterIndex);

      for (const arg of args) {
        const argName = arg.required ? `<${arg.name}>` : `[${arg.name}]`;
        cmd.argument(argName, arg.description);
      }

      // Add options
      const options = this.reader.getOptionMetadata(instance)
        .filter(opt => opt.propertyKey === commandMeta.propertyKey);

      for (const option of options) {
        const flags = option.short 
          ? `-${option.short}, --${option.name}` 
          : `--${option.name}`;
        
        const flagsWithType = option.type === 'flag' ? flags : `${flags} <value>`;
        
        cmd.option(flagsWithType, option.description, option.default);
      }

      // Add action handler with comprehensive error handling
      cmd.action(async (...args: unknown[]) => {
        const methodKey = commandMeta.propertyKey;
        const method = (instance as any)[methodKey];
        
        if (typeof method === 'function') {
          // Validate arguments with Result pattern
          const validationResult = await this.validateArguments(instance, methodKey, args);
          
          if (isFailure(validationResult)) {
            // Handle validation errors
            console.error('Validation failed:');
            for (const error of validationResult.error) {
              console.error(`  ✗ ${error.message}`);
            }
            process.exit(2); // MISUSE_OF_SHELL_BUILTIN
          }
          
          try {
            // Call the command method
            return await method.apply(instance, args);
          } catch (error) {
            // Convert method execution error to typed error
            const systemError = createSystemError(
              `Command '${String(methodKey)}' execution failed`,
              {
                cause: error instanceof Error ? error : new Error(String(error)),
                metadata: {
                  methodName: String(methodKey),
                  className: instance.constructor.name,
                },
              }
            );
            
            console.error(`✗ ${systemError.message}`);
            if (process.env.DEBUG && systemError.stack) {
              console.error('Stack trace:', systemError.stack);
            }
            process.exit(1);
          }
        } else {
          const error = createSystemError(
            `Command method '${String(methodKey)}' is not a function`,
            {
              metadata: {
                methodName: String(methodKey),
                className: instance.constructor.name,
                actualType: typeof method,
              },
            }
          );
          
          console.error(`✗ ${error.message}`);
          process.exit(70); // SOFTWARE_ERROR
        }
      });
    }
  }

  private async validateArguments(
    instance: object, 
    methodKey: string | symbol, 
    args: unknown[]
  ): Promise<Result<void, ValidationError[]>> {
    return await asyncResult(
      async (): Promise<void> => {
        const validations = this.reader.getValidationMetadata(instance)
          .filter(val => val.propertyKey === methodKey);

        const validationErrors: ValidationError[] = [];
        const argumentMetadata = this.reader.getArgumentMetadata(instance)
          .filter(arg => arg.propertyKey === methodKey)
          .sort((a, b) => a.parameterIndex - b.parameterIndex);
        const optionMetadata = this.reader.getOptionMetadata(instance)
          .filter(opt => opt.propertyKey === methodKey);

        for (const validation of validations) {
          const value = args[validation.parameterIndex!];
          const validator = (validators as any)[validation.validator];
          
          if (validator) {
            // Get parameter name from metadata
            const paramName = (() => {
              const argMeta = argumentMetadata.find(arg => arg.parameterIndex === validation.parameterIndex);
              if (argMeta) return argMeta.name;
              
              const optMeta = optionMetadata.find(opt => opt.parameterIndex === validation.parameterIndex);
              if (optMeta) return optMeta.name;
              
              return `parameter${validation.parameterIndex}`;
            })();
            
            let result: ValidationResult;
            if (validation.validator === 'isPath') {
              result = await validator(value, validation, paramName);
            } else {
              result = validator(value, validation, paramName);
            }
            
            if (!result.isValid && result.error) {
              validationErrors.push(result.error);
            }
          }
        }
        
        if (validationErrors.length > 0) {
          throw validationErrors;
        }
      },
      (error) => {
        if (Array.isArray(error)) {
          return error as ValidationError[];
        }
        
        // Convert generic error to ValidationError
        return [createValidationError(
          error instanceof Error ? error.message : String(error),
          {
            parameterName: 'unknown',
            cause: error instanceof Error ? error : new Error(String(error)),
            metadata: {
              source: 'decorator-validation',
              methodKey: String(methodKey),
            },
          }
        )];
      }
    );
  }
}

// === Export All ===

export {
  MetadataStorage,
  DefaultMetadataReader,
  validators,
  ValidationResult,
  COMMAND_METADATA_KEY,
  OPTION_METADATA_KEY,
  ARGUMENT_METADATA_KEY,
  VALIDATION_METADATA_KEY,
};