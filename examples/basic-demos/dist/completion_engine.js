#!/usr/bin/env node
import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';
export class CompletionEngine {
    configPath;
    config;
    constructor(configPath) {
        this.configPath = configPath || this.findConfig();
        this.config = this.loadConfig();
    }
    findConfig() {
        let current = process.cwd();
        while (current !== path.dirname(current)) {
            const configFile = path.join(current, 'goobits.yaml');
            if (fs.existsSync(configFile)) {
                return configFile;
            }
            current = path.dirname(current);
        }
        return path.join(process.cwd(), 'goobits.yaml');
    }
    loadConfig() {
        try {
            if (fs.existsSync(this.configPath)) {
                const content = fs.readFileSync(this.configPath, 'utf8');
                return yaml.load(content) || {};
            }
        }
        catch (error) {
        }
        return {};
    }
    getCompletions(shell, currentLine, cursorPos) {
        try {
            const tokens = this.parseCommandLine(currentLine, cursorPos);
            const context = this.analyzeContext(tokens);
            const completions = this.generateCompletions(context);
            return [...new Set(completions)].sort();
        }
        catch (error) {
            return [];
        }
    }
    parseCommandLine(line, cursorPos) {
        if (cursorPos === undefined) {
            cursorPos = line.length;
        }
        const relevantLine = line.substring(0, cursorPos);
        const tokens = [];
        let currentToken = "";
        let inQuotes = false;
        let quoteChar = null;
        for (let i = 0; i < relevantLine.length; i++) {
            const char = relevantLine[i];
            if ((char === '"' || char === "'") && !inQuotes) {
                inQuotes = true;
                quoteChar = char;
                currentToken += char;
            }
            else if (char === quoteChar && inQuotes) {
                inQuotes = false;
                currentToken += char;
                quoteChar = null;
            }
            else if (/\s/.test(char) && !inQuotes) {
                if (currentToken) {
                    tokens.push(currentToken);
                    currentToken = "";
                }
            }
            else {
                currentToken += char;
            }
        }
        if (currentToken) {
            tokens.push(currentToken);
        }
        return tokens;
    }
    analyzeContext(tokens) {
        if (!tokens.length) {
            return { type: "command", level: 0, lastToken: "", previousToken: "" };
        }
        if (tokens.length > 0) {
            tokens = tokens.slice(1);
        }
        if (!tokens.length) {
            return { type: "command", level: 0, lastToken: "", previousToken: "" };
        }
        const context = {
            type: "unknown",
            level: 0,
            currentCommand: undefined,
            subcommand: undefined,
            lastToken: tokens[tokens.length - 1] || "",
            previousToken: tokens.length > 1 ? tokens[tokens.length - 2] : "",
        };
        if (context.lastToken.startsWith("-")) {
            context.type = "option";
            return context;
        }
        if (context.previousToken.startsWith("-")) {
            context.type = "option_value";
            context.option = context.previousToken;
            return context;
        }
        const cliCommands = this.config.cli?.commands || {};
        if (tokens.length === 1) {
            context.type = "command";
            context.level = 0;
            context.partial = tokens[0];
        }
        else if (tokens[0] in cliCommands) {
            const commandConfig = cliCommands[tokens[0]];
            context.currentCommand = tokens[0];
            if (commandConfig.subcommands && tokens.length === 2) {
                context.type = "subcommand";
                context.level = 1;
                context.partial = tokens[1];
            }
            else if (commandConfig.subcommands && tokens.length > 2 && tokens[1] in commandConfig.subcommands) {
                context.type = "option";
                context.subcommand = tokens[1];
                context.level = 2;
            }
            else {
                context.type = "option";
                context.level = 1;
            }
        }
        return context;
    }
    generateCompletions(context) {
        const completions = [];
        switch (context.type) {
            case "command":
                completions.push(...this.getCommandCompletions(context));
                break;
            case "subcommand":
                completions.push(...this.getSubcommandCompletions(context));
                break;
            case "option":
                completions.push(...this.getOptionCompletions(context));
                break;
            case "option_value":
                completions.push(...this.getOptionValueCompletions(context));
                break;
        }
        const partial = context.partial || "";
        if (partial) {
            return completions.filter(c => c.startsWith(partial));
        }
        return completions;
    }
    getCommandCompletions(context) {
        const commands = [];
        const cliCommands = this.config.cli?.commands || {};
        commands.push(...Object.keys(cliCommands));
        const builtinCommands = ["help", "version"];
        const cliConfig = this.config.cli || {};
        if (cliConfig.enable_upgrade_command !== false) {
            builtinCommands.push("upgrade");
        }
        commands.push(...builtinCommands);
        return commands;
    }
    getSubcommandCompletions(context) {
        const command = context.currentCommand;
        if (!command) {
            return [];
        }
        const cliCommands = this.config.cli?.commands || {};
        const commandConfig = cliCommands[command] || {};
        const subcommands = commandConfig.subcommands || {};
        return Object.keys(subcommands);
    }
    getOptionCompletions(context) {
        const options = [];
        const globalOptions = this.config.cli?.options || [];
        for (const opt of globalOptions) {
            options.push(`--${opt.name}`);
            if (opt.short) {
                options.push(`-${opt.short}`);
            }
        }
        const command = context.currentCommand;
        if (command) {
            const cliCommands = this.config.cli?.commands || {};
            let commandConfig = cliCommands[command] || {};
            const subcommand = context.subcommand;
            if (subcommand && commandConfig.subcommands) {
                commandConfig = commandConfig.subcommands[subcommand] || {};
            }
            const commandOptions = commandConfig.options || [];
            for (const opt of commandOptions) {
                options.push(`--${opt.name}`);
                if (opt.short) {
                    options.push(`-${opt.short}`);
                }
            }
        }
        options.push("--help", "-h", "--version", "-V");
        return options;
    }
    getOptionValueCompletions(context) {
        const option = (context.option || "").replace(/^-+/, "");
        const optionConfig = this.findOptionConfig(option, context);
        if (!optionConfig) {
            return [];
        }
        const optionType = optionConfig.type || "str";
        if (optionType === "choice" && optionConfig.choices) {
            return optionConfig.choices;
        }
        else if (optionType === "file" || ["config", "file", "input"].includes(option)) {
            return this.getFileCompletions();
        }
        else if (optionType === "dir" || ["directory", "dir", "output-dir"].includes(option)) {
            return this.getDirectoryCompletions();
        }
        else if (optionType === "bool" || optionType === "flag") {
            return ["true", "false"];
        }
        return [];
    }
    findOptionConfig(optionName, context) {
        const globalOptions = this.config.cli?.options || [];
        for (const opt of globalOptions) {
            if (opt.name === optionName || opt.short === optionName) {
                return opt;
            }
        }
        const command = context.currentCommand;
        if (command) {
            const cliCommands = this.config.cli?.commands || {};
            let commandConfig = cliCommands[command] || {};
            const subcommand = context.subcommand;
            if (subcommand && commandConfig.subcommands) {
                commandConfig = commandConfig.subcommands[subcommand] || {};
            }
            const commandOptions = commandConfig.options || [];
            for (const opt of commandOptions) {
                if (opt.name === optionName || opt.short === optionName) {
                    return opt;
                }
            }
        }
        return null;
    }
    getFileCompletions() {
        try {
            const files = [];
            const items = fs.readdirSync(".");
            for (const item of items) {
                const stat = fs.statSync(item);
                if (stat.isFile()) {
                    files.push(item);
                }
            }
            return files;
        }
        catch (error) {
            return [];
        }
    }
    getDirectoryCompletions() {
        try {
            const dirs = [];
            const items = fs.readdirSync(".");
            for (const item of items) {
                const stat = fs.statSync(item);
                if (stat.isDirectory()) {
                    dirs.push(item + "/");
                }
            }
            return dirs;
        }
        catch (error) {
            return [];
        }
    }
}
function main() {
    if (process.argv.length < 4) {
        process.exit(1);
    }
    const shell = process.argv[2];
    const currentLine = process.argv[3];
    const cursorPos = process.argv.length > 4 ? parseInt(process.argv[4]) : undefined;
    const engine = new CompletionEngine();
    const completions = engine.getCompletions(shell, currentLine, cursorPos);
    for (const completion of completions) {
        console.log(completion);
    }
}
if (require.main === module) {
    main();
}
//# sourceMappingURL=completion_engine.js.map