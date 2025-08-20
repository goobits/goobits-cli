#!/usr/bin/env node
/**
 * Universal completion engine for goobits-generated CLIs (TypeScript)
 * Reads goobits.yaml at runtime and provides context-aware completions
 */

import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';

interface Option {
  name: string;
  short?: string;
  type?: string;
  choices?: string[];
  desc?: string;
}

interface Command {
  desc?: string;
  args?: Array<{
    name: string;
    required?: boolean;
    choices?: string[];
  }>;
  options?: Option[];
  subcommands?: Record<string, Command>;
}

interface CliConfig {
  cli?: {
    commands?: Record<string, Command>;
    options?: Option[];
    enable_upgrade_command?: boolean;
  };
}

interface Context {
  type: "command" | "subcommand" | "option" | "option_value" | "unknown";
  level: number;
  currentCommand?: string;
  subcommand?: string;
  lastToken: string;
  previousToken: string;
  partial?: string;
  option?: string;
}

export class CompletionEngine {
  private configPath: string;
  private config: CliConfig;

  constructor(configPath?: string) {
    this.configPath = configPath || this.findConfig();
    this.config = this.loadConfig();
  }

  private findConfig(): string {
    let current = process.cwd();
    
    // Search up the directory tree
    while (current !== path.dirname(current)) {
      const configFile = path.join(current, 'goobits.yaml');
      if (fs.existsSync(configFile)) {
        return configFile;
      }
      current = path.dirname(current);
    }
    
    // Fallback to current directory
    return path.join(process.cwd(), 'goobits.yaml');
  }

  private loadConfig(): CliConfig {
    try {
      if (fs.existsSync(this.configPath)) {
        const content = fs.readFileSync(this.configPath, 'utf8');
        return yaml.load(content) as CliConfig || {};
      }
    } catch (error) {
      // Silent fallback for config loading errors
    }
    return {};
  }

  public getCompletions(shell: string, currentLine: string, cursorPos?: number): string[] {
    try {
      // Parse the command line
      const tokens = this.parseCommandLine(currentLine, cursorPos);
      const context = this.analyzeContext(tokens);
      
      // Generate completions based on context
      const completions = this.generateCompletions(context);
      
      return [...new Set(completions)].sort();
    } catch (error) {
      return [];
    }
  }

  private parseCommandLine(line: string, cursorPos?: number): string[] {
    if (cursorPos === undefined) {
      cursorPos = line.length;
    }
    
    // Extract the relevant part of the line up to cursor
    const relevantLine = line.substring(0, cursorPos);
    
    // Simple tokenization (could be enhanced for complex cases)
    const tokens: string[] = [];
    let currentToken = "";
    let inQuotes = false;
    let quoteChar: string | null = null;
    
    for (let i = 0; i < relevantLine.length; i++) {
      const char = relevantLine[i];
      
      if ((char === '"' || char === "'") && !inQuotes) {
        inQuotes = true;
        quoteChar = char;
        currentToken += char;
      } else if (char === quoteChar && inQuotes) {
        inQuotes = false;
        currentToken += char;
        quoteChar = null;
      } else if (/\s/.test(char) && !inQuotes) {
        if (currentToken) {
          tokens.push(currentToken);
          currentToken = "";
        }
      } else {
        currentToken += char;
      }
    }
    
    // Add final token if exists
    if (currentToken) {
      tokens.push(currentToken);
    }
    
    return tokens;
  }

  private analyzeContext(tokens: string[]): Context {
    if (!tokens.length) {
      return { type: "command", level: 0, lastToken: "", previousToken: "" };
    }
    
    // Skip the program name
    if (tokens.length > 0) {
      tokens = tokens.slice(1);
    }
    
    if (!tokens.length) {
      return { type: "command", level: 0, lastToken: "", previousToken: "" };
    }
    
    const context: Context = {
      type: "unknown",
      level: 0,
      currentCommand: undefined,
      subcommand: undefined,
      lastToken: tokens[tokens.length - 1] || "",
      previousToken: tokens.length > 1 ? tokens[tokens.length - 2] : "",
    };
    
    // Check if we're completing an option
    if (context.lastToken.startsWith("-")) {
      context.type = "option";
      return context;
    }
    
    // Check if previous token was an option that expects a value
    if (context.previousToken.startsWith("-")) {
      context.type = "option_value";
      context.option = context.previousToken;
      return context;
    }
    
    // Determine command/subcommand context
    const cliCommands = this.config.cli?.commands || {};
    
    if (tokens.length === 1) {
      // Completing top-level command
      context.type = "command";
      context.level = 0;
      context.partial = tokens[0];
    } else if (tokens[0] in cliCommands) {
      // We have a valid command, check for subcommands
      const commandConfig = cliCommands[tokens[0]];
      context.currentCommand = tokens[0];
      
      if (commandConfig.subcommands && tokens.length === 2) {
        context.type = "subcommand";
        context.level = 1;
        context.partial = tokens[1];
      } else if (commandConfig.subcommands && tokens.length > 2 && tokens[1] in commandConfig.subcommands) {
        context.type = "option";
        context.subcommand = tokens[1];
        context.level = 2;
      } else {
        context.type = "option";
        context.level = 1;
      }
    }
    
    return context;
  }

  private generateCompletions(context: Context): string[] {
    const completions: string[] = [];
    
    switch (context.type) {
      case "command":
        completions.push(...this.getCommandCompletions(context));
        break;
      case "subcommand":
        completions.push(...this.getSubcommandCompletions(context));
        break;
      case "option":
        completions.push(...this.getOptionCompletions(context));
        break;
      case "option_value":
        completions.push(...this.getOptionValueCompletions(context));
        break;
    }
    
    // Filter by partial match if applicable
    const partial = context.partial || "";
    if (partial) {
      return completions.filter(c => c.startsWith(partial));
    }
    
    return completions;
  }

  private getCommandCompletions(context: Context): string[] {
    const commands: string[] = [];
    
    // CLI commands from config
    const cliCommands = this.config.cli?.commands || {};
    commands.push(...Object.keys(cliCommands));
    
    // Built-in commands
    const builtinCommands = ["help", "version"];
    
    // Check if upgrade is enabled
    const cliConfig = this.config.cli || {};
    if (cliConfig.enable_upgrade_command !== false) {
      builtinCommands.push("upgrade");
    }
    
    commands.push(...builtinCommands);
    
    return commands;
  }

  private getSubcommandCompletions(context: Context): string[] {
    const command = context.currentCommand;
    if (!command) {
      return [];
    }
    
    const cliCommands = this.config.cli?.commands || {};
    const commandConfig = cliCommands[command] || {};
    
    const subcommands = commandConfig.subcommands || {};
    return Object.keys(subcommands);
  }

  private getOptionCompletions(context: Context): string[] {
    const options: string[] = [];
    
    // Global options
    const globalOptions = this.config.cli?.options || [];
    for (const opt of globalOptions) {
      options.push(`--${opt.name}`);
      if (opt.short) {
        options.push(`-${opt.short}`);
      }
    }
    
    // Command-specific options
    const command = context.currentCommand;
    if (command) {
      const cliCommands = this.config.cli?.commands || {};
      let commandConfig = cliCommands[command] || {};
      
      // Check if we're in a subcommand
      const subcommand = context.subcommand;
      if (subcommand && commandConfig.subcommands) {
        commandConfig = commandConfig.subcommands[subcommand] || {};
      }
      
      const commandOptions = commandConfig.options || [];
      for (const opt of commandOptions) {
        options.push(`--${opt.name}`);
        if (opt.short) {
          options.push(`-${opt.short}`);
        }
      }
    }
    
    // Standard options
    options.push("--help", "-h", "--version", "-V");
    
    return options;
  }

  private getOptionValueCompletions(context: Context): string[] {
    const option = (context.option || "").replace(/^-+/, "");
    
    // Find option configuration
    const optionConfig = this.findOptionConfig(option, context);
    if (!optionConfig) {
      return [];
    }
    
    const optionType = optionConfig.type || "str";
    
    // Handle different option types
    if (optionType === "choice" && optionConfig.choices) {
      return optionConfig.choices;
    } else if (optionType === "file" || ["config", "file", "input"].includes(option)) {
      return this.getFileCompletions();
    } else if (optionType === "dir" || ["directory", "dir", "output-dir"].includes(option)) {
      return this.getDirectoryCompletions();
    } else if (optionType === "bool" || optionType === "flag") {
      return ["true", "false"];
    }
    
    return [];
  }

  private findOptionConfig(optionName: string, context: Context): Option | null {
    // Check global options
    const globalOptions = this.config.cli?.options || [];
    for (const opt of globalOptions) {
      if (opt.name === optionName || opt.short === optionName) {
        return opt;
      }
    }
    
    // Check command-specific options
    const command = context.currentCommand;
    if (command) {
      const cliCommands = this.config.cli?.commands || {};
      let commandConfig = cliCommands[command] || {};
      
      // Check if we're in a subcommand
      const subcommand = context.subcommand;
      if (subcommand && commandConfig.subcommands) {
        commandConfig = commandConfig.subcommands[subcommand] || {};
      }
      
      const commandOptions = commandConfig.options || [];
      for (const opt of commandOptions) {
        if (opt.name === optionName || opt.short === optionName) {
          return opt;
        }
      }
    }
    
    return null;
  }

  private getFileCompletions(): string[] {
    try {
      const files: string[] = [];
      const items = fs.readdirSync(".");
      for (const item of items) {
        const stat = fs.statSync(item);
        if (stat.isFile()) {
          files.push(item);
        }
      }
      return files;
    } catch (error) {
      return [];
    }
  }

  private getDirectoryCompletions(): string[] {
    try {
      const dirs: string[] = [];
      const items = fs.readdirSync(".");
      for (const item of items) {
        const stat = fs.statSync(item);
        if (stat.isDirectory()) {
          dirs.push(item + "/");
        }
      }
      return dirs;
    } catch (error) {
      return [];
    }
  }
}

// Main completion function - called by CLIs with _completion command
function main(): void {
  if (process.argv.length < 4) {
    process.exit(1);
  }
  
  const shell = process.argv[2];
  const currentLine = process.argv[3];
  const cursorPos = process.argv.length > 4 ? parseInt(process.argv[4]) : undefined;
  
  const engine = new CompletionEngine();
  const completions = engine.getCompletions(shell, currentLine, cursorPos);
  
  // Output completions one per line
  for (const completion of completions) {
    console.log(completion);
  }
}

if (require.main === module) {
  main();
}