"use strict";
/**
 * Configuration management for Demo TypeScript CLI
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConfigManager = void 0;
exports.getConfig = getConfig;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const os = __importStar(require("os"));
const yaml = __importStar(require("js-yaml"));
class ConfigManager {
    constructor(configFile) {
        this.configFile = configFile || this.getDefaultConfigPath();
        this.config = { debug: false,
            outputFormat: 'text' };
        this.loadConfig();
    }
    getDefaultConfigPath() {
        const configDir = path.join(os.homedir(), '.config', 'demo-typescript-cli');
        if (!fs.existsSync(configDir)) {
            fs.mkdirSync(configDir, { recursive: true });
        }
        return path.join(configDir, 'config.yaml');
    }
    loadConfig() {
        // Load from config file if it exists
        if (fs.existsSync(this.configFile)) {
            try {
                const content = fs.readFileSync(this.configFile, 'utf8');
                let data;
                if (this.configFile.endsWith('.json')) {
                    data = JSON.parse(content);
                }
                else {
                    data = yaml.load(content);
                }
                if (data) {
                    Object.assign(this.config, data);
                }
            }
            catch (error) {
                console.warn(`Warning: Failed to load config file ${this.configFile}: ${error.message}`);
            }
        }
        // Override with environment variables
        const envPrefix = 'DEMO_TYPESCRIPT_CLI_';
        for (const key of Object.keys(this.config)) {
            const envKey = `${envPrefix}${String(key).toUpperCase()}`;
            if (process.env[envKey]) {
                let value = process.env[envKey];
                // Convert string values to appropriate types
                const currentValue = this.config[key];
                if (typeof currentValue === 'boolean') {
                    value = ['true', '1', 'yes', 'on'].includes(value.toLowerCase());
                }
                else if (typeof currentValue === 'number') {
                    value = Number(value);
                }
                this.config[key] = value;
            }
        }
    }
    saveConfig() {
        try {
            const configDir = path.dirname(this.configFile);
            if (!fs.existsSync(configDir)) {
                fs.mkdirSync(configDir, { recursive: true });
            }
            const content = yaml.dump(this.config);
            fs.writeFileSync(this.configFile, content, 'utf8');
        }
        catch (error) {
            console.error(`Error: Failed to save config file ${this.configFile}: ${error.message}`);
        }
    }
    get(key, defaultValue = null) {
        return this.config[key] !== undefined ? this.config[key] : defaultValue;
    }
    set(key, value) {
        if (key in this.config) {
            this.config[key] = value;
        }
        else {
            throw new Error(`Unknown configuration key: ${key}`);
        }
    }
    toObject() {
        return { ...this.config };
    }
}
exports.ConfigManager = ConfigManager;
// Global configuration instance
let _configManager = null;
function getConfig() {
    if (!_configManager) {
        _configManager = new ConfigManager();
    }
    return _configManager;
}
//# sourceMappingURL=config.js.map