/**
 * Hook system for Test Rust CLI
 * Auto-generated from test-rust-cli.yaml
 */

use anyhow::Result;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use libloading::{Library, Symbol};
use std::path::PathBuf;
use serde::{Deserialize, Serialize};

/// Execution phase for hooks
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum ExecutionPhase {
    PreCommand,
    PostCommand,
    OnError,
    OnSuccess,
}

/// Context passed to hooks during execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HookContext {
    /// Command being executed
    pub command: String,
    /// Subcommand if any
    pub subcommand: Option<String>,
    /// Command arguments
    pub args: Vec<String>,
    /// Command options/flags
    pub options: HashMap<String, String>,
    /// Current working directory
    pub working_dir: PathBuf,
    /// Environment variables
    pub env_vars: HashMap<String, String>,
    /// Execution phase
    pub phase: String,
    /// Error message if in error phase
    pub error_message: Option<String>,
}

impl HookContext {
    pub fn new(
        command: String,
        subcommand: Option<String>,
        args: Vec<String>,
        options: HashMap<String, String>,
        phase: ExecutionPhase,
    ) -> Result<Self> {
        let working_dir = std::env::current_dir()?;
        let env_vars = std::env::vars().collect();
        
        Ok(Self {
            command,
            subcommand,
            args,
            options,
            working_dir,
            env_vars,
            phase: format!("{:?}", phase),
            error_message: None,
        })
    }
    
    pub fn with_error(mut self, error: &str) -> Self {
        self.error_message = Some(error.to_string());
        self
    }
}

/// Hook function signature
pub type HookFn = fn(&HookContext) -> Result<()>;

/// Dynamic hook from external library
pub struct DynamicHook {
    #[allow(dead_code)]
    library: Library,
    function: Symbol<'static, HookFn>,
    name: String,
}

impl DynamicHook {
    pub fn load(library_path: &str, function_name: &str) -> Result<Self> {
        unsafe {
            let library = Library::new(library_path)?;
            let function: Symbol<HookFn> = library.get(function_name.as_bytes())?;
            let function = std::mem::transmute(function);
            
            Ok(Self {
                library,
                function,
                name: function_name.to_string(),
            })
        }
    }
    
    pub fn execute(&self, context: &HookContext) -> Result<()> {
        (self.function)(context)
    }
}

/// Built-in hook implementations
pub struct BuiltinHooks;

impl BuiltinHooks {
    
    /// Pre-command hook for hello
    pub fn pre_hello(_context: &HookContext) -> Result<()> {
        // Default pre-command behavior for hello
        
        // No specific pre-command hook defined
        
        Ok(())
    }
    
    /// Post-command hook for hello
    pub fn post_hello(_context: &HookContext) -> Result<()> {
        // Default post-command behavior for hello
        
        // No specific post-command hook defined
        
        Ok(())
    }
    
    /// Pre-command hook for process
    pub fn pre_process(_context: &HookContext) -> Result<()> {
        // Default pre-command behavior for process
        
        // No specific pre-command hook defined
        
        Ok(())
    }
    
    /// Post-command hook for process
    pub fn post_process(_context: &HookContext) -> Result<()> {
        // Default post-command behavior for process
        
        // No specific post-command hook defined
        
        Ok(())
    }
    
    
    /// Global pre-command hook
    pub fn global_pre_command(context: &HookContext) -> Result<()> {
        use crate::utils::output;
        
        // Log command execution if debug mode
        if cfg!(debug_assertions) {
            output::debug(&format!("Executing command: {} {:?}", context.command, context.args));
        }
        
        // Validate working directory exists
        if !context.working_dir.exists() {
            anyhow::bail!("Working directory does not exist: {}", context.working_dir.display());
        }
        
        Ok(())
    }
    
    /// Global post-command hook
    pub fn global_post_command(context: &HookContext) -> Result<()> {
        use crate::utils::output;
        
        if cfg!(debug_assertions) {
            output::debug(&format!("Command completed: {}", context.command));
        }
        
        Ok(())
    }
    
    /// Global error hook
    pub fn global_error_handler(context: &HookContext) -> Result<()> {
        use crate::utils::output;
        
        if let Some(error) = &context.error_message {
            output::error(&format!("Command '{}' failed: {}", context.command, error));
        }
        
        Ok(())
    }
}

/// Hook registry managing all hooks
pub struct HookRegistry {
    builtin_hooks: HashMap<String, HashMap<ExecutionPhase, HookFn>>,
    dynamic_hooks: HashMap<String, HashMap<ExecutionPhase, Arc<DynamicHook>>>,
    global_hooks: HashMap<ExecutionPhase, Vec<HookFn>>,
}

impl HookRegistry {
    pub fn new() -> Self {
        let mut registry = Self {
            builtin_hooks: HashMap::new(),
            dynamic_hooks: HashMap::new(),
            global_hooks: HashMap::new(),
        };
        
        // Register built-in hooks
        registry.register_builtin_hooks();
        registry.register_global_hooks();
        
        registry
    }
    
    fn register_builtin_hooks(&mut self) {
        
        let mut hello_hooks = HashMap::new();
        hello_hooks.insert(ExecutionPhase::PreCommand, BuiltinHooks::pre_hello as HookFn);
        hello_hooks.insert(ExecutionPhase::PostCommand, BuiltinHooks::post_hello as HookFn);
        self.builtin_hooks.insert("hello".to_string(), hello_hooks);
        
        let mut process_hooks = HashMap::new();
        process_hooks.insert(ExecutionPhase::PreCommand, BuiltinHooks::pre_process as HookFn);
        process_hooks.insert(ExecutionPhase::PostCommand, BuiltinHooks::post_process as HookFn);
        self.builtin_hooks.insert("process".to_string(), process_hooks);
        
    }
    
    fn register_global_hooks(&mut self) {
        self.global_hooks.insert(ExecutionPhase::PreCommand, vec![BuiltinHooks::global_pre_command]);
        self.global_hooks.insert(ExecutionPhase::PostCommand, vec![BuiltinHooks::global_post_command]);
        self.global_hooks.insert(ExecutionPhase::OnError, vec![BuiltinHooks::global_error_handler]);
    }
    
    /// Register a dynamic hook from an external library
    pub fn register_dynamic_hook(
        &mut self,
        command: &str,
        phase: ExecutionPhase,
        library_path: &str,
        function_name: &str,
    ) -> Result<()> {
        let hook = Arc::new(DynamicHook::load(library_path, function_name)?);
        
        self.dynamic_hooks
            .entry(command.to_string())
            .or_insert_with(HashMap::new)
            .insert(phase, hook);
        
        Ok(())
    }
    
    /// Execute hooks for a command and phase
    pub fn execute_hooks(
        &self,
        command: &str,
        phase: ExecutionPhase,
        context: &HookContext,
    ) -> Result<()> {
        // Execute global hooks first
        if let Some(global_hooks) = self.global_hooks.get(&phase) {
            for hook in global_hooks {
                hook(context)?;
            }
        }
        
        // Execute built-in command-specific hooks
        if let Some(command_hooks) = self.builtin_hooks.get(command) {
            if let Some(hook) = command_hooks.get(&phase) {
                hook(context)?;
            }
        }
        
        // Execute dynamic hooks
        if let Some(dynamic_command_hooks) = self.dynamic_hooks.get(command) {
            if let Some(hook) = dynamic_command_hooks.get(&phase) {
                hook.execute(context)?;
            }
        }
        
        Ok(())
    }
    
    /// Load hooks from configuration directory
    pub fn load_hooks_from_config(&mut self, config_dir: &PathBuf) -> Result<()> {
        let hooks_dir = config_dir.join("hooks");
        if !hooks_dir.exists() {
            return Ok(());
        }
        
        // Look for hook configuration file
        let hook_config_path = hooks_dir.join("hooks.yaml");
        if hook_config_path.exists() {
            let content = std::fs::read_to_string(&hook_config_path)?;
            let hook_config: HookConfig = serde_yaml::from_str(&content)?;
            
            for (command, phases) in hook_config.hooks {
                for (phase_str, hook_def) in phases {
                    let phase = match phase_str.as_str() {
                        "pre" => ExecutionPhase::PreCommand,
                        "post" => ExecutionPhase::PostCommand,
                        "error" => ExecutionPhase::OnError,
                        "success" => ExecutionPhase::OnSuccess,
                        _ => continue,
                    };
                    
                    if let Some(library) = hook_def.library {
                        let function = hook_def.function.unwrap_or_else(|| format!("{}_hook", command));
                        self.register_dynamic_hook(&command, phase, &library, &function)?;
                    }
                }
            }
        }
        
        Ok(())
    }
}

#[derive(Debug, Deserialize)]
struct HookConfig {
    hooks: HashMap<String, HashMap<String, HookDefinition>>,
}

#[derive(Debug, Deserialize)]
struct HookDefinition {
    library: Option<String>,
    function: Option<String>,
}

/// Global hook registry instance
static HOOK_REGISTRY: Mutex<Option<HookRegistry>> = Mutex::new(None);

// Command-specific modules for hook implementations

pub mod hello {
    use anyhow::Result;
    use serde::{Deserialize, Serialize};
    
    #[derive(Debug, Clone, Serialize, Deserialize)]
    pub struct Args {
        
        pub name: String,
        
        
        
        pub greeting: Option<String>,
        
        
        
        pub verbose: bool,
        
        
    }
    
    pub fn execute(_args: Args) -> Result<()> {
        // TODO: Implement hello command logic
        
        println!("Executing hello command");
        
        Ok(())
    }
}

pub mod process {
    use anyhow::Result;
    use serde::{Deserialize, Serialize};
    
    #[derive(Debug, Clone, Serialize, Deserialize)]
    pub struct Args {
        
        pub input: String,
        
        
        
        pub output: Option<String>,
        
        
        
        pub format: Option<String>,
        
        
    }
    
    pub fn execute(_args: Args) -> Result<()> {
        // TODO: Implement process command logic
        
        println!("Executing process command");
        
        Ok(())
    }
}


/// Initialize the global hook registry
pub fn initialize_hooks(config_dir: &PathBuf) -> Result<()> {
    let mut registry = HookRegistry::new();
    registry.load_hooks_from_config(config_dir)?;
    
    let mut global_registry = HOOK_REGISTRY.lock().unwrap();
    *global_registry = Some(registry);
    
    Ok(())
}

/// Execute hooks using the global registry
pub fn execute_command_hooks(
    command: &str,
    phase: ExecutionPhase,
    context: &HookContext,
) -> Result<()> {
    let global_registry = HOOK_REGISTRY.lock().unwrap();
    if let Some(ref registry) = *global_registry {
        registry.execute_hooks(command, phase, context)?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;
    
    #[test]
    fn test_hook_context_creation() {
        let context = HookContext::new(
            "test".to_string(),
            None,
            vec!["arg1".to_string()],
            HashMap::new(),
            ExecutionPhase::PreCommand,
        ).unwrap();
        
        assert_eq!(context.command, "test");
        assert_eq!(context.phase, "PreCommand");
    }
    
    #[test]
    fn test_hook_registry() {
        let registry = HookRegistry::new();
        
        // Test that built-in hooks are registered
        
        assert!(registry.builtin_hooks.contains_key("hello"));
        
        assert!(registry.builtin_hooks.contains_key("process"));
        
        
        // Test global hooks
        assert!(registry.global_hooks.contains_key(&ExecutionPhase::PreCommand));
        assert!(registry.global_hooks.contains_key(&ExecutionPhase::PostCommand));
    }
    
    #[test]
    fn test_builtin_hooks_execution() {
        let context = HookContext::new(
            "test".to_string(),
            None,
            vec![],
            HashMap::new(),
            ExecutionPhase::PreCommand,
        ).unwrap();
        
        // Test global hooks don't panic
        assert!(BuiltinHooks::global_pre_command(&context).is_ok());
        assert!(BuiltinHooks::global_post_command(&context).is_ok());
    }
}