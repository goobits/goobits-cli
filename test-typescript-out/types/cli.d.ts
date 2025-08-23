/**
 * Comprehensive TypeScript type definitions for Test TypeScript CLI
 * Auto-generated from test-typescript.yaml
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

/** Arguments for hello command */
export interface HelloArgs {
}

/** Options for hello command */
export interface HelloOptions {
  readonly [key: string]: unknown;
}

/** Complete context for hello command */
export interface HelloContext extends CommandContext<HelloArgs> {
  readonly options: HelloOptions;
}


/** Arguments for build command */
export interface BuildArgs {
}

/** Options for build command */
export interface BuildOptions {
  readonly [key: string]: unknown;
}

/** Complete context for build command */
export interface BuildContext extends CommandContext<BuildArgs> {
  readonly options: BuildOptions;
}

// Subcommand types for build
/** Arguments for build project subcommand */
export interface BuildProjectArgs {
}

/** Options for build project subcommand */
export interface BuildProjectOptions {
  readonly [key: string]: unknown;
}

/** Complete context for build project subcommand */
export interface BuildProjectContext extends CommandContext<BuildProjectArgs> {
  readonly options: BuildProjectOptions;
}

/** Arguments for serve command */
export interface ServeArgs {
}

/** Options for serve command */
export interface ServeOptions {
  readonly [key: string]: unknown;
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
  onHello?: CommandHook<HelloContext>;
  onBuild?: CommandHook<BuildContext>;
  onBuildProject?: CommandHook<BuildProjectContext>;
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
    commands: {
      hello: {
        desc: string;
        icon?: string;
        alias?: string;
        is_default?: boolean;
        lifecycle?: 'standard' | 'managed';
      };
      build: {
        desc: string;
        icon?: string;
        alias?: string;
        is_default?: boolean;
        lifecycle?: 'standard' | 'managed';
        subcommands: Record<string, unknown>;
      };
      serve: {
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

export * from './decorators.js';
export * from './validators.js';
export * from './plugins.js';