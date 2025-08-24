// Built-in daemon management commands for Demo Node.js CLI
const chalk = require('chalk');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

class DaemonHelper {
  constructor(commandName) {
    this.commandName = commandName;
    this.pidFile = this.getPidFilePath();
  }

  getPidFilePath() {
    const runtimeDir = process.env.XDG_RUNTIME_DIR || path.join(os.tmpdir(), `${process.getuid()}`);
    return path.join(runtimeDir, `demo_js-${this.commandName}.pid`);
  }

  getPid() {
    try {
      if (fs.existsSync(this.pidFile)) {
        const pid = parseInt(fs.readFileSync(this.pidFile, 'utf8').trim());
        // Check if process is still running
        try {
          process.kill(pid, 0);
          return pid;
        } catch (e) {
          // Process not running, clean up stale PID file
          fs.unlinkSync(this.pidFile);
          return null;
        }
      }
    } catch (error) {
      return null;
    }
    return null;
  }

  isRunning() {
    return this.getPid() !== null;
  }

  stop(timeout = 10) {
    const pid = this.getPid();
    if (!pid) return true;

    try {
      // Send SIGTERM for graceful shutdown
      process.kill(pid, 'SIGTERM');
      
      // Wait for process to terminate
      const startTime = Date.now();
      while (Date.now() - startTime < timeout * 1000) {
        try {
          process.kill(pid, 0);
          // Process still running, wait a bit
          require('child_process').execSync('sleep 0.1');
        } catch (e) {
          // Process terminated
          if (fs.existsSync(this.pidFile)) {
            fs.unlinkSync(this.pidFile);
          }
          return true;
        }
      }
      
      // Force kill if still running
      process.kill(pid, 'SIGKILL');
      if (fs.existsSync(this.pidFile)) {
        fs.unlinkSync(this.pidFile);
      }
      return true;
    } catch (error) {
      return false;
    }
  }

  getDaemonStats() {
    const pid = this.getPid();
    return {
      running: pid !== null,
      pid: pid,
      pid_file: this.pidFile,
      command: this.commandName
    };
  }
}

module.exports = function(program) {
  

  return program;
};