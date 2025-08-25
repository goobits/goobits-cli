#!/usr/bin/env node
/**
 * Hook implementations for Node.js/TypeScript CLI demo
 */

/**
 * Handle greet command
 */
export async function onGreet(args) {
    const { name, message = "Hello", style = "casual", count = 1, uppercase = false, language = "en" } = args;
    
    let greeting = `${message}, ${name}`;
    
    if (uppercase) {
        greeting = greeting.toUpperCase();
    }
    
    // Handle style variations
    switch (style) {
        case "formal":
            greeting += ".";
            break;
        case "excited":
            greeting += "!!!";
            break;
        default: // casual
            greeting += "!";
    }
    
    // Repeat greeting based on count
    for (let i = 0; i < count; i++) {
        console.log(greeting);
    }
    
    console.log(`Welcome to the Node.js CLI demo, ${name}!`);
}

/**
 * Handle info command
 */
export async function onInfo(args) {
    const { format = "text", verbose = false, sections = "all" } = args;
    
    const info = {
        title: "🟢 Node.js CLI Information",
        separator: "-".repeat(30),
        node_version: `Node.js Version: ${process.version}`,
        platform: `Platform: ${process.platform}`,
        architecture: `Architecture: ${process.arch}`,
        memory: `Memory Usage: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB`
    };
    
    if (format === "json") {
        console.log(JSON.stringify({
            node_version: process.version,
            platform: process.platform,
            architecture: process.arch,
            memory_mb: Math.round(process.memoryUsage().heapUsed / 1024 / 1024)
        }, null, 2));
    } else {
        console.log(info.title);
        console.log(info.separator);
        console.log(info.node_version);
        console.log(info.platform);
        console.log(info.architecture);
        if (verbose) {
            console.log(info.memory);
        }
    }
}