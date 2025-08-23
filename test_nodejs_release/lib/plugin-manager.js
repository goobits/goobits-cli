/**
 * Enhanced Plugin Manager for Goobits CLI Framework
 * Provides dynamic plugin loading, discovery, and management capabilities
 */

import { readdir, stat, access } from 'fs/promises';
import { join, resolve, basename } from 'path';
import { existsSync } from 'fs';
import { execSync } from 'child_process';
import chalk from 'chalk';

// Import error handling utilities
import {
  PluginError,
  PluginNotFoundError,
  PluginLoadError,
  FileSystemError,
  ProcessError,
  handleError,
  asyncErrorHandler
} from './errors.js';

export class PluginManager {
  constructor(cli) {
    this.cli = cli;
    this.loadedPlugins = new Map();
    this.pluginDirs = this._getPluginDirectories();
    this.registry = new Map();
  }

  /**
   * Get standard plugin directories
   */
  _getPluginDirectories() {
    const userConfigDir = process.env.XDG_CONFIG_HOME || 
                         join(process.env.HOME || '', '.config');
    
    return [
      // User-specific plugin directory
      join(userConfigDir, 'goobits', 'Goobits CLI', 'plugins'),
      // Local plugin directory
      join(process.cwd(), 'plugins'),
      // Project plugin directory
      join(process.cwd(), '.goobits', 'plugins'),
      // Global npm plugins
      this._getGlobalNpmDir()
    ].filter(dir => dir);
  }

  /**
   * Get global npm directory for plugin discovery
   */
  _getGlobalNpmDir() {
    try {
      const npmRoot = execSync('npm root -g', { encoding: 'utf8' }).trim();
      return npmRoot;
    } catch (error) {
      if (process.env.DEBUG) {
        console.debug('Could not determine global npm directory:', error.message);
      }
      return null;
    }
  }

  /**
   * Discover plugins in all plugin directories
   */
  discoverPlugins = asyncErrorHandler(async function discoverPlugins() {
    const discovered = new Map();

    for (const pluginDir of this.pluginDirs) {
      try {
        if (!existsSync(pluginDir)) {
          if (process.env.DEBUG) {
            console.debug(`Plugin directory not found: ${pluginDir}`);
          }
          continue;
        }

        const entries = await readdir(pluginDir);
        
        for (const entry of entries) {
          const fullPath = join(pluginDir, entry);
          
          try {
            const stats = await stat(fullPath);

            if (stats.isDirectory()) {
              // Check for npm-style plugin (package.json)
              const packagePath = join(fullPath, 'package.json');
              if (existsSync(packagePath)) {
                try {
                  const { default: pkg } = await import(packagePath, { 
                    assert: { type: 'json' } 
                  });
                  
                  if (this._isValidPlugin(pkg)) {
                    discovered.set(entry, {
                      name: entry,
                      path: fullPath,
                      type: 'npm',
                      package: pkg,
                      entry: pkg.main || 'index.js'
                    });
                    
                    if (process.env.DEBUG) {
                      console.debug(`Found npm plugin: ${entry}`);
                    }
                  } else {
                    if (process.env.DEBUG) {
                      console.debug(`Invalid plugin package (missing keywords or main): ${entry}`);
                    }
                  }
                } catch (error) {
                  if (process.env.DEBUG) {
                    console.debug(`Invalid plugin package at ${packagePath}:`, error.message);
                  }
                }
              }
            } else if (entry.endsWith('.js') && !entry.startsWith('_')) {
              // Single file plugin
              const pluginName = entry.replace('.js', '');
              discovered.set(pluginName, {
                name: pluginName,
                path: fullPath,
                type: 'file',
                entry: entry
              });
              
              if (process.env.DEBUG) {
                console.debug(`Found file plugin: ${pluginName}`);
              }
            }
          } catch (statError) {
            if (process.env.DEBUG) {
              console.debug(`Could not stat plugin entry ${fullPath}:`, statError.message);
            }
          }
        }
      } catch (error) {
        const dirError = new FileSystemError(
          `Could not scan plugin directory ${pluginDir}: ${error.message}`,
          pluginDir,
          'read'
        );
        if (process.env.DEBUG) {
          console.debug(dirError.getUserMessage());
        }
      }
    }

    // Discover npm plugins with naming convention
    try {
      await this._discoverNpmPlugins(discovered);
    } catch (error) {
      if (process.env.DEBUG) {
        console.debug('Failed to discover npm plugins:', error.message);
      }
    }

    return discovered;
  });

  /**
   * Discover plugins from npm with naming convention
   */
  async _discoverNpmPlugins(discovered) {
    try {
      const pluginPattern = `Goobits CLI-plugin-*`;
      const globalPluginPattern = `goobits-plugin-*`;

      // Try to find plugins using npm ls
      const patterns = [pluginPattern, globalPluginPattern];
      
      for (const pattern of patterns) {
        try {
          const output = execSync(`npm ls -g --depth=0 --parseable | grep "${pattern.replace('*', '')}"`, {
            encoding: 'utf8',
            stdio: ['ignore', 'pipe', 'ignore']
          });

          const pluginPaths = output.trim().split('\n').filter(Boolean);
          
          for (const pluginPath of pluginPaths) {
            if (existsSync(pluginPath)) {
              const packagePath = join(pluginPath, 'package.json');
              if (existsSync(packagePath)) {
                try {
                  const { default: pkg } = await import(packagePath, { 
                    assert: { type: 'json' } 
                  });
                  
                  const pluginName = basename(pluginPath);
                  discovered.set(pluginName, {
                    name: pluginName,
                    path: pluginPath,
                    type: 'npm-global',
                    package: pkg,
                    entry: pkg.main || 'index.js'
                  });
                } catch (error) {
                  console.debug(`Could not load npm plugin ${pluginPath}:`, error.message);
                }
              }
            }
          }
        } catch (error) {
          // npm ls failed, skip this pattern
          console.debug(`npm plugin discovery failed for ${pattern}:`, error.message);
        }
      }
    } catch (error) {
      console.debug('npm plugin discovery failed:', error.message);
    }
  }

  /**
   * Check if a package.json represents a valid plugin
   */
  _isValidPlugin(pkg) {
    return (
      pkg.keywords && 
      (pkg.keywords.includes('Goobits CLI-plugin') || 
       pkg.keywords.includes('goobits-plugin')) &&
      (pkg.main || existsSync(join(dirname(pkg.path || ''), 'index.js')))
    );
  }

  /**
   * Load a specific plugin
   */
  loadPlugin = asyncErrorHandler(async function loadPlugin(pluginInfo) {
    try {
      if (!pluginInfo || !pluginInfo.name) {
        throw new PluginError('Invalid plugin info provided', 'unknown');
      }
      
      let pluginModule;
      
      if (pluginInfo.type === 'file') {
        if (!existsSync(pluginInfo.path)) {
          throw new PluginNotFoundError(pluginInfo.name);
        }
        pluginModule = await import(pluginInfo.path);
      } else {
        // npm-style plugin
        const entryPath = join(pluginInfo.path, pluginInfo.entry);
        if (!existsSync(entryPath)) {
          throw new PluginLoadError(pluginInfo.name, new Error(`Entry file not found: ${entryPath}`));
        }
        pluginModule = await import(entryPath);
      }

      // Validate plugin structure
      const plugin = pluginModule.default || pluginModule;
      
      if (typeof plugin === 'function') {
        // Function-style plugin
        try {
          plugin(this.cli);
          this.loadedPlugins.set(pluginInfo.name, {
            ...pluginInfo,
            module: plugin,
            type: 'function'
          });
          return true;
        } catch (registerError) {
          throw new PluginLoadError(pluginInfo.name, registerError);
        }
      } else if (plugin && plugin.register && typeof plugin.register === 'function') {
        // Object-style plugin with register method
        try {
          plugin.register(this.cli);
          this.loadedPlugins.set(pluginInfo.name, {
            ...pluginInfo,
            module: plugin,
            type: 'object'
          });
          return true;
        } catch (registerError) {
          throw new PluginLoadError(pluginInfo.name, registerError);
        }
      } else {
        throw new PluginLoadError(
          pluginInfo.name, 
          new Error('Plugin must export a function or object with register method')
        );
      }
    } catch (error) {
      if (error instanceof PluginError) {
        console.error(chalk.red(error.getUserMessage()));
        if (process.env.DEBUG) {
          console.error(error.stack);
        }
      } else {
        const pluginError = new PluginLoadError(pluginInfo.name, error);
        console.error(chalk.red(pluginError.getUserMessage()));
        if (process.env.DEBUG) {
          console.error(error.stack);
        }
      }
      return false;
    }
  });

  /**
   * Load all discovered plugins
   */
  async loadAllPlugins() {
    const discovered = await this.discoverPlugins();
    let loadedCount = 0;

    for (const [name, pluginInfo] of discovered) {
      if (await this.loadPlugin(pluginInfo)) {
        loadedCount++;
        console.debug(chalk.green(`✓ Loaded plugin: ${name}`));
      }
    }

    return loadedCount;
  }

  /**
   * Install a plugin from npm
   */
  installPlugin = asyncErrorHandler(async function installPlugin(pluginName, options = {}) {
    try {
      if (!pluginName || typeof pluginName !== 'string') {
        throw new PluginError('Invalid plugin name provided', pluginName);
      }
      
      const { global = false, version = 'latest' } = options;
      
      let installCmd = `npm install ${pluginName}@${version}`;
      if (global) {
        installCmd += ' -g';
      }

      console.log(chalk.blue(`Installing plugin: ${pluginName}`));
      
      try {
        execSync(installCmd, { stdio: 'inherit' });
      } catch (execError) {
        throw new ProcessError(
          `Failed to install plugin ${pluginName}: ${execError.message}`,
          installCmd,
          execError.status
        );
      }

      // Try to load the newly installed plugin
      const discovered = await this.discoverPlugins();
      const plugin = discovered.get(pluginName);
      
      if (plugin && await this.loadPlugin(plugin)) {
        console.log(chalk.green(`✅ Plugin ${pluginName} installed and loaded successfully`));
        return true;
      } else {
        console.warn(chalk.yellow(`Plugin ${pluginName} installed but could not be loaded. Check plugin compatibility.`));
        return false;
      }
    } catch (error) {
      if (error instanceof PluginError || error instanceof ProcessError) {
        console.error(chalk.red(error.getUserMessage()));
        if (process.env.DEBUG) {
          console.error(error.stack);
        }
      } else {
        const pluginError = new PluginError(`Failed to install plugin ${pluginName}: ${error.message}`, pluginName);
        console.error(chalk.red(pluginError.getUserMessage()));
        if (process.env.DEBUG) {
          console.error(error.stack);
        }
      }
      return false;
    }
  });

  /**
   * Uninstall a plugin
   */
  uninstallPlugin = asyncErrorHandler(async function uninstallPlugin(pluginName, options = {}) {
    try {
      if (!pluginName || typeof pluginName !== 'string') {
        throw new PluginError('Invalid plugin name provided', pluginName);
      }
      
      const { global = false } = options;
      
      let uninstallCmd = `npm uninstall ${pluginName}`;
      if (global) {
        uninstallCmd += ' -g';
      }

      console.log(chalk.blue(`Uninstalling plugin: ${pluginName}`));
      
      try {
        execSync(uninstallCmd, { stdio: 'inherit' });
      } catch (execError) {
        throw new ProcessError(
          `Failed to uninstall plugin ${pluginName}: ${execError.message}`,
          uninstallCmd,
          execError.status
        );
      }

      // Remove from loaded plugins
      this.loadedPlugins.delete(pluginName);
      
      console.log(chalk.green(`✅ Plugin ${pluginName} uninstalled successfully`));
      return true;
    } catch (error) {
      if (error instanceof PluginError || error instanceof ProcessError) {
        console.error(chalk.red(error.getUserMessage()));
        if (process.env.DEBUG) {
          console.error(error.stack);
        }
      } else {
        const pluginError = new PluginError(`Failed to uninstall plugin ${pluginName}: ${error.message}`, pluginName);
        console.error(chalk.red(pluginError.getUserMessage()));
        if (process.env.DEBUG) {
          console.error(error.stack);
        }
      }
      return false;
    }
  });

  /**
   * List all available plugins
   */
  async listPlugins() {
    const discovered = await this.discoverPlugins();
    
    return {
      discovered: Array.from(discovered.values()),
      loaded: Array.from(this.loadedPlugins.values())
    };
  }

  /**
   * Get plugin information
   */
  getPluginInfo(pluginName) {
    return this.loadedPlugins.get(pluginName);
  }

  /**
   * Check if a plugin is loaded
   */
  isPluginLoaded(pluginName) {
    return this.loadedPlugins.has(pluginName);
  }
}

export default PluginManager;