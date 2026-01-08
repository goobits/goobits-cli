/**
 * Hook implementations for the test CLI (Node.js/TypeScript)
 */

import fs from 'fs';
import path from 'path';
import readline from 'readline';

async function on_hello(name, options = {}) {
    const { greeting = "Hello" } = options;
    console.log(`${greeting} ${name}`);
    return 0;
}

async function on_config_get(key, options = {}) {
    const defaultConfig = {
        theme: process.env.TEST_CLI_THEME || "default",
        api_key: "",
        timeout: 30
    };
    
    if (key in defaultConfig) {
        console.log(`${key}: ${defaultConfig[key]}`);
        return 0;
    } else {
        console.error(`Config key '${key}' not found`);
        return 1;
    }
}

async function on_config_set(key, value, options = {}) {
    console.log(`Setting ${key} to ${value}`);
    return 0;
}

async function on_config_list(options = {}) {
    const defaultConfig = {
        theme: "default",
        api_key: "",
        timeout: 30
    };
    
    for (const [key, value] of Object.entries(defaultConfig)) {
        console.log(`${key}: ${value}`);
    }
    return 0;
}

async function on_config_reset(options = {}) {
    const { force } = options;
    if (!force) {
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        
        return new Promise((resolve) => {
            rl.question('Are you sure you want to reset the configuration? (y/N): ', (answer) => {
                rl.close();
                if (answer.toLowerCase() !== 'y') {
                    console.log('Reset cancelled');
                    resolve(0);
                } else {
                    console.log('Configuration reset to defaults');
                    resolve(0);
                }
            });
        });
    }
    
    console.log('Configuration reset to defaults');
    return 0;
}

async function on_fail(options = {}) {
    const { code = 1 } = options;
    console.error(`Error: Command failed with exit code ${code}`);
    return code;
}

async function on_echo(words, options = {}) {
    if (words && words.length > 0) {
        console.log(words.join(' '));
    }
    return 0;
}

async function on_file_create(filePath, options = {}) {
    const { content } = options;
    try {
        const dir = path.dirname(filePath);
        await fs.promises.mkdir(dir, { recursive: true });
        
        if (content) {
            await fs.promises.writeFile(filePath, content);
        } else {
            await fs.promises.writeFile(filePath, '');
        }
        
        console.log(`Created file: ${filePath}`);
        return 0;
    } catch (error) {
        if (error.code === 'EACCES') {
            console.error(`Permission denied: ${filePath}`);
        } else {
            console.error(`Error creating file: ${error.message}`);
        }
        return 1;
    }
}

async function on_file_delete(filePath, options = {}) {
    try {
        await fs.promises.unlink(filePath);
        console.log(`Deleted file: ${filePath}`);
        return 0;
    } catch (error) {
        if (error.code === 'ENOENT') {
            console.error(`File not found: ${filePath}`);
        } else if (error.code === 'EACCES') {
            console.error(`Permission denied: ${filePath}`);
        } else {
            console.error(`Error deleting file: ${error.message}`);
        }
        return 1;
    }
}

async function on_config(options = {}) {
    return 0;
}

async function on_file(options = {}) {
    return 0;
}

export {
    on_hello,
    on_config_get,
    on_config_set,
    on_config_list,
    on_config_reset,
    on_fail,
    on_echo,
    on_file_create,
    on_file_delete,
    on_config,
    on_file
};