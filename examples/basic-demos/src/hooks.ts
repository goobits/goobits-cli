/**
 * Hook implementations for Demo TypeScript CLI
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
import * as fs from 'fs';
import * as path from 'path';
/**
 * Greet someone with style * @param name Name to greet * @param message Custom greeting message * @param options Command options * @param options.style Greeting style * @param options.count Repeat greeting N times * @param options.uppercase Convert to uppercase * @param options.language Language code * @returns Promise<number> - Exit code (0 for success)
 */
export async function on_greet(    name: string,    message: string,    options: {        style?: string;        count?: string;        uppercase?: string;        language?: string;    }): Promise<number> {    // Implement greeting business logic with TypeScript types
    const nameValue: string = name || 'World';
    const messageValue: string = message || 'Hello';
    const style: string = options?.style || 'casual';
    const count: number = parseInt(String(options?.count)) || 1;
    const uppercase: boolean = options?.uppercase || false;
    const language: string = options?.language || 'en';
    
    // Language-specific greetings with types
    const greetings: { [key: string]: { [style: string]: string } } = {
        'en': { casual: 'Hi', formal: 'Hello', friendly: 'Hey' },
        'es': { casual: 'Hola', formal: 'Buenos días', friendly: 'Ey' },
        'fr': { casual: 'Salut', formal: 'Bonjour', friendly: 'Coucou' },
        'de': { casual: 'Hallo', formal: 'Guten Tag', friendly: 'Hey' }
    };
    
    const greetingWord: string = greetings[language]?.[style] || greetings['en'][style] || messageValue;
    let output: string = `${greetingWord}, ${nameValue}!`;
    
    if (uppercase) {
        output = output.toUpperCase();
    }
    
    // Repeat the greeting
    for (let i = 0; i < count; i++) {
        console.log(output);
    }    
    // Return 0 for success, non-zero for error
    return 0;
}
/**
 * Display system and environment information * @param options Command options * @param options.format Output format * @param options.verbose Show detailed information * @param options.sections Comma-separated sections to show * @returns Promise<number> - Exit code (0 for success)
 */
export async function on_info(    options: {        format?: string;        verbose?: string;        sections?: string;    }): Promise<number> {    // Implement system info display logic with TypeScript types
    const format: string = options?.format || 'text';
    const verbose: boolean = options?.verbose || false;
    const sections: string[] = (options?.sections || 'all').split(',').map((s: string) => s.trim());
    
    interface SystemInfo {
        system: {
            platform: string;
            arch: string;
            version: string;
            uptime: number;
        };
        environment: {
            nodeVersion: string;
            cwd: string;
            user: string;
        };
        memory: {
            used: number;
            heap: number;
            external: number;
        };
    }
    
    const info: SystemInfo = {
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
    
    const showSection = (section: string): boolean => sections.includes('all') || sections.includes(section);
    
    if (format === 'json') {
        const output: Partial<SystemInfo> = {};
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
    // Return 0 for success, non-zero for error
    return 0;
}