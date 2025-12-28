/**
 * Code Formatting Plugin (TypeScript)
 * Provides code formatting and linting capabilities across multiple languages
 */

import { spawn, exec, ChildProcessWithoutNullStreams } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs/promises';
import * as path from 'path';

const execAsync = promisify(exec);

/**
 * Supported programming languages for formatting
 */
export enum SupportedLanguage {
  TYPESCRIPT = 'typescript',
  JAVASCRIPT = 'javascript',
  PYTHON = 'python',
  RUST = 'rust',
  GO = 'go',
  JSON = 'json',
  YAML = 'yaml',
  MARKDOWN = 'markdown'
}

/**
 * Formatting tools for each language
 */
export enum FormattingTool {
  PRETTIER = 'prettier',
  ESLINT = 'eslint',
  BLACK = 'black',
  RUSTFMT = 'rustfmt',
  GOFMT = 'gofmt',
  AUTOPEP8 = 'autopep8',
  YAPF = 'yapf'
}

/**
 * Formatting configuration
 */
export interface FormattingConfig {
  tool: FormattingTool;
  options: string[];
  extensions: string[];
  configFile?: string;
}

/**
 * Formatting result
 */
export interface FormatResult {
  success: boolean;
  filePath: string;
  originalContent?: string;
  formattedContent?: string;
  errors: string[];
  warnings: string[];
  changed: boolean;
}

/**
 * File processing result
 */
export interface ProcessingResult {
  totalFiles: number;
  processedFiles: number;
  changedFiles: number;
  errorFiles: number;
  results: FormatResult[];
}

/**
 * Code Formatting Plugin
 */
export class FormatPlugin {
  private formatters: Map<SupportedLanguage, FormattingConfig> = new Map();
  private availableTools: Map<FormattingTool, boolean> = new Map();

  constructor() {
    this.initializeFormatters();
  }

  /**
   * Initialize formatting configurations for each language
   */
  private initializeFormatters(): void {
    // TypeScript/JavaScript with Prettier
    this.formatters.set(SupportedLanguage.TYPESCRIPT, {
      tool: FormattingTool.PRETTIER,
      options: ['--parser', 'typescript', '--write'],
      extensions: ['.ts', '.tsx'],
      configFile: '.prettierrc'
    });

    this.formatters.set(SupportedLanguage.JAVASCRIPT, {
      tool: FormattingTool.PRETTIER,
      options: ['--parser', 'javascript', '--write'],
      extensions: ['.js', '.jsx'],
      configFile: '.prettierrc'
    });

    // Python with Black
    this.formatters.set(SupportedLanguage.PYTHON, {
      tool: FormattingTool.BLACK,
      options: ['--line-length', '88'],
      extensions: ['.py'],
      configFile: 'pyproject.toml'
    });

    // Rust with rustfmt
    this.formatters.set(SupportedLanguage.RUST, {
      tool: FormattingTool.RUSTFMT,
      options: ['--edition', '2021'],
      extensions: ['.rs'],
      configFile: 'rustfmt.toml'
    });

    // Go with gofmt
    this.formatters.set(SupportedLanguage.GO, {
      tool: FormattingTool.GOFMT,
      options: ['-w'],
      extensions: ['.go'],
    });

    // JSON with Prettier
    this.formatters.set(SupportedLanguage.JSON, {
      tool: FormattingTool.PRETTIER,
      options: ['--parser', 'json', '--write'],
      extensions: ['.json'],
      configFile: '.prettierrc'
    });

    // YAML with Prettier
    this.formatters.set(SupportedLanguage.YAML, {
      tool: FormattingTool.PRETTIER,
      options: ['--parser', 'yaml', '--write'],
      extensions: ['.yaml', '.yml'],
      configFile: '.prettierrc'
    });

    // Markdown with Prettier
    this.formatters.set(SupportedLanguage.MARKDOWN, {
      tool: FormattingTool.PRETTIER,
      options: ['--parser', 'markdown', '--write'],
      extensions: ['.md'],
      configFile: '.prettierrc'
    });
  }

  /**
   * Check availability of formatting tools
   */
  async checkToolAvailability(): Promise<Map<FormattingTool, boolean>> {
    const tools = Object.values(FormattingTool);
    
    for (const tool of tools) {
      try {
        await this.runCommand(tool, ['--version'], { timeout: 5000 });
        this.availableTools.set(tool, true);
      } catch (error) {
        this.availableTools.set(tool, false);
      }
    }

    return this.availableTools;
  }

  /**
   * Detect language from file extension
   */
  detectLanguage(filePath: string): SupportedLanguage | null {
    const ext = path.extname(filePath).toLowerCase();
    
    for (const [language, config] of this.formatters.entries()) {
      if (config.extensions.includes(ext)) {
        return language;
      }
    }

    return null;
  }

  /**
   * Format a single file
   */
  async formatFile(filePath: string, options: {
    dryRun?: boolean;
    backup?: boolean;
    language?: SupportedLanguage;
  } = {}): Promise<FormatResult> {
    const result: FormatResult = {
      success: false,
      filePath,
      errors: [],
      warnings: [],
      changed: false
    };

    try {
      // Detect language
      const language = options.language || this.detectLanguage(filePath);
      if (!language) {
        result.errors.push('Unsupported file type or language not detected');
        return result;
      }

      // Get formatter configuration
      const config = this.formatters.get(language);
      if (!config) {
        result.errors.push(`No formatter configuration for ${language}`);
        return result;
      }

      // Check if tool is available
      if (!this.availableTools.get(config.tool)) {
        result.errors.push(`Formatting tool ${config.tool} not available`);
        return result;
      }

      // Read original content
      const originalContent = await fs.readFile(filePath, 'utf-8');
      result.originalContent = originalContent;

      if (options.backup) {
        await fs.writeFile(`${filePath}.bak`, originalContent);
      }

      // Format the file
      const formatResult = await this.runFormatter(config, filePath, options.dryRun || false);
      
      if (formatResult.success) {
        // Read formatted content
        if (!options.dryRun) {
          const formattedContent = await fs.readFile(filePath, 'utf-8');
          result.formattedContent = formattedContent;
          result.changed = originalContent !== formattedContent;
        }
        
        result.success = true;
      } else {
        result.errors.push(...formatResult.errors);
      }

      return result;

    } catch (error) {
      result.errors.push(`Failed to format file: ${error.message}`);
      return result;
    }
  }

  /**
   * Format multiple files
   */
  async formatFiles(filePaths: string[], options: {
    dryRun?: boolean;
    backup?: boolean;
    parallel?: boolean;
    onProgress?: (current: number, total: number, file: string) => void;
  } = {}): Promise<ProcessingResult> {
    const result: ProcessingResult = {
      totalFiles: filePaths.length,
      processedFiles: 0,
      changedFiles: 0,
      errorFiles: 0,
      results: []
    };

    if (options.parallel) {
      // Process files in parallel
      const promises = filePaths.map(async (filePath, index) => {
        const formatResult = await this.formatFile(filePath, options);
        
        if (options.onProgress) {
          options.onProgress(index + 1, filePaths.length, filePath);
        }

        return formatResult;
      });

      result.results = await Promise.all(promises);
    } else {
      // Process files sequentially
      for (let i = 0; i < filePaths.length; i++) {
        const filePath = filePaths[i];
        const formatResult = await this.formatFile(filePath, options);
        result.results.push(formatResult);

        if (options.onProgress) {
          options.onProgress(i + 1, filePaths.length, filePath);
        }
      }
    }

    // Calculate statistics
    for (const formatResult of result.results) {
      if (formatResult.success) {
        result.processedFiles++;
        if (formatResult.changed) {
          result.changedFiles++;
        }
      } else {
        result.errorFiles++;
      }
    }

    return result;
  }

  /**
   * Format all files in a directory
   */
  async formatDirectory(dirPath: string, options: {
    recursive?: boolean;
    extensions?: string[];
    exclude?: string[];
    dryRun?: boolean;
    backup?: boolean;
    onProgress?: (current: number, total: number, file: string) => void;
  } = {}): Promise<ProcessingResult> {
    const files = await this.findFormattableFiles(dirPath, options);
    return this.formatFiles(files, options);
  }

  /**
   * Find all formattable files in a directory
   */
  async findFormattableFiles(dirPath: string, options: {
    recursive?: boolean;
    extensions?: string[];
    exclude?: string[];
  } = {}): Promise<string[]> {
    const files: string[] = [];
    const extensions = options.extensions || this.getAllSupportedExtensions();
    const exclude = options.exclude || [
      'node_modules',
      '.git',
      'target',
      '__pycache__',
      '.mypy_cache',
      'venv',
      '.venv'
    ];

    async function walkDir(currentPath: string): Promise<void> {
      const entries = await fs.readdir(currentPath, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = path.join(currentPath, entry.name);

        if (entry.isDirectory()) {
          if (options.recursive && !exclude.includes(entry.name)) {
            await walkDir(fullPath);
          }
        } else if (entry.isFile()) {
          const ext = path.extname(entry.name);
          if (extensions.includes(ext)) {
            files.push(fullPath);
          }
        }
      }
    }

    await walkDir(dirPath);
    return files;
  }

  /**
   * Get all supported file extensions
   */
  getAllSupportedExtensions(): string[] {
    const extensions: string[] = [];
    for (const config of this.formatters.values()) {
      extensions.push(...config.extensions);
    }
    return [...new Set(extensions)];
  }

  /**
   * Lint files (check formatting without changing)
   */
  async lintFiles(filePaths: string[], options: {
    fix?: boolean;
    onProgress?: (current: number, total: number, file: string) => void;
  } = {}): Promise<ProcessingResult> {
    return this.formatFiles(filePaths, {
      dryRun: !options.fix,
      onProgress: options.onProgress
    });
  }

  /**
   * Create a formatting configuration file
   */
  async createConfigFile(language: SupportedLanguage, outputDir: string): Promise<string | null> {
    const config = this.formatters.get(language);
    if (!config?.configFile) {
      return null;
    }

    const configPath = path.join(outputDir, config.configFile);
    let configContent = '';

    switch (config.tool) {
      case FormattingTool.PRETTIER:
        configContent = JSON.stringify({
          semi: true,
          trailingComma: 'es5',
          singleQuote: true,
          printWidth: 100,
          tabWidth: 2,
          useTabs: false
        }, null, 2);
        break;

      case FormattingTool.BLACK:
        configContent = `[tool.black]
line-length = 88
target-version = ['py38']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | build
  | dist
)/
'''`;
        break;

      case FormattingTool.RUSTFMT:
        configContent = `# rustfmt configuration
edition = "2021"
max_width = 100
tab_spaces = 4
newline_style = "Unix"
use_small_heuristics = "Default"
reorder_imports = true
reorder_modules = true`;
        break;

      default:
        return null;
    }

    await fs.writeFile(configPath, configContent);
    return configPath;
  }

  /**
   * Run a formatter tool
   */
  private async runFormatter(config: FormattingConfig, filePath: string, dryRun: boolean): Promise<{
    success: boolean;
    errors: string[];
  }> {
    const args = [...config.options];
    
    // Add dry-run flag if supported
    if (dryRun) {
      switch (config.tool) {
        case FormattingTool.PRETTIER:
          args.push('--check');
          break;
        case FormattingTool.BLACK:
          args.push('--check');
          break;
        case FormattingTool.RUSTFMT:
          args.push('--check');
          break;
      }
    }

    args.push(filePath);

    try {
      await this.runCommand(config.tool, args);
      return { success: true, errors: [] };
    } catch (error) {
      return { success: false, errors: [error.message] };
    }
  }

  /**
   * Run a command with timeout
   */
  private async runCommand(command: string, args: string[], options: {
    timeout?: number;
    cwd?: string;
  } = {}): Promise<{ stdout: string; stderr: string }> {
    const timeout = options.timeout || 30000;
    const cwd = options.cwd || process.cwd();

    try {
      const { stdout, stderr } = await execAsync(
        `${command} ${args.join(' ')}`,
        { timeout, cwd }
      );
      
      return { stdout, stderr };
    } catch (error) {
      throw new Error(`Command failed: ${error.message}`);
    }
  }

  /**
   * Get plugin information for marketplace
   */
  getPluginInfo() {
    return {
      name: 'code-formatter',
      version: '1.0.0',
      author: 'Goobits Framework',
      description: 'Multi-language code formatting and linting',
      language: 'typescript',
      dependencies: ['prettier', 'eslint'],
      capabilities: [
        'multi_language_formatting',
        'batch_processing',
        'dry_run_support',
        'backup_creation',
        'config_generation',
        'lint_checking'
      ],
      commands: {
        'format': 'Format files with automatic language detection',
        'format-check': 'Check formatting without making changes',
        'format-dir': 'Format all files in directory recursively',
        'format-config': 'Generate formatting configuration files'
      }
    };
  }
}

// CLI Integration hooks for Goobits
export async function onFormat(args: string[]): Promise<void> {
  const plugin = new FormatPlugin();
  
  console.log('🎨 Code Formatter');
  
  // Check tool availability
  await plugin.checkToolAvailability();
  
  if (args.length === 0) {
    console.log('❌ No files specified');
    return;
  }

  const dryRun = args.includes('--check') || args.includes('--dry-run');
  const backup = args.includes('--backup');
  const parallel = args.includes('--parallel');
  
  // Filter out flags to get file paths
  const filePaths = args.filter(arg => !arg.startsWith('--'));
  
  console.log(`📝 ${dryRun ? 'Checking' : 'Formatting'} ${filePaths.length} file(s)...`);
  
  let current = 0;
  const result = await plugin.formatFiles(filePaths, {
    dryRun,
    backup,
    parallel,
    onProgress: (curr, total, file) => {
      current = curr;
      console.log(`  [${curr}/${total}] ${path.basename(file)}`);
    }
  });
  
  console.log('\n📊 Results:');
  console.log(`  Total files: ${result.totalFiles}`);
  console.log(`  Processed: ${result.processedFiles}`);
  console.log(`  Changed: ${result.changedFiles}`);
  console.log(`  Errors: ${result.errorFiles}`);
  
  if (result.errorFiles > 0) {
    console.log('\n❌ Errors:');
    result.results
      .filter(r => !r.success)
      .forEach(r => {
        console.log(`  ${r.filePath}: ${r.errors.join(', ')}`);
      });
  }
}

export async function onFormatCheck(args: string[]): Promise<void> {
  await onFormat(['--check', ...args]);
}

export async function onFormatDir(args: string[]): Promise<void> {
  const plugin = new FormatPlugin();
  
  const dirPath = args[0] || process.cwd();
  const recursive = !args.includes('--no-recursive');
  const dryRun = args.includes('--check');
  
  console.log(`🎨 Formatting directory: ${dirPath}`);
  console.log(`📁 Recursive: ${recursive ? 'Yes' : 'No'}`);
  
  await plugin.checkToolAvailability();
  
  let current = 0;
  const result = await plugin.formatDirectory(dirPath, {
    recursive,
    dryRun,
    onProgress: (curr, total, file) => {
      current = curr;
      console.log(`  [${curr}/${total}] ${path.relative(dirPath, file)}`);
    }
  });
  
  console.log('\n📊 Results:');
  console.log(`  Total files: ${result.totalFiles}`);
  console.log(`  Processed: ${result.processedFiles}`);
  console.log(`  Changed: ${result.changedFiles}`);
  console.log(`  Errors: ${result.errorFiles}`);
}

export async function onFormatConfig(args: string[]): Promise<void> {
  const plugin = new FormatPlugin();
  
  const language = args[0] as SupportedLanguage;
  const outputDir = args[1] || process.cwd();
  
  if (!language || !Object.values(SupportedLanguage).includes(language)) {
    console.log('❌ Please specify a supported language:');
    console.log(`  ${Object.values(SupportedLanguage).join(', ')}`);
    return;
  }
  
  console.log(`⚙️  Generating ${language} formatting configuration...`);
  
  const configPath = await plugin.createConfigFile(language, outputDir);
  
  if (configPath) {
    console.log(`✅ Configuration created: ${configPath}`);
  } else {
    console.log(`❌ No configuration template available for ${language}`);
  }
}

// Example usage
if (require.main === module) {
  async function demo(): Promise<void> {
    const plugin = new FormatPlugin();
    
    console.log('Checking tool availability...');
    const availability = await plugin.checkToolAvailability();
    
    for (const [tool, available] of availability.entries()) {
      console.log(`${tool}: ${available ? '✅' : '❌'}`);
    }
    
    console.log('\nSupported extensions:', plugin.getAllSupportedExtensions());
  }
  
  demo().catch(console.error);
}