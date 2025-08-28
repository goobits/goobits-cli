/**
 * Hook implementations for Multi-Language Test CLI
 * 
 * This file contains the business logic for your CLI commands.
 * Implement the hook functions below to handle your CLI commands.
 * 
 * IMPORTANT: Hook names must use snake_case with 'on_' prefix
 * Example:
 * - Command 'hello' -> Hook function 'on_hello'
 * - Command 'hello-world' -> Hook function 'on_hello_world'
 */

// Import any modules you need here
import fs from 'fs';
import path from 'path';
/**
 * Greet someone * @param {string} name - Name to greet * @param {Object} options - Command options * @param {bool} options.enthusiastic - Be enthusiastic * @returns {Promise<number>} - Exit code (0 for success)
 */
async function on_greet(name, options) {    // Implement greeting business logic
    const nameValue = name || 'World';
    const messageValue = message || 'Hello';
    const style = options?.style || 'casual';
    const count = parseInt(options?.count) || 1;
    const uppercase = options?.uppercase || false;
    const language = options?.language || 'en';
    
    // Language-specific greetings
    const greetings = {
        'en': { casual: 'Hi', formal: 'Hello', friendly: 'Hey' },
        'es': { casual: 'Hola', formal: 'Buenos días', friendly: 'Ey' },
        'fr': { casual: 'Salut', formal: 'Bonjour', friendly: 'Coucou' },
        'de': { casual: 'Hallo', formal: 'Guten Tag', friendly: 'Hey' }
    };
    
    const greetingWord = greetings[language]?.[style] || greetings['en'][style] || messageValue;
    let output = `${greetingWord}, ${nameValue}!`;
    
    if (uppercase) {
        output = output.toUpperCase();
    }
    
    // Repeat the greeting
    for (let i = 0; i < count; i++) {
        console.log(output);
    }    
    return 0;
}
/**
 * Show information * @param {Object} options - Command options * @param {bool} options.verbose - Verbose output * @returns {Promise<number>} - Exit code (0 for success)
 */
async function on_info(options) {    // Implement system info display logic
    const format = options?.format || 'text';
    const verbose = options?.verbose || false;
    const sections = (options?.sections || 'all').split(',').map(s => s.trim());
    
    const info = {
        system: {
            platform: process.platform,
            arch: process.arch,
            version: process.version,
            uptime: Math.floor(process.uptime())
        },
        environment: {
            nodeVersion: process.version,
            cwd: process.cwd(),
            user: process.env.USER || process.env.USERNAME || 'unknown'
        },
        memory: {
            used: Math.round(process.memoryUsage().rss / 1024 / 1024),
            heap: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
            external: Math.round(process.memoryUsage().external / 1024 / 1024)
        }
    };
    
    const showSection = (section) => sections.includes('all') || sections.includes(section);
    
    if (format === 'json') {
        const output = {};
        if (showSection('system')) output.system = info.system;
        if (showSection('environment')) output.environment = info.environment;
        if (showSection('memory')) output.memory = info.memory;
        console.log(JSON.stringify(output, null, verbose ? 2 : 0));
    } else {
        console.log('System Information:');
        
        if (showSection('system')) {
            console.log('\n📱 System:');
            console.log(`  Platform: ${info.system.platform}`);
            console.log(`  Architecture: ${info.system.arch}`);
            console.log(`  Node.js: ${info.system.version}`);
            if (verbose) console.log(`  Uptime: ${info.system.uptime}s`);
        }
        
        if (showSection('environment')) {
            console.log('\n🌍 Environment:');
            console.log(`  Working Directory: ${info.environment.cwd}`);
            console.log(`  User: ${info.environment.user}`);
            if (verbose) console.log(`  Node Version: ${info.environment.nodeVersion}`);
        }
        
        if (showSection('memory')) {
            console.log('\n💾 Memory Usage:');
            console.log(`  RSS: ${info.memory.used}MB`);
            console.log(`  Heap Used: ${info.memory.heap}MB`);
            if (verbose) console.log(`  External: ${info.memory.external}MB`);
        }
    }    
    return 0;
}
// Export all hook functions
export {    on_greet,    on_info,};