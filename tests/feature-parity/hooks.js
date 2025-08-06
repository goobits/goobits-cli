/**
 * Hook implementations for the test CLI (Node.js/TypeScript)
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

async function onHello({ name, greeting = "Hello" }) {
    console.log(`${greeting} ${name}`);
    return 0;
}

async function onConfigGet({ key }) {
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

async function onConfigSet({ key, value }) {
    console.log(`Setting ${key} to ${value}`);
    return 0;
}

async function onConfigList() {
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

async function onConfigReset({ force }) {
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

async function onFail({ code = 1 }) {
    console.error(`Error: Command failed with exit code ${code}`);
    return code;
}

async function onEcho({ words }) {
    if (words && words.length > 0) {
        console.log(words.join(' '));
    }
    return 0;
}

async function onFileCreate({ path: filePath, content }) {
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

async function onFileDelete({ path: filePath }) {
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

module.exports = {
    onHello,
    onConfigGet,
    onConfigSet,
    onConfigList,
    onConfigReset,
    onFail,
    onEcho,
    onFileCreate,
    onFileDelete
};