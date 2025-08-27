// Built-in upgrade command for Demo Node.js CLI
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

module.exports = function(program) {
  const command = program
    .command('upgrade')
    .description('Upgrade Demo Node.js CLI to the latest version')
    .option('--check', 'Check for updates without installing')
    .option('--version <version>', 'Install specific version')
    .option('--pre', 'Include pre-release versions')
    .option('--dry-run', 'Show what would be done without doing it')
    .action(async function(options) {
      const packageName = 'demo-nodejs-cli';
      const displayName = 'Demo Node.js CLI';
      const commandName = 'demo_js';
      
      try {
        // Get current version
        let currentVersion = 'unknown';
        try {
          const packageJsonPath = path.join(__dirname, '..', '..', '..', 'package.json');
          if (fs.existsSync(packageJsonPath)) {
            const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
            currentVersion = packageJson.version;
          }
        } catch (e) {
          // Ignore errors getting current version
        }
        
        console.log(`Current version: ${currentVersion}`);
        
        if (options.check) {
          console.log(`Checking for updates to ${displayName}...`);
          
          try {
            // Check latest version from npm
            const npmViewCmd = `npm view ${packageName} version`;
            const latestVersion = execSync(npmViewCmd, { encoding: 'utf8' }).trim();
            
            if (latestVersion !== currentVersion) {
              console.log(`Update available: ${currentVersion} → ${latestVersion}`);
              console.log(`Run '${commandName} upgrade' to install the latest version.`);
            } else {
              console.log(`You are already on the latest version (${currentVersion}).`);
            }
          } catch (error) {
            console.log('Update check failed. Please check your internet connection.');
          }
          return;
        }
        
        // Build the upgrade command
        let cmd;
        const isGloballyInstalled = process.env.npm_config_global === 'true' || 
                                  process.argv[1].includes(path.join('npm', 'bin')) ||
                                  process.argv[1].includes(path.join('.npm-global', 'bin'));
        
        if (isGloballyInstalled) {
          console.log(`Upgrading ${displayName} globally with npm...`);
          cmd = ['npm', 'install', '-g'];
        } else {
          console.log(`Upgrading ${displayName} locally with npm...`);
          cmd = ['npm', 'install'];
        }
        
        if (options.version) {
          cmd.push(`${packageName}@${options.version}`);
        } else {
          cmd.push(`${packageName}@latest`);
          if (options.pre) {
            cmd.push('--tag', 'next');
          }
        }
        
        if (options.dryRun) {
          console.log(`Dry run - would execute: ${cmd.join(' ')}`);
          return;
        }
        
        // Execute upgrade
        console.log('Upgrading...');
        try {
          execSync(cmd.join(' '), { stdio: 'inherit' });
          console.log(`✅ ${displayName} upgraded successfully!`);
          console.log(`Run '${commandName} --version' to verify the new version.`);
        } catch (error) {
          console.error(`❌ Upgrade failed with exit code ${error.status || 1}`);
          process.exit(1);
        }
      } catch (error) {
        console.error('Error during upgrade:', error.message);
        process.exit(1);
      }
    });

  return command;
};