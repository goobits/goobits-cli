//! Hook system interface for Test Rust CLI
//! 
//! This module defines the interface between the generated CLI and user-defined hooks.
//! Users should implement hook functions in hooks.rs to provide business logic.

use std::collections::HashMap;
use clap::ArgMatches;

pub type HookResult = Result<(), Box<dyn std::error::Error>>;

/// Trait that all hook implementations must follow
pub trait Hook {
    fn execute(&self, args: &ArgMatches) -> HookResult;
}

/// Hook manager that handles registration and execution of hooks
pub struct HookManager  {
    hooks: HashMap<String, Box<dyn Hook>>,
}

impl HookManager {
    pub fn new() -> Self  {
        Self {
            hooks: HashMap::new(),
        }
    }

    pub fn register_hook<H: Hook + 'static>(&mut self, name: String, hook: H) {
        self.hooks.insert(name, Box::new(hook));
    }

    pub fn has_hook(&self, name: &str) -> bool  {
        self.hooks.contains_key(name)
    }

    pub fn execute_hook(&self, name: &str, args: &ArgMatches) -> HookResult  {
        match self.hooks.get(name) {
            Some(hook) => hook.execute(args),
            None => Err(format!("Hook '{}' not found", name).into()),
        }
    }

    pub fn list_hooks(&self) -> Vec<&String>  {
        self.hooks.keys().collect()
    }
}

impl Default for HookManager {
    fn default() -> Self  {
        Self::new()
    }
}

/// Generate a template hooks.rs file for the user
pub fn generate_hooks_template() -> String  {
    format!(r#"//! Hook implementations for Test Rust CLI
//! 
//! This file contains the business logic for your CLI commands.
//! Implement the hook functions below to handle your CLI commands.
//! 
//! Each command in your CLI corresponds to a hook function.

use clap::ArgMatches;
use crate::(Undefined, Undefined);

/// Say hello
pub struct HelloHook;

impl Hook for HelloHook {
    fn execute(&self, args: &ArgMatches) -> HookResult  {
        // TODO: Implement your business logic here
        println!("Hook on_hello called");        // Extract arguments        if let Some(name) = args.get_one::<String>("name") {
            println!("name: {}", name);
        }        // Extract options        if let Some(greeting) = args.get_one::<String>("greeting") {
            println!("greeting: {}", greeting);
        }        
        // Return Ok(()) for success, Err(...) for error
        Ok(())
    }}
}}
/// Initialize and register all hooks
pub fn register_hooks(manager: &mut crate::HookManager) {    manager.register_hook("on_hello".to_string(), HelloHook);}

// Add any utility functions or structures here
"#)
}

// Global hook manager
static mut HOOK_MANAGER: Option<HookManager> = None;
static INIT_HOOK_MANAGER: std::sync::Once = std::sync::Once::new();

pub fn get_hook_manager() -> &'static mut HookManager  {
    unsafe {
        INIT_HOOK_MANAGER.call_once(|| {
            HOOK_MANAGER = Some(HookManager::new());
        });
        HOOK_MANAGER.as_mut().unwrap()
    }
}

pub fn execute_hook(name: &str, args: &ArgMatches) -> HookResult  {
    get_hook_manager().execute_hook(name, args)
}

pub fn has_hook(name: &str) -> bool  {
    get_hook_manager().has_hook(name)
}