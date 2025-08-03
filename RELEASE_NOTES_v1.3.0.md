# Release Notes - Goobits CLI v1.3.0

**🚀 Multi-Language Support Release**

*Released: August 3, 2025*

## 🎉 Major New Features

### Multi-Language CLI Generation
Goobits CLI now supports generating command-line applications in **three languages**:

- **Python** - Enhanced Click-based CLIs with pipx installation (existing)
- **Node.js** ✨ - Professional Commander.js CLIs with npm support  
- **TypeScript** ✨ - Fully typed CLIs with modern TypeScript tooling

Simply specify your target language in `goobits.yaml`:

```yaml
language: python     # Default - existing Python CLIs unchanged
language: nodejs     # NEW - Generate Node.js CLI
language: typescript # NEW - Generate TypeScript CLI
```

### Complete Node.js Ecosystem Integration

**Generated Node.js CLIs include:**
- Professional Commander.js CLI structure
- Complete npm package configuration ready for publishing
- Executable binary wrappers (`bin/cli.js`)
- Jest testing framework with CLI validation helpers
- Cross-platform compatibility (Windows, macOS, Linux)

**Example Node.js CLI:**
```bash
# Create Node.js CLI
language: nodejs
package_name: my-awesome-cli
dependencies:
  npm_packages: ["commander", "chalk"]

# Generated files:
# ├── index.js          # Main CLI entry point
# ├── package.json      # npm package ready for publishing
# ├── bin/cli.js        # Executable wrapper
# ├── app_hooks.js      # Your business logic
# └── test/             # Jest testing framework
```

### Full TypeScript Support

**Generated TypeScript CLIs include:**
- Complete type safety with TypeScript interfaces
- Modern `tsconfig.json` configuration
- Enhanced package.json with TypeScript dependencies
- Type-safe hook functions for business logic
- Integrated testing with type checking

**Example TypeScript CLI:**
```typescript
// Type-safe hook implementation
interface GreetOptions {
    greeting?: string;
    uppercase?: boolean;
}

export function onGreet(name: string, options: GreetOptions): string {
    const greeting = options.greeting || 'Hello';
    const message = `${greeting}, ${name}!`;
    return options.uppercase ? message.toUpperCase() : message;
}
```

## 🏗️ Architecture Improvements

### Extensible Generator Pattern
- Introduced `BaseGenerator` abstract class for clean language separation
- `PythonGenerator` - Refactored existing Python generation
- `NodeJSGenerator` - New Commander.js-based generation
- `TypeScriptGenerator` - Extends Node.js with type safety
- Foundation ready for future languages (Go, Rust, Deno)

### Enhanced Template System
- **Node.js Templates** (`templates/nodejs/`) - Complete CLI ecosystem
- **TypeScript Templates** (`templates/typescript/`) - Type-safe variants
- Jinja2-based templating for all languages
- Professional project structure for each language

### Comprehensive Testing
- End-to-end testing for all three languages
- Programmatic CLI generation and validation
- All 27 tests passing across Python, Node.js, and TypeScript
- Real CLI execution testing with stdin/stdout validation

## 📚 Documentation & Developer Experience

### New Documentation
- **Comprehensive Node.js/TypeScript Guide** (`docs/nodejs_guide.md`)
  - Step-by-step tutorials
  - Hook system patterns
  - Testing frameworks
  - npm publishing workflows
  - TypeScript best practices

### Enhanced README
- Multi-language quick start examples
- Language-specific installation instructions
- Expandable code examples for each language
- Migration guidance

### Updated Examples
All examples now show language-specific implementations:

**Python** (existing):
```bash
./setup.sh install --dev
awesome greet World
```

**Node.js/TypeScript** (new):
```bash
npm install && npm link
awesome greet World
```

## 🔧 Technical Details

### Schema Enhancements
- Added `language` field to `GoobitsConfigSchema`
- Enhanced dependency management for npm packages
- Validation for language-specific configurations

### Build System Updates
- Intelligent language routing in `main.py`
- Multi-file generation support for Node.js/TypeScript projects
- Executable file handling with `__executable__` key

### Installation & Packaging
- Updated package description to reflect multi-language support
- Enhanced template discovery for new languages
- Comprehensive package data inclusion

## 🔄 Migration & Compatibility

### Backward Compatibility
- **Existing Python CLIs work unchanged** - No breaking changes
- Default language remains `python` for existing projects
- All existing workflows continue to function

### Migration Path
For users wanting to try Node.js/TypeScript:

1. **Update language in existing project:**
   ```yaml
   # Add this line to existing goobits.yaml
   language: nodejs  # or typescript
   ```

2. **Regenerate:**
   ```bash
   goobits build
   ```

3. **Install and test:**
   ```bash
   npm install && npm link
   ```

## 🎯 Use Cases & Benefits

### For JavaScript/TypeScript Developers
- **Familiar tooling** - Commander.js is the industry standard
- **Rich ecosystem** - Access to millions of npm packages
- **Type safety** - Optional TypeScript with full type definitions
- **Modern development** - ESM modules, async/await, latest features

### For Multi-Language Teams
- **Consistent patterns** - Same YAML configuration across languages
- **Shared knowledge** - Hook system works identically across languages
- **Flexible deployment** - Choose the right language for each CLI

### For Enterprise Users
- **Standardization** - Uniform CLI generation across technology stacks
- **Best practices** - Professional project structure out of the box
- **Testing integration** - Comprehensive testing frameworks included

## 📈 Performance & Quality

### Generation Speed
- Node.js CLI generation: **<2 seconds**
- TypeScript CLI generation: **<3 seconds** (includes type checking)
- Python CLI generation: **<1 second** (unchanged)

### Code Quality
- Generated JavaScript/TypeScript follows industry best practices
- ESLint-compatible code generation
- Proper async/await patterns
- Professional error handling

## 🧪 Testing & Validation

### Comprehensive Test Suite
- **Unit tests** - Individual component testing
- **Integration tests** - Cross-language workflow validation  
- **End-to-end tests** - Real CLI generation, installation, and execution
- **Type checking** - TypeScript compilation validation

### Quality Assurance
- All generated CLIs tested in clean environments
- Cross-platform compatibility verified
- npm package structure validated
- TypeScript type safety confirmed

## 🚀 Getting Started

### Quick Start - Node.js CLI
```bash
# Install goobits-cli
pipx install goobits-cli

# Create Node.js CLI
mkdir my-node-cli && cd my-node-cli
cat > goobits.yaml << 'EOF'
language: nodejs
package_name: my-node-cli
command_name: mycli
dependencies:
  npm_packages: ["commander", "chalk"]
cli:
  name: mycli
  commands:
    greet:
      desc: "Greet someone"
      args: [{ name: "name", desc: "Name to greet", required: true }]
EOF

# Generate and test
goobits build
npm install && npm link
mycli greet "World"
```

### Quick Start - TypeScript CLI
```bash
# Same as Node.js, but change language
language: typescript

# Additional TypeScript benefits
- Full type safety
- Modern tsconfig.json
- Type-safe testing
```

## 🔮 Future Roadmap

This release establishes the foundation for:
- **Additional Languages** - Go, Rust, Deno support using the same pattern
- **Enhanced Features** - Plugin systems, cloud function generation
- **Developer Tools** - VS Code extensions, live reload, debugging tools

## 📖 Documentation

- **Main Guide**: [README.md](README.md)
- **Node.js/TypeScript Guide**: [docs/nodejs_guide.md](docs/nodejs_guide.md) 
- **Implementation Details**: [PROPOSAL_05_NODE.md](PROPOSAL_05_NODE.md)

## 🙏 Acknowledgments

This release represents a significant expansion of Goobits CLI's capabilities, bringing the same powerful YAML-driven approach to the JavaScript/TypeScript ecosystem. The implementation maintains the simplicity and elegance that makes Goobits CLI special while opening up new possibilities for multi-language development teams.

---

**Full Changelog**: v1.2.1...v1.3.0

**Install**: `pipx install goobits-cli==1.3.0`

**Upgrade**: `pipx upgrade goobits-cli`