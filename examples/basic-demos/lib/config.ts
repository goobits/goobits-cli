/**
 * Configuration management for Demo TypeScript CLI
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import * as yaml from 'js-yaml';

interface ConfigSchema {    debug: boolean;
    outputFormat: string;}

export class ConfigManager {
    private configFile: string;
    private config: ConfigSchema;

    constructor(configFile?: string) {
        this.configFile = configFile || this.getDefaultConfigPath();
        this.config = {            debug: false,
            outputFormat: 'text'        };
        this.loadConfig();
    }

    private getDefaultConfigPath(): string {
        const configDir = path.join(os.homedir(), '.config', 'demo-typescript-cli');
        if (!fs.existsSync(configDir)) {
            fs.mkdirSync(configDir, { recursive: true });
        }
        return path.join(configDir, 'config.yaml');
    }

    public loadConfig(): void {
        // Load from config file if it exists
        if (fs.existsSync(this.configFile)) {
            try {
                const content = fs.readFileSync(this.configFile, 'utf8');
                let data: any;
                
                if (this.configFile.endsWith('.json')) {
                    data = JSON.parse(content);
                } else {
                    data = yaml.load(content);
                }

                if (data) {
                    Object.assign(this.config, data);
                }
            } catch (error) {
                console.warn(`Warning: Failed to load config file ${this.configFile}: ${(error as Error).message}`);
            }
        }

        // Override with environment variables
        const envPrefix = 'DEMO_TYPESCRIPT_CLI_';
        for (const key of Object.keys(this.config) as (keyof ConfigSchema)[]) {
            const envKey = `${envPrefix}${String(key).toUpperCase()}`;
            if (process.env[envKey]) {
                let value: any = process.env[envKey];
                
                // Convert string values to appropriate types
                const currentValue = this.config[key];
                if (typeof currentValue === 'boolean') {
                    value = ['true', '1', 'yes', 'on'].includes(value.toLowerCase());
                } else if (typeof currentValue === 'number') {
                    value = Number(value);
                }
                
                this.config[key] = value;
            }
        }
    }

    public saveConfig(): void {
        try {
            const configDir = path.dirname(this.configFile);
            if (!fs.existsSync(configDir)) {
                fs.mkdirSync(configDir, { recursive: true });
            }

            const content = yaml.dump(this.config);
            fs.writeFileSync(this.configFile, content, 'utf8');
        } catch (error) {
            console.error(`Error: Failed to save config file ${this.configFile}: ${(error as Error).message}`);
        }
    }

    public get<K extends keyof ConfigSchema>(key: K): ConfigSchema[K];
    public get(key: string, defaultValue?: any): any;
    public get(key: any, defaultValue: any = null): any {
        return this.config[key as keyof ConfigSchema] !== undefined ? this.config[key as keyof ConfigSchema] : defaultValue;
    }

    public set<K extends keyof ConfigSchema>(key: K, value: ConfigSchema[K]): void;
    public set(key: string, value: any): void;
    public set(key: any, value: any): void {
        if (key in this.config) {
            (this.config as any)[key] = value;
        } else {
            throw new Error(`Unknown configuration key: ${key}`);
        }
    }

    public toObject(): ConfigSchema {
        return { ...this.config };
    }
}

// Global configuration instance
let _configManager: ConfigManager | null = null;

export function getConfig(): ConfigManager {
    if (!_configManager) {
        _configManager = new ConfigManager();
    }
    return _configManager;
}