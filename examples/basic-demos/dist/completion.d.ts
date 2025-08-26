/**
 * Shell completion engine for Demo TypeScript CLI
 */
interface CliSchema {
    root_command: {
        name: string;
        subcommands: Array<{
            name: string;
            description: string;
            options: Array<{
                name: string;
                short?: string;
                description: string;
            }>;
            arguments: Array<{
                name: string;
                description: string;
            }>;
        }>;
    };
}
export declare class CompletionEngine {
    private cliSchema;
    constructor(cliSchema: CliSchema);
    generateBashCompletion(): string;
    generateZshCompletion(): string;
    generateFishCompletion(): string;
    installCompletion(shell?: string | null): Promise<boolean>;
}
export {};
//# sourceMappingURL=completion.d.ts.map