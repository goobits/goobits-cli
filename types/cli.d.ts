/**
 * Comprehensive TypeScript type definitions for NodeJSTestCLI
 * Auto-generated from test_typescript_2level.yaml
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
  readonly config?: string;
}

// === Command-specific Types ===

/** Arguments for init command */
export interface InitArgs {
  readonly name: any;
}

/** Options for init command */
export interface InitOptions {
  readonly template?: string;
  readonly skip_install?: boolean;
}

/** Complete context for init command */
export interface InitContext extends CommandContext<InitArgs> {
  readonly options: InitOptions;
}


/** Arguments for deploy command */
export interface DeployArgs {
  readonly environment: any;
}

/** Options for deploy command */
export interface DeployOptions {
  readonly force?: boolean;
  readonly dry_run?: boolean;
}

/** Complete context for deploy command */
export interface DeployContext extends CommandContext<DeployArgs> {
  readonly options: DeployOptions;
}


/** Arguments for server command */
export interface ServerArgs {
}

/** Options for server command */
export interface ServerOptions {
  readonly [key: string]: unknown;
}

/** Complete context for server command */
export interface ServerContext extends CommandContext<ServerArgs> {
  readonly options: ServerOptions;
}

// Subcommand types for server
/** Arguments for server start subcommand */
export interface ServerStartArgs {
}

/** Options for server start subcommand */
export interface ServerStartOptions {
  readonly port?: number;
  readonly daemon?: boolean;
}

/** Complete context for server start subcommand */
export interface ServerStartContext extends CommandContext<ServerStartArgs> {
  readonly options: ServerStartOptions;
}
/** Arguments for server stop subcommand */
export interface ServerStopArgs {
}

/** Options for server stop subcommand */
export interface ServerStopOptions {
  readonly graceful?: boolean;
}

/** Complete context for server stop subcommand */
export interface ServerStopContext extends CommandContext<ServerStopArgs> {
  readonly options: ServerStopOptions;
}
/** Arguments for server restart subcommand */
export interface ServerRestartArgs {
  readonly service?: any;
}

/** Options for server restart subcommand */
export interface ServerRestartOptions {
  readonly [key: string]: unknown;
}

/** Complete context for server restart subcommand */
export interface ServerRestartContext extends CommandContext<ServerRestartArgs> {
  readonly options: ServerRestartOptions;
}

/** Arguments for database command */
export interface DatabaseArgs {
}

/** Options for database command */
export interface DatabaseOptions {
  readonly [key: string]: unknown;
}

/** Complete context for database command */
export interface DatabaseContext extends CommandContext<DatabaseArgs> {
  readonly options: DatabaseOptions;
}

// Subcommand types for database
/** Arguments for database migrate subcommand */
export interface DatabaseMigrateArgs {
}

/** Options for database migrate subcommand */
export interface DatabaseMigrateOptions {
  readonly direction?: string;
  readonly steps?: number;
}

/** Complete context for database migrate subcommand */
export interface DatabaseMigrateContext extends CommandContext<DatabaseMigrateArgs> {
  readonly options: DatabaseMigrateOptions;
}
/** Arguments for database seed subcommand */
export interface DatabaseSeedArgs {
  readonly dataset?: any;
}

/** Options for database seed subcommand */
export interface DatabaseSeedOptions {
  readonly truncate?: boolean;
}

/** Complete context for database seed subcommand */
export interface DatabaseSeedContext extends CommandContext<DatabaseSeedArgs> {
  readonly options: DatabaseSeedOptions;
}
/** Arguments for database backup subcommand */
export interface DatabaseBackupArgs {
}

/** Options for database backup subcommand */
export interface DatabaseBackupOptions {
  readonly output?: string;
  readonly compress?: boolean;
}

/** Complete context for database backup subcommand */
export interface DatabaseBackupContext extends CommandContext<DatabaseBackupArgs> {
  readonly options: DatabaseBackupOptions;
}

/** Arguments for test command */
export interface TestArgs {
  readonly pattern?: any;
}

/** Options for test command */
export interface TestOptions {
  readonly coverage?: boolean;
  readonly watch?: boolean;
  readonly bail?: boolean;
}

/** Complete context for test command */
export interface TestContext extends CommandContext<TestArgs> {
  readonly options: TestOptions;
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
  onInit?: CommandHook<InitContext>;
  deployCommand?: ManagedCommand<DeployContext>;
  onServer?: CommandHook<ServerContext>;
  onServerStart?: CommandHook<ServerStartContext>;
  onServerStop?: CommandHook<ServerStopContext>;
  onServerRestart?: CommandHook<ServerRestartContext>;
  onDatabase?: CommandHook<DatabaseContext>;
  onDatabaseMigrate?: CommandHook<DatabaseMigrateContext>;
  onDatabaseSeed?: CommandHook<DatabaseSeedContext>;
  onDatabaseBackup?: CommandHook<DatabaseBackupContext>;
  onTest?: CommandHook<TestContext>;
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
      server: {
        desc: string;
        icon?: string;
        alias?: string;
        is_default?: boolean;
        lifecycle?: 'standard' | 'managed';
        subcommands: Record<string, unknown>;
      };
      database: {
        desc: string;
        icon?: string;
        alias?: string;
        is_default?: boolean;
        lifecycle?: 'standard' | 'managed';
        subcommands: Record<string, unknown>;
      };
      test: {
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

export * from './decorators.js';
export * from './validators.js';
export * from './plugins.js';