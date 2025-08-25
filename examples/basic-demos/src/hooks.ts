/**
 * Hook functions for Demo TypeScript CLI
 * Auto-generated from typescript-example.yaml
 * 
 * Implement your business logic in these hook functions.
 * Each command will call its corresponding hook function.
 */

// Type definitions for hook arguments
interface CommandArgs {
  commandName: string;
  rawArgs?: Record<string, any>;
  [key: string]: any;
}

/**
 * Hook function for unknown commands
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
export async function onUnknownCommand(args: CommandArgs): Promise<void> {
  console.log(`🤔 Unknown command: ${args.commandName}`);
  console.log('   Use --help to see available commands');
}


/**
 * Hook function for 'greet' command
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
export async function onGreet(args: CommandArgs): Promise<void> {
    // Handle both Node.js (direct args) and TypeScript (context object) formats
    let name: string, message = "Hello", style = "casual", count = 1, uppercase = false, language = "en";
    
    if (args.args && args.options) {
        // TypeScript format: { commandName, args: { name, message }, options: { style, count, etc } }
        ({ name, message = "Hello" } = args.args as any);
        // Commander.js may use single letter keys for options with short flags
        style = args.options.style || args.options.S || "casual";
        count = args.options.count || args.options.C || 1;
        uppercase = args.options.uppercase || args.options.U || false;
        language = args.options.language || args.options.L || "en";
    } else {
        // Node.js format: direct destructuring
        ({ name, message = "Hello", style = "casual", count = 1, uppercase = false, language = "en" } = args as any);
    }

    // Generate greeting based on style
    let greeting = "";
    if (style === "formal") {
        greeting = `Good day, ${name}. ${message} to the CLI demo.`;
    } else if (style === "excited") {
        greeting = `🎉 ${message}, ${name}! Welcome to the amazing CLI demo!!! 🚀`;
    } else {
        greeting = `${message}, ${name}! Welcome to the CLI demo, ${name}!`;
    }
    
    // Apply uppercase if requested
    if (uppercase) {
        greeting = greeting.toUpperCase();
    }
    
    // Repeat based on count
    for (let i = 0; i < count; i++) {
        console.log(greeting);
    }
}

/**
 * Hook function for 'info' command
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
export async function onInfo(args: CommandArgs): Promise<void> {
    // Handle both Node.js (direct args) and TypeScript (context object) formats
    let format = "text", verbose = false, sections = "all";
    
    if (args.options) {
        // TypeScript format: { commandName, options: { format, verbose, sections } }
        // Commander.js may use single letter keys for options with short flags
        format = args.options.format || args.options.F || "text";
        verbose = args.options.verbose || args.options.V || false;
        sections = args.options.sections || args.options.S || "all";
    } else {
        // Node.js format: direct destructuring
        ({ format = "text", verbose = false, sections = "all" } = args as any);
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
