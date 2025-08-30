"""
Language Adapters
=================

Language-specific adapters for generating progress management code.
Each adapter generates equivalent progress functionality for its target language.
"""

from typing import Dict, Any, List, Optional
from ..universal.language_adapters import LanguageAdapter


class PythonProgressAdapter(LanguageAdapter):
    """Python adapter for progress management code generation."""
    
    def generate_imports(self, config: Dict[str, Any]) -> str:
        """Generate Python imports for progress management."""
        imports = [
            "import sys",
            "import time",
            "from typing import Optional, Any",
            "from contextlib import contextmanager",
        ]
        
        # Add Rich imports if configured
        if config.get('use_rich', True):
            imports.extend([
                "",
                "try:",
                "    from rich.progress import Progress, BarColumn, TextColumn",
                "    from rich.console import Console",
                "    from rich.status import Status",
                "    HAS_RICH = True",
                "except ImportError:",
                "    HAS_RICH = False"
            ])
        
        return "\n".join(imports)
    
    def generate_progress_manager_class(self, config: Dict[str, Any]) -> str:
        """Generate Python progress manager class."""
        class_code = '''class ProgressManager:
    """Progress management with Rich integration and fallback support."""
    
    def __init__(self, use_rich=True):
        self.use_rich = use_rich and globals().get('HAS_RICH', False)
        self.console = Console() if self.use_rich else None
    
    @contextmanager
    def spinner(self, text="Processing..."):
        """Context manager for spinner display."""
        if self.use_rich and self.console:
            with self.console.status(f"[bold blue]{text}") as status:
                try:
                    yield status
                    self.console.print(f"[green]{text} ✓[/green]")
                except Exception:
                    self.console.print(f"[red]{text} ✗[/red]")
                    raise
        else:
            print(f"{text}", end="", flush=True)
            try:
                yield None
                print(" ✓")
            except Exception:
                print(" ✗")
                raise
    
    @contextmanager
    def progress_bar(self, description="Processing...", total=None):
        """Context manager for progress bar display."""
        if self.use_rich and self.console:
            with Progress(console=self.console) as progress:
                task_id = progress.add_task(description, total=total)
                yield progress, task_id
        else:
            print(f"{description}")
            
            class FallbackProgress:
                def __init__(self):
                    self.current = 0
                    self.total = total or 100
                
                def update(self, task_id, advance=1):
                    self.current += advance
                    if self.total > 0:
                        pct = min(100, (self.current / self.total) * 100)
                        print(f"\\rProgress: {pct:.1f}%", end="", flush=True)
                
                def add_task(self, desc, total=None):
                    return "fallback"
            
            progress = FallbackProgress()
            try:
                yield progress, "fallback"
            finally:
                print()'''
        
        return class_code
    
    def generate_convenience_functions(self, config: Dict[str, Any]) -> str:
        """Generate Python convenience functions."""
        return '''
# Global instance
_progress_manager = None

def get_progress_manager():
    """Get global progress manager instance."""
    global _progress_manager
    if _progress_manager is None:
        _progress_manager = ProgressManager()
    return _progress_manager

def spinner(text="Processing..."):
    """Get spinner context manager."""
    return get_progress_manager().spinner(text)

def progress_bar(description="Processing...", total=None):
    """Get progress bar context manager."""
    return get_progress_manager().progress_bar(description, total)
'''


class NodeJSProgressAdapter(LanguageAdapter):
    """Node.js adapter for progress management code generation."""
    
    def generate_imports(self, config: Dict[str, Any]) -> str:
        """Generate Node.js imports for progress management."""
        return '''const { performance } = require('perf_hooks');

// Optional chalk for colors
let chalk;
try {
    chalk = require('chalk');
} catch (error) {
    chalk = {
        green: (text) => text,
        red: (text) => text,
        blue: (text) => text
    };
}'''
    
    def generate_progress_manager_class(self, config: Dict[str, Any]) -> str:
        """Generate Node.js progress manager class."""
        return '''class ProgressManager {
    constructor() {
        this.spinnerFrames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
        this.currentFrame = 0;
    }
    
    async spinner(text = 'Processing...', operation) {
        const spinnerInterval = setInterval(() => {
            process.stdout.write(`\\r${this.spinnerFrames[this.currentFrame]} ${text}`);
            this.currentFrame = (this.currentFrame + 1) % this.spinnerFrames.length;
        }, 100);
        
        try {
            const result = await operation();
            clearInterval(spinnerInterval);
            process.stdout.write(`\\r${chalk.green('✓')} ${text}\\n`);
            return result;
        } catch (error) {
            clearInterval(spinnerInterval);
            process.stdout.write(`\\r${chalk.red('✗')} ${text}\\n`);
            throw error;
        }
    }
    
    async progressBar(description = 'Processing...', total = 100, operation) {
        let current = 0;
        console.log(description);
        
        const updateProgress = (advance = 1) => {
            current += advance;
            const percentage = Math.min(100, (current / total) * 100);
            const barLength = 40;
            const filledLength = Math.floor((percentage / 100) * barLength);
            const bar = '█'.repeat(filledLength) + '░'.repeat(barLength - filledLength);
            process.stdout.write(`\\r[${bar}] ${percentage.toFixed(1)}%`);
        };
        
        try {
            const result = await operation(updateProgress);
            process.stdout.write('\\n');
            return result;
        } catch (error) {
            process.stdout.write(' ✗\\n');
            throw error;
        }
    }
}'''
    
    def generate_convenience_functions(self, config: Dict[str, Any]) -> str:
        """Generate Node.js convenience functions."""
        return '''
// Global instance
let _progressManager = null;

function getProgressManager() {
    if (!_progressManager) {
        _progressManager = new ProgressManager();
    }
    return _progressManager;
}

async function spinner(text = 'Processing...', operation) {
    return getProgressManager().spinner(text, operation);
}

async function progressBar(description = 'Processing...', total = 100, operation) {
    return getProgressManager().progressBar(description, total, operation);
}

module.exports = {
    ProgressManager,
    getProgressManager,
    spinner,
    progressBar
};'''


class TypeScriptProgressAdapter(LanguageAdapter):
    """TypeScript adapter for progress management code generation."""
    
    def generate_imports(self, config: Dict[str, Any]) -> str:
        """Generate TypeScript imports for progress management."""
        return '''import { performance } from 'perf_hooks';

// Optional chalk for colors
let chalk: any;
try {
    chalk = require('chalk');
} catch (error) {
    chalk = {
        green: (text: string) => text,
        red: (text: string) => text,
        blue: (text: string) => text
    };
}

type ProgressCallback = (advance?: number) => void;
type ProgressOperation<T> = (updateProgress?: ProgressCallback) => Promise<T>;'''
    
    def generate_progress_manager_class(self, config: Dict[str, Any]) -> str:
        """Generate TypeScript progress manager class."""
        return '''export class ProgressManager {
    private spinnerFrames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
    private currentFrame = 0;
    
    public async spinner<T>(text: string = 'Processing...', operation: () => Promise<T>): Promise<T> {
        const spinnerInterval = setInterval(() => {
            process.stdout.write(`\\r${this.spinnerFrames[this.currentFrame]} ${text}`);
            this.currentFrame = (this.currentFrame + 1) % this.spinnerFrames.length;
        }, 100);
        
        try {
            const result = await operation();
            clearInterval(spinnerInterval);
            process.stdout.write(`\\r${chalk.green('✓')} ${text}\\n`);
            return result;
        } catch (error) {
            clearInterval(spinnerInterval);
            process.stdout.write(`\\r${chalk.red('✗')} ${text}\\n`);
            throw error;
        }
    }
    
    public async progressBar<T>(
        description: string = 'Processing...',
        total: number = 100,
        operation: ProgressOperation<T>
    ): Promise<T> {
        let current = 0;
        console.log(description);
        
        const updateProgress = (advance: number = 1) => {
            current += advance;
            const percentage = Math.min(100, (current / total) * 100);
            const barLength = 40;
            const filledLength = Math.floor((percentage / 100) * barLength);
            const bar = '█'.repeat(filledLength) + '░'.repeat(barLength - filledLength);
            process.stdout.write(`\\r[${bar}] ${percentage.toFixed(1)}%`);
        };
        
        try {
            const result = await operation(updateProgress);
            process.stdout.write('\\n');
            return result;
        } catch (error) {
            process.stdout.write(' ✗\\n');
            throw error;
        }
    }
}'''
    
    def generate_convenience_functions(self, config: Dict[str, Any]) -> str:
        """Generate TypeScript convenience functions."""
        return '''
// Global instance
let _progressManager: ProgressManager | null = null;

export function getProgressManager(): ProgressManager {
    if (!_progressManager) {
        _progressManager = new ProgressManager();
    }
    return _progressManager;
}

export async function spinner<T>(text: string = 'Processing...', operation: () => Promise<T>): Promise<T> {
    return getProgressManager().spinner(text, operation);
}

export async function progressBar<T>(
    description: string = 'Processing...',
    total: number = 100,
    operation: ProgressOperation<T>
): Promise<T> {
    return getProgressManager().progressBar(description, total, operation);
}'''


class RustProgressAdapter(LanguageAdapter):
    """Rust adapter for progress management code generation."""
    
    def generate_imports(self, config: Dict[str, Any]) -> str:
        """Generate Rust imports for progress management."""
        return '''use std::io::{self, Write};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};
use anyhow::Result;

// Optional indicatif for enhanced progress bars
#[cfg(feature = "indicatif")]
use indicatif::{ProgressBar, ProgressStyle, Spinner};'''
    
    def generate_progress_manager_struct(self, config: Dict[str, Any]) -> str:
        """Generate Rust progress manager struct."""
        return '''pub struct ProgressManager {
    use_enhanced: bool,
}

impl ProgressManager {
    pub fn new() -> Self {
        Self {
            use_enhanced: cfg!(feature = "indicatif"),
        }
    }
    
    pub fn spinner<F, T>(&self, text: &str, operation: F) -> Result<T>
    where
        F: FnOnce() -> Result<T>,
    {
        #[cfg(feature = "indicatif")]
        {
            if self.use_enhanced {
                let spinner = Spinner::new(
                    indicatif::ProgressStyle::default_spinner()
                        .template("{spinner:.blue} {msg}")?,
                    text.to_string(),
                );
                
                let result = operation();
                spinner.finish_with_message(match &result {
                    Ok(_) => format!("✓ {}", text),
                    Err(_) => format!("✗ {}", text),
                });
                
                return result;
            }
        }
        
        // Fallback implementation
        print!("{}", text);
        io::stdout().flush()?;
        
        let result = operation();
        match &result {
            Ok(_) => println!(" ✓"),
            Err(_) => println!(" ✗"),
        }
        
        result
    }
    
    pub fn progress_bar<F, T>(&self, description: &str, total: u64, operation: F) -> Result<T>
    where
        F: FnOnce(&dyn Fn(u64)) -> Result<T>,
    {
        #[cfg(feature = "indicatif")]
        {
            if self.use_enhanced {
                let pb = ProgressBar::new(total);
                pb.set_style(
                    ProgressStyle::default_bar()
                        .template("[{elapsed_precise}] {bar:40.cyan/blue} {pos:>7}/{len:7} {msg}")?
                        .progress_chars("##-")
                );
                pb.set_message(description);
                
                let update_fn = |advance: u64| pb.inc(advance);
                let result = operation(&update_fn);
                
                pb.finish();
                return result;
            }
        }
        
        // Fallback implementation
        println!("{}", description);
        let mut current = 0u64;
        
        let update_fn = |advance: u64| {
            current += advance;
            let percentage = if total > 0 { (current * 100) / total } else { 0 };
            print!("\\rProgress: {}%", percentage);
            io::stdout().flush().unwrap_or(());
        };
        
        let result = operation(&update_fn);
        println!();
        
        result
    }
}

impl Default for ProgressManager {
    fn default() -> Self {
        Self::new()
    }
}'''
    
    def generate_convenience_functions(self, config: Dict[str, Any]) -> str:
        """Generate Rust convenience functions."""
        return '''
// Global instance using lazy_static or once_cell
use std::sync::OnceLock;
static PROGRESS_MANAGER: OnceLock<ProgressManager> = OnceLock::new();

pub fn get_progress_manager() -> &'static ProgressManager {
    PROGRESS_MANAGER.get_or_init(|| ProgressManager::new())
}

pub fn spinner<F, T>(text: &str, operation: F) -> Result<T>
where
    F: FnOnce() -> Result<T>,
{
    get_progress_manager().spinner(text, operation)
}

pub fn progress_bar<F, T>(description: &str, total: u64, operation: F) -> Result<T>
where
    F: FnOnce(&dyn Fn(u64)) -> Result<T>,
{
    get_progress_manager().progress_bar(description, total, operation)
}'''
    
    def generate_cargo_dependencies(self, config: Dict[str, Any]) -> str:
        """Generate Cargo.toml dependencies for progress features."""
        return '''# Add to [dependencies] section of Cargo.toml
anyhow = "1.0"

# Optional enhanced progress indicators
[dependencies.indicatif]
version = "0.17"
optional = true

[features]
default = []
enhanced-progress = ["indicatif"]'''