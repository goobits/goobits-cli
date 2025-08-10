/**
 * Comprehensive TypeScript type definitions for Complex CLI Test Tool
 * Auto-generated from test_complex_config.yaml
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


/** Arguments for build command */
export interface BuildArgs {
  
  
  readonly target: any;
  
  readonly source?: any;
  
  
}

/** Options for build command */
export interface BuildOptions {
  
  
  readonly verbose?: boolean;
  
  readonly output_format?: "json" | "yaml" | "xml";
  
  readonly parallel_jobs?: number;
  
  readonly timeout?: number;
  
  
}

/** Complete context for build command */
export interface BuildContext extends CommandContext<BuildArgs> {
  readonly options: BuildOptions;
}




/** Arguments for deploy command */
export interface DeployArgs {
  
  
  readonly environment: "dev" | "staging" | "prod";
  
  
}

/** Options for deploy command */
export interface DeployOptions {
  
  
  readonly dry_run?: boolean;
  
  readonly config_file?: string;
  
  readonly force?: boolean;
  
  
}

/** Complete context for deploy command */
export interface DeployContext extends CommandContext<DeployArgs> {
  readonly options: DeployOptions;
}




/** Arguments for test command */
export interface TestArgs {
  
}

/** Options for test command */
export interface TestOptions {
  
  readonly [key: string]: unknown;
  
}

/** Complete context for test command */
export interface TestContext extends CommandContext<TestArgs> {
  readonly options: TestOptions;
}


// Subcommand types for test

/** Arguments for test unit subcommand */
export interface TestUnitArgs {
  
}

/** Options for test unit subcommand */
export interface TestUnitOptions {
  
  
  readonly coverage?: boolean;
  
  readonly pattern?: string;
  
  
}

/** Complete context for test unit subcommand */
export interface TestUnitContext extends CommandContext<TestUnitArgs> {
  readonly options: TestUnitOptions;
}

/** Arguments for test integration subcommand */
export interface TestIntegrationArgs {
  
  
  readonly service?: any;
  
  
}

/** Options for test integration subcommand */
export interface TestIntegrationOptions {
  
  
  readonly environment?: "test" | "staging";
  
  readonly parallel?: boolean;
  
  
}

/** Complete context for test integration subcommand */
export interface TestIntegrationContext extends CommandContext<TestIntegrationArgs> {
  readonly options: TestIntegrationOptions;
}

/** Arguments for test performance subcommand */
export interface TestPerformanceArgs {
  
}

/** Options for test performance subcommand */
export interface TestPerformanceOptions {
  
  
  readonly iterations?: number;
  
  readonly threshold?: number;
  
  
}

/** Complete context for test performance subcommand */
export interface TestPerformanceContext extends CommandContext<TestPerformanceArgs> {
  readonly options: TestPerformanceOptions;
}




/** Arguments for config command */
export interface ConfigArgs {
  
}

/** Options for config command */
export interface ConfigOptions {
  
  readonly [key: string]: unknown;
  
}

/** Complete context for config command */
export interface ConfigContext extends CommandContext<ConfigArgs> {
  readonly options: ConfigOptions;
}


// Subcommand types for config

/** Arguments for config get subcommand */
export interface ConfigGetArgs {
  
  
  readonly key: any;
  
  
}

/** Options for config get subcommand */
export interface ConfigGetOptions {
  
  readonly [key: string]: unknown;
  
}

/** Complete context for config get subcommand */
export interface ConfigGetContext extends CommandContext<ConfigGetArgs> {
  readonly options: ConfigGetOptions;
}

/** Arguments for config set subcommand */
export interface ConfigSetArgs {
  
  
  readonly key: any;
  
  readonly value: any;
  
  
}

/** Options for config set subcommand */
export interface ConfigSetOptions {
  
  
  readonly global?: boolean;
  
  
}

/** Complete context for config set subcommand */
export interface ConfigSetContext extends CommandContext<ConfigSetArgs> {
  readonly options: ConfigSetOptions;
}

/** Arguments for config list subcommand */
export interface ConfigListArgs {
  
}

/** Options for config list subcommand */
export interface ConfigListOptions {
  
  
  readonly format?: "table" | "json" | "yaml";
  
  
}

/** Complete context for config list subcommand */
export interface ConfigListContext extends CommandContext<ConfigListArgs> {
  readonly options: ConfigListOptions;
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
  
  
  
  
  onDeploy?: CommandHook<DeployContext>;
  
  
  
  
  onTest?: CommandHook<TestContext>;
  
  
  
  onTestUnit?: CommandHook<TestUnitContext>;
  
  onTestIntegration?: CommandHook<TestIntegrationContext>;
  
  onTestPerformance?: CommandHook<TestPerformanceContext>;
  
  
  
  
  onConfig?: CommandHook<ConfigContext>;
  
  
  
  onConfigGet?: CommandHook<ConfigGetContext>;
  
  onConfigSet?: CommandHook<ConfigSetContext>;
  
  onConfigList?: CommandHook<ConfigListContext>;
  
  
  
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
      
      deploy: {
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
      
      test: {
        desc: string;
        icon?: string;
        alias?: string;
        is_default?: boolean;
        lifecycle?: 'standard' | 'managed';
        
        
        
        subcommands: Record<string, unknown>;
        
      };
      
      config: {
        desc: string;
        icon?: string;
        alias?: string;
        is_default?: boolean;
        lifecycle?: 'standard' | 'managed';
        
        
        
        subcommands: Record<string, unknown>;
        
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