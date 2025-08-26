// Type definitions for Test Universal CLI CLI
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
  greeting?: string;
}


export type HookFunction = (context: CommandContext) => Promise<void> | void;

export interface HookRegistry {
  [key: string]: HookFunction;
}
