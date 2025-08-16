/**
 * Comprehensive TypeScript type definitions for Demo TypeScript CLI
 * Auto-generated from typescript-example.yaml
 */

// === Core CLI Types ===

/** Base configuration interface for all commands */
export interface BaseConfig {
  readonly [key: string]: unknown;
}

/** Command execution context */
export interface CommandContext<T = Record<string, unknown>> {
  readonly commandName: string;
  readonly args: T;
  readonly options: Record<string, unknown>;
  readonly globalOptions: GlobalOptions;
}

/** Global CLI options */
export interface GlobalOptions {
  
  readonly [key: string]: unknown;
  
}

// === Command-specific Types ===


/** Arguments for calculate command */
export interface CalculateArgs {
  
  
  readonly operation: "add" | "subtract" | "multiply" | "divide";
  
  readonly a: any;
  
  readonly b: any;
  
  
}

/** Options for calculate command */
export interface CalculateOptions {
  
  
  readonly precision?: number;
  
  
}

/** Complete context for calculate command */
export interface CalculateContext extends CommandContext<CalculateArgs> {
  readonly options: CalculateOptions;
}




/** Arguments for status command */
export interface StatusArgs {
  
}

/** Options for status command */
export interface StatusOptions {
  
  readonly [key: string]: unknown;
  
}

/** Complete context for status command */
export interface StatusContext extends CommandContext<StatusArgs> {
  readonly options: StatusOptions;
}





// === Hook System Types ===

/** Standard command hook function signature */
export type CommandHook<TContext extends CommandContext = CommandContext> = (
  context: TContext
) => Promise<void | unknown> | void | unknown;

/** Managed command interface for lifecycle commands */
export interface ManagedCommand<TContext extends CommandContext = CommandContext> {
  execute(context: TContext): Promise<unknown>;
  start?(context: TContext): Promise<void>;
  stop?(context: TContext): Promise<void>;
  restart?(context: TContext): Promise<void>;
  status?(context: TContext): Promise<void>;
}

/** Hook registry mapping command names to their handlers */
export interface HookRegistry {
  
  
  onCalculate?: CommandHook<CalculateContext>;
  
  
  
  
  onStatus?: CommandHook<StatusContext>;
  
  
  
  [key: string]: CommandHook | ManagedCommand | unknown;
}

// === Plugin System Types ===

/** Plugin registration function */
export type PluginRegistration = (program: import('commander').Command) => void;

/** Plugin module interface */
export interface PluginModule {
  register: PluginRegistration;
  default?: PluginRegistration;
}

// === Validation Types ===

/** Validation result */
export interface ValidationResult {
  readonly isValid: boolean;
  readonly errors: string[];
  readonly warnings: string[];
}

/** Validator function signature */
export type Validator<T = unknown> = (value: T) => ValidationResult | Promise<ValidationResult>;

// === Utility Types ===

/** Extract command names from CLI configuration */
export type CommandNames = keyof typeof cli.commands;

/** Make properties optional */
export type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

/** Make properties required */
export type RequiredBy<T, K extends keyof T> = T & Required<Pick<T, K>>;

/** Deep readonly type */
export type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

/** Configuration schema type */
export type ConfigSchema = DeepReadonly<{
  
  cli: {
    name: string;
    tagline: string;
    description?: string;
    
    commands: {
      
      calculate: {
        desc: string;
        icon?: string;
        alias?: string;
        is_default?: boolean;
        lifecycle?: 'standard' | 'managed';
        
        args: Array<{
          name: string;
          type?: string;
          desc: string;
          required?: boolean;
          choices?: string[];
        }>;
        
        
        options: Array<{
          name: string;
          short?: string;
          type: string;
          desc: string;
          required?: boolean;
          default?: unknown;
          choices?: string[];
        }>;
        
        
      };
      
      status: {
        desc: string;
        icon?: string;
        alias?: string;
        is_default?: boolean;
        lifecycle?: 'standard' | 'managed';
        
        
        
      };
      
    };
  };
  
  package_name: string;
  command_name: string;
  display_name: string;
  description: string;
  version: string;
  author?: string;
  license?: string;
  repository?: string;
  bugs_url?: string;
  homepage?: string;
}>;

// === Module Declarations ===

declare module 'app_hooks' {
  const hooks: HookRegistry;
  export = hooks;
}

declare module '*/app_hooks' {
  const hooks: HookRegistry;
  export = hooks;
}

declare module '*/app_hooks.js' {
  const hooks: HookRegistry;
  export = hooks;
}

// === Global Augmentations ===

declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV?: 'development' | 'production' | 'test';
      DEBUG?: string;
      [key: string]: string | undefined;
    }
  }
}

// === Export All Types ===

export * from './decorators';
export * from './validators';
export * from './plugins';