// Type definitions for Demo TypeScript CLI CLI
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

export interface GreetOptions {
  style?: string;
  count?: number;
  uppercase?: boolean;
  language?: string;
}

export interface InfoOptions {
  format?: string;
  verbose?: boolean;
  sections?: string;
}


export type HookFunction = (context: CommandContext) => Promise<void> | void;

export interface HookRegistry {
  [key: string]: HookFunction;
}
