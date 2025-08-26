#!/usr/bin/env node
/**
 * Universal completion engine for goobits-generated CLIs (TypeScript)
 * Reads goobits.yaml at runtime and provides context-aware completions
 */
export declare class CompletionEngine {
    private configPath;
    private config;
    constructor(configPath?: string);
    private findConfig;
    private loadConfig;
    getCompletions(shell: string, currentLine: string, cursorPos?: number): string[];
    private parseCommandLine;
    private analyzeContext;
    private generateCompletions;
    private getCommandCompletions;
    private getSubcommandCompletions;
    private getOptionCompletions;
    private getOptionValueCompletions;
    private findOptionConfig;
    private getFileCompletions;
    private getDirectoryCompletions;
}
//# sourceMappingURL=completion_engine.d.ts.map