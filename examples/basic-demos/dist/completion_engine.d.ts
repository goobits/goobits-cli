#!/usr/bin/env node
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