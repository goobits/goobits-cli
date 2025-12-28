/**
 * Docker Management Plugin (Node.js)
 * Provides Docker container and image management capabilities
 */

const { spawn, exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs').promises;
const path = require('path');

const execAsync = promisify(exec);

/**
 * Docker container status enumeration
 */
const ContainerStatus = {
  RUNNING: 'running',
  STOPPED: 'stopped',
  PAUSED: 'paused',
  RESTARTING: 'restarting',
  DEAD: 'dead'
};

/**
 * Docker container information
 */
class ContainerInfo {
  constructor(data) {
    this.id = data.id || data.ID;
    this.name = data.name || data.Names;
    this.image = data.image || data.Image;
    this.status = data.status || data.Status;
    this.state = data.state || data.State;
    this.ports = data.ports || data.Ports || [];
    this.created = data.created || data.Created;
    this.command = data.command || data.Command;
  }

  isRunning() {
    return this.state === ContainerStatus.RUNNING;
  }

  getFormattedPorts() {
    if (!this.ports || this.ports.length === 0) return 'None';
    return this.ports.map(port => {
      if (port.PublicPort && port.PrivatePort) {
        return `${port.PublicPort}:${port.PrivatePort}`;
      }
      return port.PrivatePort || port;
    }).join(', ');
  }
}

/**
 * Docker image information
 */
class ImageInfo {
  constructor(data) {
    this.id = data.id || data.ID;
    this.repository = data.repository || data.Repository;
    this.tag = data.tag || data.Tag;
    this.size = data.size || data.Size;
    this.created = data.created || data.Created;
  }

  getFullName() {
    return this.tag === '<none>' ? this.id.substring(0, 12) : `${this.repository}:${this.tag}`;
  }

  getFormattedSize() {
    if (typeof this.size === 'string') return this.size;
    
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = this.size;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)}${units[unitIndex]}`;
  }
}

/**
 * Docker Management Plugin
 */
class DockerPlugin {
  constructor(dockerPath = 'docker') {
    this.dockerPath = dockerPath;
    this.isDockerAvailable = false;
  }

  /**
   * Initialize the plugin and check Docker availability
   */
  async initialize() {
    try {
      await this.runDockerCommand(['--version']);
      this.isDockerAvailable = true;
      return true;
    } catch (error) {
      this.isDockerAvailable = false;
      return false;
    }
  }

  /**
   * Check if Docker daemon is running
   */
  async isDaemonRunning() {
    try {
      await this.runDockerCommand(['info'], { timeout: 5000 });
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * List all containers
   */
  async listContainers(all = false) {
    const args = ['ps', '--format', 'json'];
    if (all) args.push('--all');

    try {
      const result = await this.runDockerCommand(args);
      const containers = result.stdout
        .split('\n')
        .filter(line => line.trim())
        .map(line => {
          try {
            const data = JSON.parse(line);
            return new ContainerInfo(data);
          } catch (e) {
            return null;
          }
        })
        .filter(container => container !== null);

      return containers;
    } catch (error) {
      console.error('Failed to list containers:', error.message);
      return [];
    }
  }

  /**
   * List all images
   */
  async listImages() {
    try {
      const result = await this.runDockerCommand(['images', '--format', 'json']);
      const images = result.stdout
        .split('\n')
        .filter(line => line.trim())
        .map(line => {
          try {
            const data = JSON.parse(line);
            return new ImageInfo(data);
          } catch (e) {
            return null;
          }
        })
        .filter(image => image !== null);

      return images;
    } catch (error) {
      console.error('Failed to list images:', error.message);
      return [];
    }
  }

  /**
   * Start a container
   */
  async startContainer(containerIdOrName) {
    try {
      await this.runDockerCommand(['start', containerIdOrName]);
      return true;
    } catch (error) {
      console.error(`Failed to start container ${containerIdOrName}:`, error.message);
      return false;
    }
  }

  /**
   * Stop a container
   */
  async stopContainer(containerIdOrName, timeout = 10) {
    try {
      await this.runDockerCommand(['stop', '--time', timeout.toString(), containerIdOrName]);
      return true;
    } catch (error) {
      console.error(`Failed to stop container ${containerIdOrName}:`, error.message);
      return false;
    }
  }

  /**
   * Remove a container
   */
  async removeContainer(containerIdOrName, force = false) {
    const args = ['rm'];
    if (force) args.push('--force');
    args.push(containerIdOrName);

    try {
      await this.runDockerCommand(args);
      return true;
    } catch (error) {
      console.error(`Failed to remove container ${containerIdOrName}:`, error.message);
      return false;
    }
  }

  /**
   * Pull an image
   */
  async pullImage(imageName, onProgress = null) {
    return new Promise((resolve, reject) => {
      const process = spawn(this.dockerPath, ['pull', imageName]);
      
      let output = '';
      let errorOutput = '';

      process.stdout.on('data', (data) => {
        const text = data.toString();
        output += text;
        if (onProgress) {
          onProgress(text);
        }
      });

      process.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });

      process.on('close', (code) => {
        if (code === 0) {
          resolve({ success: true, output });
        } else {
          reject(new Error(`Failed to pull image: ${errorOutput}`));
        }
      });

      process.on('error', (error) => {
        reject(error);
      });
    });
  }

  /**
   * Build an image from Dockerfile
   */
  async buildImage(dockerfilePath, tag, context = '.', onProgress = null) {
    return new Promise((resolve, reject) => {
      const args = ['build', '-f', dockerfilePath, '-t', tag, context];
      const process = spawn(this.dockerPath, args);
      
      let output = '';
      let errorOutput = '';

      process.stdout.on('data', (data) => {
        const text = data.toString();
        output += text;
        if (onProgress) {
          onProgress(text);
        }
      });

      process.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });

      process.on('close', (code) => {
        if (code === 0) {
          resolve({ success: true, output });
        } else {
          reject(new Error(`Failed to build image: ${errorOutput}`));
        }
      });

      process.on('error', (error) => {
        reject(error);
      });
    });
  }

  /**
   * Run a container
   */
  async runContainer(imageName, options = {}) {
    const args = ['run'];
    
    if (options.detached) args.push('-d');
    if (options.interactive) args.push('-i');
    if (options.tty) args.push('-t');
    if (options.rm) args.push('--rm');
    if (options.name) args.push('--name', options.name);
    
    if (options.ports) {
      options.ports.forEach(port => {
        args.push('-p', port);
      });
    }
    
    if (options.environment) {
      Object.entries(options.environment).forEach(([key, value]) => {
        args.push('-e', `${key}=${value}`);
      });
    }
    
    if (options.volumes) {
      options.volumes.forEach(volume => {
        args.push('-v', volume);
      });
    }
    
    args.push(imageName);
    
    if (options.command) {
      if (Array.isArray(options.command)) {
        args.push(...options.command);
      } else {
        args.push(options.command);
      }
    }

    try {
      const result = await this.runDockerCommand(args);
      return {
        success: true,
        containerId: result.stdout.trim(),
        output: result.stdout
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get container logs
   */
  async getContainerLogs(containerIdOrName, options = {}) {
    const args = ['logs'];
    
    if (options.follow) args.push('-f');
    if (options.timestamps) args.push('-t');
    if (options.tail) args.push('--tail', options.tail.toString());
    if (options.since) args.push('--since', options.since);
    
    args.push(containerIdOrName);

    try {
      const result = await this.runDockerCommand(args);
      return result.stdout;
    } catch (error) {
      console.error(`Failed to get logs for ${containerIdOrName}:`, error.message);
      return '';
    }
  }

  /**
   * Execute command in running container
   */
  async execInContainer(containerIdOrName, command, options = {}) {
    const args = ['exec'];
    
    if (options.interactive) args.push('-i');
    if (options.tty) args.push('-t');
    if (options.detached) args.push('-d');
    if (options.user) args.push('-u', options.user);
    if (options.workdir) args.push('-w', options.workdir);
    
    args.push(containerIdOrName);
    
    if (Array.isArray(command)) {
      args.push(...command);
    } else {
      args.push('sh', '-c', command);
    }

    try {
      const result = await this.runDockerCommand(args);
      return {
        success: true,
        output: result.stdout,
        error: result.stderr
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get Docker system information
   */
  async getSystemInfo() {
    try {
      const result = await this.runDockerCommand(['system', 'info', '--format', 'json']);
      return JSON.parse(result.stdout);
    } catch (error) {
      console.error('Failed to get system info:', error.message);
      return null;
    }
  }

  /**
   * Clean up unused resources
   */
  async cleanup(options = {}) {
    const results = {};
    
    if (options.containers !== false) {
      try {
        const result = await this.runDockerCommand(['container', 'prune', '-f']);
        results.containers = result.stdout;
      } catch (error) {
        results.containers = `Error: ${error.message}`;
      }
    }
    
    if (options.images !== false) {
      try {
        const result = await this.runDockerCommand(['image', 'prune', '-f']);
        results.images = result.stdout;
      } catch (error) {
        results.images = `Error: ${error.message}`;
      }
    }
    
    if (options.volumes !== false) {
      try {
        const result = await this.runDockerCommand(['volume', 'prune', '-f']);
        results.volumes = result.stdout;
      } catch (error) {
        results.volumes = `Error: ${error.message}`;
      }
    }
    
    if (options.networks !== false) {
      try {
        const result = await this.runDockerCommand(['network', 'prune', '-f']);
        results.networks = result.stdout;
      } catch (error) {
        results.networks = `Error: ${error.message}`;
      }
    }
    
    return results;
  }

  /**
   * Run a Docker command
   */
  async runDockerCommand(args, options = {}) {
    const timeout = options.timeout || 30000;
    
    try {
      const { stdout, stderr } = await execAsync(
        `${this.dockerPath} ${args.join(' ')}`, 
        { timeout }
      );
      
      return { stdout, stderr };
    } catch (error) {
      throw new Error(`Docker command failed: ${error.message}`);
    }
  }

  /**
   * Get plugin information for marketplace
   */
  getPluginInfo() {
    return {
      name: 'docker-management',
      version: '1.0.0',
      author: 'Goobits Framework',
      description: 'Docker container and image management',
      language: 'nodejs',
      dependencies: [],
      capabilities: [
        'container_management',
        'image_management',
        'build_operations',
        'log_viewing',
        'system_monitoring',
        'cleanup_operations'
      ],
      commands: {
        'docker-ps': 'List containers with enhanced formatting',
        'docker-images': 'List images with size information',
        'docker-quick-run': 'Quick container run with common options',
        'docker-cleanup': 'Clean up unused Docker resources',
        'docker-logs': 'View container logs with filtering'
      }
    };
  }
}

// CLI Integration hooks for Goobits
async function onDockerPs(args) {
  const plugin = new DockerPlugin();
  
  if (!await plugin.initialize()) {
    console.log('❌ Docker not available');
    return;
  }
  
  if (!await plugin.isDaemonRunning()) {
    console.log('❌ Docker daemon not running');
    return;
  }
  
  console.log('🐳 Docker Containers:');
  
  const showAll = args.includes('--all') || args.includes('-a');
  const containers = await plugin.listContainers(showAll);
  
  if (containers.length === 0) {
    console.log('  No containers found');
    return;
  }
  
  containers.forEach(container => {
    const statusIcon = container.isRunning() ? '🟢' : '🔴';
    console.log(`  ${statusIcon} ${container.name}`);
    console.log(`     Image: ${container.image}`);
    console.log(`     Status: ${container.status}`);
    console.log(`     Ports: ${container.getFormattedPorts()}`);
    console.log('');
  });
}

async function onDockerImages(args) {
  const plugin = new DockerPlugin();
  
  if (!await plugin.initialize()) {
    console.log('❌ Docker not available');
    return;
  }
  
  console.log('📦 Docker Images:');
  
  const images = await plugin.listImages();
  
  if (images.length === 0) {
    console.log('  No images found');
    return;
  }
  
  images.forEach(image => {
    console.log(`  🏷️  ${image.getFullName()}`);
    console.log(`     Size: ${image.getFormattedSize()}`);
    console.log(`     Created: ${image.created}`);
    console.log('');
  });
}

async function onDockerQuickRun(args) {
  const plugin = new DockerPlugin();
  
  if (!await plugin.initialize()) {
    console.log('❌ Docker not available');
    return;
  }
  
  if (args.length === 0) {
    console.log('❌ Image name required');
    return;
  }
  
  const imageName = args[0];
  console.log(`🚀 Running container from ${imageName}...`);
  
  const result = await plugin.runContainer(imageName, {
    detached: true,
    rm: true,
    interactive: false
  });
  
  if (result.success) {
    console.log(`✅ Container started: ${result.containerId.substring(0, 12)}`);
  } else {
    console.log(`❌ Failed to start container: ${result.error}`);
  }
}

async function onDockerCleanup(args) {
  const plugin = new DockerPlugin();
  
  if (!await plugin.initialize()) {
    console.log('❌ Docker not available');
    return;
  }
  
  console.log('🧹 Cleaning up Docker resources...');
  
  const results = await plugin.cleanup();
  
  Object.entries(results).forEach(([resource, result]) => {
    console.log(`  ${resource}: ${result}`);
  });
  
  console.log('✅ Cleanup complete!');
}

async function onDockerLogs(args) {
  const plugin = new DockerPlugin();
  
  if (!await plugin.initialize()) {
    console.log('❌ Docker not available');
    return;
  }
  
  if (args.length === 0) {
    console.log('❌ Container name or ID required');
    return;
  }
  
  const containerName = args[0];
  console.log(`📄 Logs for ${containerName}:`);
  
  const logs = await plugin.getContainerLogs(containerName, {
    tail: 50,
    timestamps: true
  });
  
  if (logs) {
    console.log(logs);
  } else {
    console.log('❌ No logs found or container not accessible');
  }
}

// Export for use in other modules
module.exports = {
  DockerPlugin,
  ContainerInfo,
  ImageInfo,
  ContainerStatus,
  onDockerPs,
  onDockerImages,
  onDockerQuickRun,
  onDockerCleanup,
  onDockerLogs
};

// Example usage
if (require.main === module) {
  async function demo() {
    const plugin = new DockerPlugin();
    
    if (await plugin.initialize()) {
      console.log('Docker plugin initialized successfully');
      
      const containers = await plugin.listContainers();
      console.log(`Found ${containers.length} containers`);
      
      const images = await plugin.listImages();
      console.log(`Found ${images.length} images`);
    } else {
      console.log('Docker not available');
    }
  }
  
  demo().catch(console.error);
}