/**
 * Comprehensive TypeScript type definitions for Goobits CLI Framework
 * Auto-generated from goobits.yaml
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
  
  
  readonly verbose?: boolean;
  
  
}

// === Command-specific Types ===


/** Arguments for build command */
export interface BuildArgs {
  
  
  readonly config_path?: any;
  
  
}

/** Options for build command */
export interface BuildOptions {
  
  
  readonly output_dir?: string;
  
  readonly output?: string;
  
  readonly backup?: boolean;
  
  readonly universal_templates?: boolean;
  
  
}

/** Complete context for build command */
export interface BuildContext extends CommandContext<BuildArgs> {
  readonly options: BuildOptions;
}




/** Arguments for init command */
export interface InitArgs {
  
  
  readonly project_name?: any;
  
  
}

/** Options for init command */
export interface InitOptions {
  
  
  readonly template?: "basic" | "advanced" | "api-client" | "text-processor";
  
  readonly force?: boolean;
  
  
}

/** Complete context for init command */
export interface InitContext extends CommandContext<InitArgs> {
  readonly options: InitOptions;
}




/** Arguments for serve command */
export interface ServeArgs {
  
  
  readonly directory: any;
  
  
}

/** Options for serve command */
export interface ServeOptions {
  
  
  readonly host?: string;
  
  readonly port?: number;
  
  
}

/** Complete context for serve command */
export interface ServeContext extends CommandContext<ServeArgs> {
  readonly options: ServeOptions;
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
  
  
  onBuild?: CommandHook<BuildContext>;
  
  
  
  
  onInit?: CommandHook<InitContext>;
  
  
  
  
  onServe?: CommandHook<ServeContext>;
  
  
  
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
    
    options: Array<{
      name: string;
      short?: string;
      type: string;
      desc: string;
      required?: boolean;
      default?: unknown;
      choices?: string[];
    }>;
    
    commands: {
      
      build: {
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
      
      init: {
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
      
      serve: {
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