# Simple Greeting CLI Example

This example demonstrates the basic features of Goobits CLI Framework v2.0 with a simple greeting application that works across Python, Node.js, and TypeScript.

## What This Example Teaches

- Basic CLI structure with multiple commands
- Command arguments and options
- Different option types (string, integer, flag, choices)
- Hook function implementation across languages
- Universal template usage

## Commands

### `greeting hello <name>`

Say hello to someone with various styles.

**Arguments:**
- `name` (required) - Name of person to greet

**Options:**
- `--style, -s` - Greeting style: casual, formal, enthusiastic (default: casual)
- `--repeat, -r` - Number of times to repeat greeting (default: 1)

**Examples:**
```bash
greeting hello "World"                    # Casual greeting
greeting hello "Alice" --style formal     # Formal greeting
greeting hello "Bob" -s enthusiastic -r 3 # Enthusiastic greeting, repeated 3 times
```

### `greeting goodbye <name>`

Say goodbye to someone.

**Arguments:**
- `name` (required) - Name of person to bid farewell

**Options:**
- `--polite, -p` - Use polite farewell

**Examples:**
```bash
greeting goodbye "Alice"        # Simple goodbye
greeting goodbye "Bob" --polite # Polite goodbye
```

### `greeting introduce`

Introduce yourself.

**Options:**
- `--name, -n` (required) - Your name
- `--role, -r` - Your role or title (default: "friend")

**Examples:**
```bash
greeting introduce --name "Alice"                    # Basic introduction
greeting introduce -n "Bob" -r "colleague"          # Introduction with role
```

## Usage Instructions

### Python Version

```bash
# Ensure Python language is set in goobits.yaml
language: python

# Generate CLI
goobits build --universal-templates

# Install dependencies
./setup.sh --dev

# Use the CLI
greeting --help
greeting hello "World"
greeting hello "Alice" --style formal --verbose
greeting goodbye "Bob" --polite
greeting introduce --name "Charlie" --role "developer"
```

### Node.js Version

```bash
# Set Node.js language in goobits.yaml
language: nodejs

# Generate CLI
goobits build --universal-templates

# Install dependencies (includes chalk for colors)
./setup.sh --dev

# Use the CLI
greeting --help
greeting hello "World"
greeting hello "Alice" --style enthusiastic --repeat 2
```

### TypeScript Version

```bash
# Set TypeScript language in goobits.yaml
language: typescript

# Generate CLI
goobits build --universal-templates

# Install dependencies and build
./setup.sh --dev
npm run build

# Use the CLI
node dist/index.js --help
node dist/index.js hello "World"
node dist/index.js introduce --name "TypeScript" --role "language"
```

## Expected Output

### Hello Command Examples

```bash
$ greeting hello "World"
Hey World! 👋

$ greeting hello "Alice" --style formal
Good day, Alice.

$ greeting hello "Bob" --style enthusiastic
🎉 HELLO BOB! 🎉

$ greeting hello "Charlie" --repeat 3
[1] Hey Charlie! 👋
[2] Hey Charlie! 👋
[3] Hey Charlie! 👋
```

### Goodbye Command Examples

```bash
$ greeting goodbye "Alice"
See you later, Alice! 👋

$ greeting goodbye "Bob" --polite
It was a pleasure meeting you, Bob. Have a wonderful day!
```

### Introduce Command Examples

```bash
$ greeting introduce --name "Alice"
Hello! My name is Alice and I'm your friend. Nice to meet you!

$ greeting introduce --name "Bob" --role "colleague"
Hello! My name is Bob and I'm your colleague. Nice to meet you!
```

## Performance Testing

Test the performance of your generated CLI:

```bash
# Test startup time (should be <100ms)
python ../../performance/startup_validator.py --command "python cli.py --help" --target 100

# Test memory usage
python ../../performance/memory_profiler.py --command "python cli.py hello World"

# Full performance suite
python ../../performance/performance_suite.py
```

## Key Learning Points

1. **Multi-Command Structure**: Shows how to define multiple commands in one CLI
2. **Argument Validation**: Demonstrates required arguments with descriptive help
3. **Option Types**: Examples of flag, string, integer, and choice options
4. **Cross-Language Consistency**: Same functionality across Python, Node.js, and TypeScript
5. **Universal Templates**: Single configuration generates all language versions
6. **Hook Patterns**: Clean separation between CLI structure and business logic

## Code Structure

```
simple-greeting/
├── goobits.yaml          # CLI configuration
├── app_hooks.py          # Python hook functions
├── app_hooks.js          # Node.js hook functions  
├── app_hooks.ts          # TypeScript hook functions
└── README.md            # This documentation
```

## Extension Ideas

Try extending this example:

1. **Add Configuration**: Support a config file for default greeting styles
2. **Add Validation**: Validate names (no numbers, reasonable length)
3. **Add Localization**: Support multiple languages for greetings
4. **Add History**: Remember previous greetings
5. **Add Interactive Mode**: Ask for name if not provided

## Troubleshooting

**Command not found after installation:**
```bash
# Ensure the CLI is installed properly
./setup.sh --dev
which greeting  # Should show the installed location
```

**Module import errors (Node.js):**
```bash
# Ensure chalk is installed
npm list chalk
# If missing, reinstall
npm install
```

**TypeScript compilation errors:**
```bash
# Check TypeScript configuration
npx tsc --noEmit
# Rebuild if needed
npm run build
```

This example provides a foundation for understanding Goobits CLI Framework and can be easily extended with more complex functionality.