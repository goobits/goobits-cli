/**
 * Hook implementations for test Node.js CLI
 */

export async function on_hello() {
    console.log("Hello from Node.js CLI!");
}

export async function on_build() {
    console.log("Build command executed!");
}

export async function on_project() {
    console.log("Building project...");
}

export async function on_serve() {
    console.log("Starting server...");
}