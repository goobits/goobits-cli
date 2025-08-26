/**
 * Configuration management for Demo TypeScript CLI
 */
interface ConfigSchema {
    debug: boolean;
    outputFormat: string;
}
export declare class ConfigManager {
    private configFile;
    private config;
    constructor(configFile?: string);
    private getDefaultConfigPath;
    loadConfig(): void;
    saveConfig(): void;
    get<K extends keyof ConfigSchema>(key: K): ConfigSchema[K];
    get(key: string, defaultValue?: any): any;
    set<K extends keyof ConfigSchema>(key: K, value: ConfigSchema[K]): void;
    set(key: string, value: any): void;
    toObject(): ConfigSchema;
}
export declare function getConfig(): ConfigManager;
export {};
//# sourceMappingURL=config.d.ts.map