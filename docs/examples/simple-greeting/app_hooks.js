/**
 * Hook functions for Simple Greeting CLI - Node.js version
 */

import chalk from 'chalk';

export async function onHello(args) {
    const { name, style = 'casual', repeat = 1, verbose = false } = args;
    
    if (verbose) {
        console.log(chalk.gray(`Greeting ${name} with ${style} style, repeating ${repeat} times`));
    }
    
    // Define greeting styles with colors
    const greetings = {
        casual: chalk.blue(`Hey ${name}! 👋`),
        formal: chalk.green(`Good day, ${name}.`),
        enthusiastic: chalk.yellow.bold(`🎉 HELLO ${name.toUpperCase()}! 🎉`)
    };
    
    const greeting = greetings[style] || greetings.casual;
    
    // Repeat greeting
    for (let i = 0; i < repeat; i++) {
        if (repeat > 1) {
            console.log(chalk.cyan(`[${i + 1}]`) + ` ${greeting}`);
        } else {
            console.log(greeting);
        }
    }
}

export async function onGoodbye(args) {
    const { name, polite = false, verbose = false } = args;
    
    if (verbose) {
        console.log(chalk.gray(`Saying goodbye to ${name}, polite=${polite}`));
    }
    
    if (polite) {
        console.log(chalk.green(`It was a pleasure meeting you, ${name}. Have a wonderful day!`));
    } else {
        console.log(chalk.blue(`See you later, ${name}! 👋`));
    }
}

export async function onIntroduce(args) {
    const { name, role = 'friend', verbose = false } = args;
    
    if (verbose) {
        console.log(chalk.gray(`Introducing as ${name} (${role})`));
    }
    
    console.log(chalk.green(`Hello! My name is ${name} and I'm your ${role}. Nice to meet you!`));
}