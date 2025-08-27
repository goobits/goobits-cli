// Type definitions for Test TypeScript CLI
export interface CLIOptions {
  verbose?: boolean;
  debug?: boolean;
  quiet?: boolean;
  config?: string;
}

export interface CommandContext {
  name: string;
  args: string[];
  options: CLIOptions;
}

export interface HelloOptions {
}


export type HookFunction = (context: CommandContext) => Promise<void> | void;

export interface HookRegistry {
  [key: string]: HookFunction;
}
