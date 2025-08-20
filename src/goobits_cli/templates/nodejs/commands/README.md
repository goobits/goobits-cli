# Node.js Command Templates

This directory contains Jinja2 templates for generating Node.js CLI commands using Commander.js.

## Templates

### command.js.j2
Template for generating single commands with argument, option, and hook support.

### group.js.j2
Template for generating command groups with subcommands.

### dynamic-command.js.j2
Template for commands that can be dynamically loaded from the commands/ directory.

### standalone-command.js.j2
Template for generating a single command file that users can customize.

### builtin/upgrade.js.j2
Built-in upgrade command implementation for npm-based CLIs.

### builtin/daemon.js.j2
Built-in daemon management commands for managed lifecycle commands.

## Hook Integration

Commands integrate with user-defined hooks following these patterns:

### Standard Commands
- Hook name: `on{CommandName}` (e.g., `onBuild`, `onDeploy`)
- The hook receives an object with all command arguments and options

### Subcommands
- Hook name: `on{ParentCommand}{SubCommand}` (e.g., `onConfigGet`, `onConfigSet`)

### Managed Commands
- Export name: `{commandName}Command` (e.g., `serverCommand`)
- Must have an `execute(args)` method

## Example Usage

```javascript
// app_hooks.js
export async function onBuild({ source, output, verbose }) {
  console.log(`Building from ${source} to ${output}`);
  // Implementation here
}

export const serverCommand = {
  async execute({ port, host }) {
    console.log(`Starting server on ${host}:${port}`);
    // Daemon implementation here
  }
};
```

## Template Variables

Each template receives:
- `cmd_name`: The command name
- `cmd_data`: Command configuration object with:
  - `desc`: Command description
  - `icon`: Optional emoji icon
  - `args`: Array of argument definitions
  - `options`: Array of option definitions
  - `lifecycle`: "standard" or "managed"
  - `alias`: Optional command alias
  - `is_default`: Whether this is the default command

## Commander.js Integration

All templates generate Commander.js compatible command definitions that:
- Support command chaining
- Handle async operations
- Include proper error handling
- Pass through global options from parent commands