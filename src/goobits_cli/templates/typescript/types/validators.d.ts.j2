/**
 * Validation system types for CLI command arguments and options
 */

// === Core Validation Types ===

/** Result of a validation check */
export interface ValidationResult {
  readonly isValid: boolean;
  readonly errors: readonly string[];
  readonly warnings: readonly string[];
  readonly metadata?: Record<string, unknown>;
}

/** Validation context provided to validators */
export interface ValidationContext {
  readonly value: unknown;
  readonly parameterName: string;
  readonly commandName: string;
  readonly allParameters: Record<string, unknown>;
  readonly environment: 'development' | 'production' | 'test';
}

/** Validator function signature */
export type ValidatorFunction<TConfig = Record<string, unknown>> = (
  context: ValidationContext,
  config?: TConfig
) => ValidationResult | Promise<ValidationResult>;

/** Validator factory function */
export type ValidatorFactory<TConfig = Record<string, unknown>> = (
  config: TConfig
) => ValidatorFunction<TConfig>;

// === Built-in Validator Configurations ===

/** Configuration for required field validation */
export interface RequiredValidatorConfig {
  /** Allow empty strings */
  allowEmpty?: boolean;
  /** Custom error message */
  message?: string;
  /** Skip validation in certain environments */
  skipInEnv?: ('development' | 'production' | 'test')[];
}

/** Configuration for string validation */
export interface StringValidatorConfig {
  /** Minimum length */
  minLength?: number;
  /** Maximum length */
  maxLength?: number;
  /** Regular expression pattern */
  pattern?: RegExp;
  /** Pattern description for error messages */
  patternDescription?: string;
  /** Trim whitespace before validation */
  trim?: boolean;
  /** Convert to lowercase before validation */
  toLowerCase?: boolean;
  /** Convert to uppercase before validation */
  toUpperCase?: boolean;
  /** Custom error message */
  message?: string;
}

/** Configuration for number validation */
export interface NumberValidatorConfig {
  /** Minimum value (inclusive) */
  min?: number;
  /** Maximum value (inclusive) */
  max?: number;
  /** Must be an integer */
  integer?: boolean;
  /** Must be positive */
  positive?: boolean;
  /** Must be negative */
  negative?: boolean;
  /** Allow infinity */
  allowInfinity?: boolean;
  /** Allow NaN */
  allowNaN?: boolean;
  /** Custom error message */
  message?: string;
}

/** Configuration for email validation */
export interface EmailValidatorConfig {
  /** Allowed domains */
  domains?: string[];
  /** Blocked domains */
  blockedDomains?: string[];
  /** Allow plus addressing (user+tag@domain.com) */
  allowPlusAddressing?: boolean;
  /** Require TLD */
  requireTLD?: boolean;
  /** Custom error message */
  message?: string;
}

/** Configuration for URL validation */
export interface UrlValidatorConfig {
  /** Allowed protocols */
  protocols?: string[];
  /** Require protocol */
  requireProtocol?: boolean;
  /** Require host */
  requireHost?: boolean;
  /** Allow localhost */
  allowLocalhost?: boolean;
  /** Allow IP addresses */
  allowIP?: boolean;
  /** Custom error message */
  message?: string;
}

/** Configuration for path validation */
export interface PathValidatorConfig {
  /** Path must exist */
  mustExist?: boolean;
  /** Path type */
  type?: 'file' | 'directory' | 'any';
  /** Path must be readable */
  readable?: boolean;
  /** Path must be writable */
  writable?: boolean;
  /** Path must be executable */
  executable?: boolean;
  /** Allowed extensions (for files) */
  extensions?: string[];
  /** Resolve relative paths */
  resolve?: boolean;
  /** Allow symlinks */
  allowSymlinks?: boolean;
  /** Custom error message */
  message?: string;
}

/** Configuration for choice validation */
export interface ChoiceValidatorConfig {
  /** Available choices */
  choices: readonly unknown[];
  /** Case sensitive comparison */
  caseSensitive?: boolean;
  /** Allow multiple selections */
  multiple?: boolean;
  /** Separator for multiple selections */
  separator?: string;
  /** Custom error message */
  message?: string;
}

/** Configuration for array validation */
export interface ArrayValidatorConfig {
  /** Minimum number of items */
  minItems?: number;
  /** Maximum number of items */
  maxItems?: number;
  /** Items must be unique */
  unique?: boolean;
  /** Validator for each item */
  itemValidator?: ValidatorFunction;
  /** Custom error message */
  message?: string;
}

/** Configuration for object validation */
export interface ObjectValidatorConfig {
  /** Required properties */
  required?: string[];
  /** Property validators */
  properties?: Record<string, ValidatorFunction>;
  /** Allow additional properties */
  additionalProperties?: boolean;
  /** Custom error message */
  message?: string;
}

/** Configuration for date validation */
export interface DateValidatorConfig {
  /** Minimum date */
  min?: Date | string;
  /** Maximum date */
  max?: Date | string;
  /** Date format for string parsing */
  format?: string;
  /** Must be in the future */
  future?: boolean;
  /** Must be in the past */
  past?: boolean;
  /** Custom error message */
  message?: string;
}

// === Composite Validators ===

/** Configuration for and() validator */
export interface AndValidatorConfig {
  /** Validators that must all pass */
  validators: ValidatorFunction[];
  /** Stop on first failure */
  stopOnFailure?: boolean;
  /** Custom error message */
  message?: string;
}

/** Configuration for or() validator */
export interface OrValidatorConfig {
  /** Validators where at least one must pass */
  validators: ValidatorFunction[];
  /** Custom error message */
  message?: string;
}

/** Configuration for not() validator */
export interface NotValidatorConfig {
  /** Validator that must fail */
  validator: ValidatorFunction;
  /** Custom error message */
  message?: string;
}

/** Configuration for conditional validation */
export interface ConditionalValidatorConfig {
  /** Condition function */
  condition: (context: ValidationContext) => boolean | Promise<boolean>;
  /** Validator to run if condition is true */
  then: ValidatorFunction;
  /** Validator to run if condition is false */
  otherwise?: ValidatorFunction;
  /** Custom error message */
  message?: string;
}

// === Validator Registry ===

/** Registry for custom validators */
export interface ValidatorRegistry {
  /** Register a new validator */
  register<TConfig = Record<string, unknown>>(
    name: string,
    validator: ValidatorFunction<TConfig> | ValidatorFactory<TConfig>
  ): void;

  /** Get a registered validator */
  get<TConfig = Record<string, unknown>>(name: string): ValidatorFunction<TConfig> | ValidatorFactory<TConfig> | undefined;

  /** Check if a validator is registered */
  has(name: string): boolean;

  /** List all registered validators */
  list(): string[];

  /** Unregister a validator */
  unregister(name: string): boolean;
}

// === Validation Chain Builder ===

/** Fluent interface for building validation chains */
export interface ValidationChain {
  /** Add required validation */
  required(config?: RequiredValidatorConfig): ValidationChain;

  /** Add string validation */
  string(config?: StringValidatorConfig): ValidationChain;

  /** Add number validation */
  number(config?: NumberValidatorConfig): ValidationChain;

  /** Add email validation */
  email(config?: EmailValidatorConfig): ValidationChain;

  /** Add URL validation */
  url(config?: UrlValidatorConfig): ValidationChain;

  /** Add path validation */
  path(config?: PathValidatorConfig): ValidationChain;

  /** Add choice validation */
  choice(config: ChoiceValidatorConfig): ValidationChain;

  /** Add array validation */
  array(config?: ArrayValidatorConfig): ValidationChain;

  /** Add object validation */
  object(config?: ObjectValidatorConfig): ValidationChain;

  /** Add date validation */
  date(config?: DateValidatorConfig): ValidationChain;

  /** Add custom validator */
  custom<TConfig = Record<string, unknown>>(
    validator: ValidatorFunction<TConfig>,
    config?: TConfig
  ): ValidationChain;

  /** Add custom validator by name */
  customByName<TConfig = Record<string, unknown>>(
    name: string,
    config?: TConfig
  ): ValidationChain;

  /** Combine with AND logic */
  and(...chains: ValidationChain[]): ValidationChain;

  /** Combine with OR logic */
  or(...chains: ValidationChain[]): ValidationChain;

  /** Negate the validation */
  not(): ValidationChain;

  /** Add conditional validation */
  when(
    condition: (context: ValidationContext) => boolean | Promise<boolean>,
    then: ValidationChain,
    otherwise?: ValidationChain
  ): ValidationChain;

  /** Build the final validator function */
  build(): ValidatorFunction;
}

// === Error Types ===

/** Validation error details */
export interface ValidationError extends Error {
  readonly code: string;
  readonly parameterName: string;
  readonly commandName: string;
  readonly value: unknown;
  readonly config?: Record<string, unknown>;
}

/** Multiple validation errors */
export interface ValidationErrors extends Error {
  readonly errors: readonly ValidationError[];
  readonly commandName: string;
}

// === Utility Types ===

/** Extract validator config type from validator function */
export type ValidatorConfig<T> = T extends ValidatorFunction<infer C> ? C : never;

/** Make validation properties optional */
export type OptionalValidation<T> = Omit<T, 'message'> & { message?: string };

/** Create a typed validator function */
export type TypedValidator<T, TConfig = Record<string, unknown>> = (
  context: ValidationContext & { value: T },
  config?: TConfig
) => ValidationResult | Promise<ValidationResult>;

// === Export Everything ===

export {
  ValidationResult,
  ValidationContext,
  ValidatorFunction,
  ValidatorFactory,
  ValidatorRegistry,
  ValidationChain,
  ValidationError,
  ValidationErrors,
};