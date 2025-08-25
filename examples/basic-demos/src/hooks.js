/**
 * Hook implementations for Node.js CLI demo
 */

async function onGreet(args) {
    // Handle both Node.js (direct args) and TypeScript (context object) formats
    let name, message = "Hello", style = "casual", count = 1, uppercase = false, language = "en";
    
    if (args.args && args.options) {
        // TypeScript format: { commandName, args: { name, message }, options: { style, count, etc } }
        ({ name, message = "Hello" } = args.args);
        ({ style = "casual", count = 1, uppercase = false, language = "en" } = args.options);
    } else {
        // Node.js format: direct destructuring
        ({ name, message = "Hello", style = "casual", count = 1, uppercase = false, language = "en" } = args);
    }
    
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
    
    console.log(`Welcome to the CLI demo, ${name}!`);
}

async function onInfo(args) {
    // Handle both Node.js (direct args) and TypeScript (context object) formats
    let format = "text", verbose = false, sections = "all";
    
    if (args.args && args.options) {
        // TypeScript format: { commandName, args: {}, options: { format, verbose, etc } }
        ({ format = "text", verbose = false, sections = "all" } = args.options);
    } else {
        // Node.js format: direct destructuring
        ({ format = "text", verbose = false, sections = "all" } = args);
    }
    
    const info = {
        title: "=== CLI Information ===",
        separator: "=====================",
        node_version: `Node Version: ${process.version}`,
        platform: `Platform: ${process.platform}`,
        architecture: `Architecture: ${process.arch}`,
        memory: `Memory Usage: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)} MB`
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

module.exports = {
    onGreet,
    onInfo
};