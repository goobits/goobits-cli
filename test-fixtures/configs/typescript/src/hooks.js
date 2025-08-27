/**
 * Hook implementations for test TypeScript CLI
 */
export async function on_hello() {
    console.log("Hello from TypeScript CLI!");
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
