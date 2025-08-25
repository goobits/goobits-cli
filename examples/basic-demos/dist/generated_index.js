import { Command } from 'commander';
import chalk from 'chalk';
import * as hooks from './src/hooks.js';
const program = new Command();
export function cli() {
    program
        .name('demo_ts')
        .description('A sample TypeScript CLI built with Goobits')
        .version('1.0.0');
    program
        .command('greet')
        .description('Greet someone with style')
        .argument('<name>', 'Name to greet')
        .argument('[message]', 'Custom greeting message')
        .option('-s, --style <str>', 'Greeting style', 'casual')
        .option('-c, --count <int>', 'Repeat greeting N times', '1')
        .option('-u, --uppercase', 'Convert to uppercase', 'False')
        .option('-l, --language <str>', 'Language code', 'en')
        .action(async (name, message, options) => {
        const args = {
            commandName: 'greet',
            rawArgs: options,
            name,
            message,
        };
        try {
            const hookName = 'onGreet';
            if (hooks && typeof hooks[hookName] === 'function') {
                await hooks[hookName](args);
            }
            else {
                console.log(chalk.blue(`Executing greet command...`));
                console.log(`  name:`, name);
                console.log(`  message:`, message);
                console.log('Options:', options);
            }
        }
        catch (error) {
            console.error(chalk.red(`Error executing greet:`), error);
            process.exit(1);
        }
    });
    program
        .command('info')
        .description('Display system and environment information')
        .option('-f, --format <str>', 'Output format', 'text')
        .option('-v, --verbose', 'Show detailed information', 'False')
        .option('-s, --sections <str>', 'Comma-separated sections to show', 'all')
        .action(async (options) => {
        const args = {
            commandName: 'info',
            rawArgs: options,
        };
        try {
            const hookName = 'onInfo';
            if (hooks && typeof hooks[hookName] === 'function') {
                await hooks[hookName](args);
            }
            else {
                console.log(chalk.blue(`Executing info command...`));
                console.log('Options:', options);
            }
        }
        catch (error) {
            console.error(chalk.red(`Error executing info:`), error);
            process.exit(1);
        }
    });
    program.parse(process.argv);
    if (!process.argv.slice(2).length) {
        program.outputHelp();
    }
}
export default cli;
//# sourceMappingURL=generated_index.js.map