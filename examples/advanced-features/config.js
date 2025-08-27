/**
 * Configuration management for Nested Command Demo
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const yaml = require('js-yaml');

class ConfigManager {
    constructor(configFile = null) {
        this.configFile = configFile || this._getDefaultConfigPath();
        this.config = {            debug: false,
            outputFormat: 'text'        };
        this.loadConfig();
    }

    _getDefaultConfigPath() {
        const configDir = path.join(os.homedir(), '.config', 'nested-command-demo');
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
                } else {
                    data = yaml.load(content);
                }

                if (data) {
                    Object.assign(this.config, data);
                }
            } catch (error) {
                console.warn(`Warning: Failed to load config file ${this.configFile}: ${error.message}`);
            }
        }

        // Override with environment variables
        const envPrefix = 'NESTED_COMMAND_DEMO_';
        for (const key of Object.keys(this.config)) {
            const envKey = `${envPrefix}${key.toUpperCase()}`;
            if (process.env[envKey]) {
                let value = process.env[envKey];
                
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

    saveConfig() {
        try {
            const configDir = path.dirname(this.configFile);
            if (!fs.existsSync(configDir)) {
                fs.mkdirSync(configDir, { recursive: true });
            }

            const content = yaml.dump(this.config);
            fs.writeFileSync(this.configFile, content, 'utf8');
        } catch (error) {
            console.error(`Error: Failed to save config file ${this.configFile}: ${error.message}`);
        }
    }

    get(key, defaultValue = null) {
        return this.config[key] !== undefined ? this.config[key] : defaultValue;
    }

    set(key, value) {
        if (key in this.config) {
            this.config[key] = value;
        } else {
            throw new Error(`Unknown configuration key: ${key}`);
        }
    }

    toObject() {
        return { ...this.config };
    }
}

// Global configuration instance
let _configManager = null;

function getConfig() {
    if (!_configManager) {
        _configManager = new ConfigManager();
    }
    return _configManager;
}

module.exports = {
    ConfigManager,
    getConfig
};