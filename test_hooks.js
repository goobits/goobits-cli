#!/usr/bin/env node
/**
 * Hook implementation for Node.js feature testing
 */

import fs from 'fs/promises';
import path from 'path';
import { spawn } from 'child_process';

export async function onHello(args) {
    const { name, surname, greeting = "Hello", uppercase = false, repeat = 1, separator = " " } = args;
    
    let fullName = surname ? `${name} ${surname}` : name;
    let message = `${greeting} ${fullName}`;
    
    if (uppercase) {
        message = message.toUpperCase();
    }
    
    const messages = Array(repeat).fill(message);
    const output = messages.join(separator);
    console.log(output);
}

export async function onDataProcess(args) {
    const { 
        inputFile, 
        filters = [], 
        output, 
        format = "json", 
        validate = false, 
        batchSize = 100, 
        timeout = 30.0 
    } = args;
    
    console.log(`Processing ${inputFile}`);
    if (filters.length > 0) {
        console.log(`Applying filters: ${filters.join(', ')}`);
    }
    
    // Simulate processing
    if (validate) {
        console.log("Validating input data...");
    }
    
    console.log(`Processing in batches of ${batchSize}`);
    console.log(`Timeout: ${timeout}s`);
    console.log(`Output format: ${format}`);
    
    if (output) {
        console.log(`Writing to: ${output}`);
        // Create dummy output file
        const outputDir = path.dirname(output);
        await fs.mkdir(outputDir, { recursive: true });
        await fs.writeFile(output, JSON.stringify({ processed: true, input: inputFile }, null, 2));
    }
}

export async function onDataValidate(args) {
    const { file, schema, strict = false } = args;
    
    console.log(`Validating ${file}`);
    if (schema) {
        console.log(`Using schema: ${schema}`);
    }
    if (strict) {
        console.log("Strict validation enabled");
    }
    console.log("✅ Validation passed");
}

export async function onDataConvert(args) {
    const { source, target, sourceFormat, targetFormat, pretty = false } = args;
    
    console.log(`Converting ${source} -> ${target}`);
    if (sourceFormat) {
        console.log(`Source format: ${sourceFormat}`);
    }
    if (targetFormat) {
        console.log(`Target format: ${targetFormat}`);
    }
    if (pretty) {
        console.log("Pretty printing enabled");
    }
    console.log("✅ Conversion completed");
}

export async function onConfigGet(args) {
    const { key, default: defaultValue } = args;
    
    // Mock config values
    const mockConfig = {
        "theme": "default",
        "api_key": "",
        "timeout": "30",
        "debug": "false"
    };
    
    const value = mockConfig[key] ?? defaultValue;
    if (value === undefined) {
        console.error(`Configuration key '${key}' not found`);
        process.exit(1);
    }
    
    console.log(value);
}

export async function onConfigSet(args) {
    const { key, value, type = "string" } = args;
    
    console.log(`Setting ${key} = ${value} (type: ${type})`);
    console.log("✅ Configuration updated");
}

export async function onConfigList(args) {
    const { filter, showDefaults = false } = args;
    
    const mockConfig = {
        "theme": "default",
        "api_key": "",
        "timeout": "30",
        "debug": "false"
    };
    
    console.log("Configuration values:");
    for (const [k, v] of Object.entries(mockConfig)) {
        if (filter && !k.includes(filter)) {
            continue;
        }
        const status = showDefaults && !v ? " (default)" : "";
        console.log(`  ${k}: ${v}${status}`);
    }
}

export async function onConfigDelete(args) {
    const { key, force = false } = args;
    
    if (!force) {
        console.log(`This will delete configuration key '${key}'. Use --force to confirm.`);
        process.exit(1);
    }
    
    console.log(`Deleted configuration key: ${key}`);
}

export async function onConfigReset(args) {
    const { force = false } = args;
    
    if (!force) {
        console.log("This will reset all configuration to defaults. Use --force to confirm.");
        process.exit(1);
    }
    
    console.log("✅ Configuration reset to defaults");
}

export async function onFileCreate(args) {
    const { 
        paths, 
        content = "", 
        template, 
        permissions = "644", 
        directory = false 
    } = args;
    
    for (const filepath of paths) {
        if (directory) {
            await fs.mkdir(filepath, { recursive: true });
            console.log(`Created directory: ${filepath}`);
        } else {
            await fs.mkdir(path.dirname(filepath), { recursive: true });
            let writeContent = content;
            if (template) {
                writeContent = `Template: ${template}\nContent: ${content}`;
            }
            
            await fs.writeFile(filepath, writeContent);
            await fs.chmod(filepath, parseInt(permissions, 8));
            console.log(`Created file: ${filepath}`);
        }
    }
}

export async function onFileDelete(args) {
    const { paths, recursive = false, force = false } = args;
    
    for (const filepath of paths) {
        try {
            const stats = await fs.stat(filepath);
            
            if (!force) {
                console.log(`Delete ${filepath}? Use --force to confirm.`);
                continue;
            }
            
            if (stats.isDirectory()) {
                if (recursive) {
                    await fs.rm(filepath, { recursive: true });
                    console.log(`Deleted directory: ${filepath}`);
                } else {
                    try {
                        await fs.rmdir(filepath);
                        console.log(`Deleted directory: ${filepath}`);
                    } catch (err) {
                        console.error(`Directory not empty: ${filepath}. Use --recursive.`);
                    }
                }
            } else {
                await fs.unlink(filepath);
                console.log(`Deleted file: ${filepath}`);
            }
        } catch (err) {
            if (err.code !== 'ENOENT') {
                console.error(`Error deleting ${filepath}: ${err.message}`);
            }
        }
    }
}

export async function onFileCopy(args) {
    const { source, destination, recursive = false, preserve = false } = args;
    
    try {
        const stats = await fs.stat(source);
        
        if (stats.isDirectory()) {
            if (!recursive) {
                console.error("Source is directory but --recursive not specified");
                process.exit(1);
            }
            // Simple directory copy (Node.js doesn't have built-in recursive copy)
            await fs.cp(source, destination, { recursive: true });
        } else {
            await fs.copyFile(source, destination);
            if (preserve) {
                const sourceStats = await fs.stat(source);
                await fs.chmod(destination, sourceStats.mode);
                await fs.utimes(destination, sourceStats.atime, sourceStats.mtime);
            }
        }
        
        console.log(`Copied ${source} -> ${destination}`);
    } catch (err) {
        console.error(`Error copying: ${err.message}`);
        process.exit(1);
    }
}

export async function onFileMove(args) {
    const { source, destination } = args;
    
    try {
        await fs.rename(source, destination);
        console.log(`Moved ${source} -> ${destination}`);
    } catch (err) {
        console.error(`Error moving: ${err.message}`);
        process.exit(1);
    }
}

export async function onTypes(args) {
    const { 
        text, 
        numbers = [], 
        stringVal = "default", 
        intVal = 42, 
        floatVal = 3.14, 
        boolVal = false, 
        choiceVal = "alpha", 
        multipleVals = [] 
    } = args;
    
    console.log(`Text: ${text}`);
    if (numbers.length > 0) {
        console.log(`Numbers: ${numbers.join(', ')}`);
    }
    
    console.log(`String value: ${stringVal}`);
    console.log(`Integer value: ${intVal}`);
    console.log(`Float value: ${floatVal}`);
    console.log(`Boolean value: ${boolVal}`);
    console.log(`Choice value: ${choiceVal}`);
    
    if (multipleVals.length > 0) {
        console.log(`Multiple values: ${multipleVals.join(', ')}`);
    }
}

export async function onTestErrorsFail(args) {
    const { code = 1, message = "Test failure" } = args;
    
    console.error(message);
    process.exit(code);
}

export async function onTestErrorsTimeout(args) {
    const { seconds = 5.0 } = args;
    
    console.log(`Starting timeout test (${seconds}s)...`);
    await new Promise(resolve => setTimeout(resolve, seconds * 1000));
    console.log("Timeout test completed");
}

export async function onTestErrorsException(args) {
    const { type = "runtime" } = args;
    
    switch (type) {
        case "runtime":
            throw new Error("Test runtime error");
        case "value":
            throw new Error("Test value error");
        case "type":
            throw new TypeError("Test type error");
        case "key":
            throw new Error("Test key error: test_key");
        default:
            throw new Error(`Unknown exception type: ${type}`);
    }
}

export async function onInteractive(args) {
    const { noPrompt = false } = args;
    
    if (noPrompt) {
        console.log("Interactive mode disabled");
        return;
    }
    
    console.log("Entering interactive mode...");
    console.log("(This is a simulation - real interactive mode would start REPL)");
}

export async function onPerformance(args) {
    const { operation, iterations = 100, size = 1000 } = args;
    
    console.log(`Running ${operation} performance test`);
    console.log(`Iterations: ${iterations}`);
    console.log(`Data size: ${size}`);
    
    const startTime = Date.now();
    
    switch (operation) {
        case "startup":
            // Simulate startup operations
            for (let i = 0; i < iterations; i++) {
                // Empty loop
            }
            break;
        case "memory":
            // Simulate memory operations
            const data = Array.from({ length: size }, (_, i) => i);
            for (let i = 0; i < iterations; i++) {
                const len = data.length;
            }
            break;
        case "cpu":
            // Simulate CPU operations
            for (let i = 0; i < iterations; i++) {
                let sum = 0;
                for (let j = 0; j < size; j++) {
                    sum += j;
                }
            }
            break;
        case "io":
            // Simulate I/O operations
            const tempPath = `/tmp/test-${Date.now()}.txt`;
            for (let i = 0; i < iterations; i++) {
                await fs.writeFile(tempPath, "test data\n");
            }
            await fs.unlink(tempPath).catch(() => {});
            break;
    }
    
    const duration = (Date.now() - startTime) / 1000;
    console.log(`✅ Performance test completed in ${duration.toFixed(3)}s`);
    console.log(`Average per operation: ${(duration / iterations * 1000).toFixed(3)}ms`);
}

export async function onUnknownCommand(args) {
    console.error("Unknown command executed");
    process.exit(1);
}