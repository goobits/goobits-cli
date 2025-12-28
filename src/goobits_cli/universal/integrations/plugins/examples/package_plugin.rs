/*!
 * Package Manager Plugin (Rust)
 * Provides universal package management across different ecosystems
 */

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::time::SystemTime;
use tokio::fs;
use tokio::process::Command as AsyncCommand;

/// Supported package managers
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum PackageManager {
    Npm,
    Yarn,
    Pnpm,
    Pip,
    Pipx,
    Poetry,
    Cargo,
    Go,
    Composer,
    Gem,
}

impl fmt::Display for PackageManager {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            PackageManager::Npm => write!(f, "npm"),
            PackageManager::Yarn => write!(f, "yarn"),
            PackageManager::Pnpm => write!(f, "pnpm"),
            PackageManager::Pip => write!(f, "pip"),
            PackageManager::Pipx => write!(f, "pipx"),
            PackageManager::Poetry => write!(f, "poetry"),
            PackageManager::Cargo => write!(f, "cargo"),
            PackageManager::Go => write!(f, "go"),
            PackageManager::Composer => write!(f, "composer"),
            PackageManager::Gem => write!(f, "gem"),
        }
    }
}

/// Package information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PackageInfo {
    pub name: String,
    pub version: String,
    pub description: Option<String>,
    pub manager: PackageManager,
    pub installed: bool,
    pub latest_version: Option<String>,
    pub install_path: Option<PathBuf>,
    pub dependencies: Vec<String>,
    pub dev_dependencies: Vec<String>,
    pub size: Option<u64>,
    pub install_time: Option<SystemTime>,
}

impl PackageInfo {
    pub fn is_outdated(&self) -> bool {
        if let Some(latest) = &self.latest_version {
            &self.version != latest
        } else {
            false
        }
    }

    pub fn get_update_command(&self) -> String {
        match self.manager {
            PackageManager::Npm => format!("npm update {}", self.name),
            PackageManager::Yarn => format!("yarn upgrade {}", self.name),
            PackageManager::Pnpm => format!("pnpm update {}", self.name),
            PackageManager::Pip => format!("pip install --upgrade {}", self.name),
            PackageManager::Pipx => format!("pipx upgrade {}", self.name),
            PackageManager::Poetry => format!("poetry update {}", self.name),
            PackageManager::Cargo => format!("cargo update {}", self.name),
            PackageManager::Go => format!("go get -u {}", self.name),
            PackageManager::Composer => format!("composer update {}", self.name),
            PackageManager::Gem => format!("gem update {}", self.name),
        }
    }
}

/// Installation result
#[derive(Debug, Clone)]
pub struct InstallResult {
    pub success: bool,
    pub package_name: String,
    pub version: Option<String>,
    pub output: String,
    pub error: Option<String>,
    pub duration: std::time::Duration,
}

/// Package search result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub name: String,
    pub version: String,
    pub description: Option<String>,
    pub manager: PackageManager,
    pub popularity: Option<u32>,
    pub download_count: Option<u64>,
    pub last_updated: Option<SystemTime>,
}

/// Package Manager Plugin
pub struct PackagePlugin {
    available_managers: HashMap<PackageManager, bool>,
    project_path: PathBuf,
}

impl PackagePlugin {
    /// Create a new package plugin instance
    pub fn new(project_path: Option<PathBuf>) -> Self {
        Self {
            available_managers: HashMap::new(),
            project_path: project_path.unwrap_or_else(|| std::env::current_dir().unwrap()),
        }
    }

    /// Initialize the plugin and check for available package managers
    pub async fn initialize(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        let managers = [
            PackageManager::Npm,
            PackageManager::Yarn,
            PackageManager::Pnpm,
            PackageManager::Pip,
            PackageManager::Pipx,
            PackageManager::Poetry,
            PackageManager::Cargo,
            PackageManager::Go,
            PackageManager::Composer,
            PackageManager::Gem,
        ];

        for manager in &managers {
            let available = self.check_manager_availability(*manager).await;
            self.available_managers.insert(*manager, available);
        }

        Ok(())
    }

    /// Check if a package manager is available
    async fn check_manager_availability(&self, manager: PackageManager) -> bool {
        let result = AsyncCommand::new(manager.to_string())
            .arg("--version")
            .output()
            .await;

        result.is_ok()
    }

    /// Detect package managers used in the current project
    pub async fn detect_project_managers(&self) -> Vec<PackageManager> {
        let mut managers = Vec::new();

        // Check for Node.js files
        if self.file_exists("package.json").await {
            if self.file_exists("yarn.lock").await {
                managers.push(PackageManager::Yarn);
            } else if self.file_exists("pnpm-lock.yaml").await {
                managers.push(PackageManager::Pnpm);
            } else {
                managers.push(PackageManager::Npm);
            }
        }

        // Check for Python files
        if self.file_exists("pyproject.toml").await {
            if self.file_exists("poetry.lock").await {
                managers.push(PackageManager::Poetry);
            } else {
                managers.push(PackageManager::Pip);
            }
        } else if self.file_exists("requirements.txt").await || self.file_exists("setup.py").await {
            managers.push(PackageManager::Pip);
        }

        // Check for Rust
        if self.file_exists("Cargo.toml").await {
            managers.push(PackageManager::Cargo);
        }

        // Check for Go
        if self.file_exists("go.mod").await {
            managers.push(PackageManager::Go);
        }

        // Check for PHP
        if self.file_exists("composer.json").await {
            managers.push(PackageManager::Composer);
        }

        // Check for Ruby
        if self.file_exists("Gemfile").await {
            managers.push(PackageManager::Gem);
        }

        managers
    }

    /// Install a package
    pub async fn install_package(
        &self,
        package_name: &str,
        manager: PackageManager,
        options: InstallOptions,
    ) -> InstallResult {
        let start_time = std::time::Instant::now();
        
        let mut cmd = AsyncCommand::new(manager.to_string());
        
        // Build install command based on manager
        match manager {
            PackageManager::Npm => {
                cmd.arg("install");
                if options.dev {
                    cmd.arg("--save-dev");
                }
                if options.global {
                    cmd.arg("--global");
                }
            }
            PackageManager::Yarn => {
                cmd.arg("add");
                if options.dev {
                    cmd.arg("--dev");
                }
                if options.global {
                    cmd.arg("global");
                }
            }
            PackageManager::Pnpm => {
                cmd.arg("add");
                if options.dev {
                    cmd.arg("--save-dev");
                }
                if options.global {
                    cmd.arg("--global");
                }
            }
            PackageManager::Pip => {
                cmd.arg("install");
                if options.user {
                    cmd.arg("--user");
                }
                if let Some(version) = &options.version {
                    cmd.arg(format!("{}=={}", package_name, version));
                    return self.execute_install_command(cmd, package_name, start_time).await;
                }
            }
            PackageManager::Pipx => {
                cmd.arg("install");
            }
            PackageManager::Poetry => {
                cmd.arg("add");
                if options.dev {
                    cmd.arg("--group").arg("dev");
                }
            }
            PackageManager::Cargo => {
                cmd.arg("install");
                if let Some(version) = &options.version {
                    cmd.arg("--version").arg(version);
                }
            }
            PackageManager::Go => {
                cmd.arg("install");
            }
            PackageManager::Composer => {
                cmd.arg("require");
                if options.dev {
                    cmd.arg("--dev");
                }
            }
            PackageManager::Gem => {
                cmd.arg("install");
                if options.user {
                    cmd.arg("--user-install");
                }
            }
        }

        // Add package name with version if specified
        if let Some(version) = &options.version {
            match manager {
                PackageManager::Npm | PackageManager::Yarn | PackageManager::Pnpm => {
                    cmd.arg(format!("{}@{}", package_name, version));
                }
                PackageManager::Composer => {
                    cmd.arg(format!("{}:{}", package_name, version));
                }
                _ => {
                    cmd.arg(package_name);
                }
            }
        } else {
            cmd.arg(package_name);
        }

        self.execute_install_command(cmd, package_name, start_time).await
    }

    /// Execute install command and return result
    async fn execute_install_command(
        &self,
        mut cmd: AsyncCommand,
        package_name: &str,
        start_time: std::time::Instant,
    ) -> InstallResult {
        cmd.current_dir(&self.project_path);
        
        match cmd.output().await {
            Ok(output) => {
                let success = output.status.success();
                let output_str = String::from_utf8_lossy(&output.stdout);
                let error_str = if success {
                    None
                } else {
                    Some(String::from_utf8_lossy(&output.stderr).to_string())
                };

                InstallResult {
                    success,
                    package_name: package_name.to_string(),
                    version: None, // Would need to parse from output
                    output: output_str.to_string(),
                    error: error_str,
                    duration: start_time.elapsed(),
                }
            }
            Err(e) => InstallResult {
                success: false,
                package_name: package_name.to_string(),
                version: None,
                output: String::new(),
                error: Some(e.to_string()),
                duration: start_time.elapsed(),
            },
        }
    }

    /// Uninstall a package
    pub async fn uninstall_package(
        &self,
        package_name: &str,
        manager: PackageManager,
        global: bool,
    ) -> InstallResult {
        let start_time = std::time::Instant::now();
        
        let mut cmd = AsyncCommand::new(manager.to_string());
        
        match manager {
            PackageManager::Npm => {
                cmd.arg("uninstall");
                if global {
                    cmd.arg("--global");
                }
            }
            PackageManager::Yarn => {
                cmd.arg("remove");
                if global {
                    cmd.arg("global");
                }
            }
            PackageManager::Pnpm => {
                cmd.arg("remove");
                if global {
                    cmd.arg("--global");
                }
            }
            PackageManager::Pip => {
                cmd.arg("uninstall").arg("--yes");
            }
            PackageManager::Pipx => {
                cmd.arg("uninstall");
            }
            PackageManager::Poetry => {
                cmd.arg("remove");
            }
            PackageManager::Cargo => {
                cmd.arg("uninstall");
            }
            PackageManager::Composer => {
                cmd.arg("remove");
            }
            PackageManager::Gem => {
                cmd.arg("uninstall");
            }
            _ => {
                return InstallResult {
                    success: false,
                    package_name: package_name.to_string(),
                    version: None,
                    output: String::new(),
                    error: Some("Uninstall not supported for this manager".to_string()),
                    duration: start_time.elapsed(),
                };
            }
        }

        cmd.arg(package_name);
        self.execute_install_command(cmd, package_name, start_time).await
    }

    /// List installed packages
    pub async fn list_packages(&self, manager: PackageManager) -> Vec<PackageInfo> {
        let mut packages = Vec::new();
        
        let mut cmd = AsyncCommand::new(manager.to_string());
        
        match manager {
            PackageManager::Npm => {
                cmd.args(&["list", "--json", "--depth=0"]);
            }
            PackageManager::Yarn => {
                cmd.args(&["list", "--json"]);
            }
            PackageManager::Pnpm => {
                cmd.args(&["list", "--json", "--depth=0"]);
            }
            PackageManager::Pip => {
                cmd.args(&["list", "--format=json"]);
            }
            PackageManager::Pipx => {
                cmd.args(&["list", "--json"]);
            }
            PackageManager::Poetry => {
                cmd.args(&["show", "--no-dev"]);
            }
            PackageManager::Cargo => {
                // Cargo doesn't have a direct list command, need to parse Cargo.toml
                return self.parse_cargo_dependencies().await;
            }
            _ => {
                return packages;
            }
        }

        cmd.current_dir(&self.project_path);
        
        if let Ok(output) = cmd.output().await {
            if output.status.success() {
                let output_str = String::from_utf8_lossy(&output.stdout);
                packages.extend(self.parse_package_list(&output_str, manager));
            }
        }

        packages
    }

    /// Parse package list output based on manager format
    fn parse_package_list(&self, output: &str, manager: PackageManager) -> Vec<PackageInfo> {
        let mut packages = Vec::new();
        
        match manager {
            PackageManager::Npm | PackageManager::Yarn | PackageManager::Pnpm => {
                if let Ok(json) = serde_json::from_str::<serde_json::Value>(output) {
                    if let Some(deps) = json["dependencies"].as_object() {
                        for (name, info) in deps {
                            let version = info["version"].as_str().unwrap_or("unknown").to_string();
                            packages.push(PackageInfo {
                                name: name.clone(),
                                version,
                                description: None,
                                manager,
                                installed: true,
                                latest_version: None,
                                install_path: None,
                                dependencies: Vec::new(),
                                dev_dependencies: Vec::new(),
                                size: None,
                                install_time: None,
                            });
                        }
                    }
                }
            }
            PackageManager::Pip => {
                if let Ok(json) = serde_json::from_str::<serde_json::Value>(output) {
                    if let Some(array) = json.as_array() {
                        for item in array {
                            if let (Some(name), Some(version)) = 
                                (item["name"].as_str(), item["version"].as_str()) {
                                packages.push(PackageInfo {
                                    name: name.to_string(),
                                    version: version.to_string(),
                                    description: None,
                                    manager,
                                    installed: true,
                                    latest_version: None,
                                    install_path: None,
                                    dependencies: Vec::new(),
                                    dev_dependencies: Vec::new(),
                                    size: None,
                                    install_time: None,
                                });
                            }
                        }
                    }
                }
            }
            _ => {}
        }

        packages
    }

    /// Parse Cargo.toml dependencies
    async fn parse_cargo_dependencies(&self) -> Vec<PackageInfo> {
        let mut packages = Vec::new();
        
        let cargo_toml_path = self.project_path.join("Cargo.toml");
        
        if let Ok(content) = fs::read_to_string(cargo_toml_path).await {
            if let Ok(toml) = toml::from_str::<toml::Value>(&content) {
                if let Some(deps) = toml["dependencies"].as_table() {
                    for (name, version_info) in deps {
                        let version = if let Some(v) = version_info.as_str() {
                            v.to_string()
                        } else if let Some(v) = version_info["version"].as_str() {
                            v.to_string()
                        } else {
                            "unknown".to_string()
                        };

                        packages.push(PackageInfo {
                            name: name.clone(),
                            version,
                            description: None,
                            manager: PackageManager::Cargo,
                            installed: true,
                            latest_version: None,
                            install_path: None,
                            dependencies: Vec::new(),
                            dev_dependencies: Vec::new(),
                            size: None,
                            install_time: None,
                        });
                    }
                }
            }
        }

        packages
    }

    /// Search for packages
    pub async fn search_packages(
        &self,
        query: &str,
        manager: PackageManager,
        limit: Option<usize>,
    ) -> Vec<SearchResult> {
        let mut results = Vec::new();
        
        let mut cmd = AsyncCommand::new(manager.to_string());
        
        match manager {
            PackageManager::Npm => {
                cmd.args(&["search", "--json", query]);
            }
            PackageManager::Pip => {
                cmd.args(&["search", query]);
            }
            PackageManager::Cargo => {
                // Cargo search doesn't support JSON output
                cmd.args(&["search", query]);
            }
            _ => {
                return results;
            }
        }

        if let Ok(output) = cmd.output().await {
            if output.status.success() {
                let output_str = String::from_utf8_lossy(&output.stdout);
                results.extend(self.parse_search_results(&output_str, manager));
            }
        }

        if let Some(limit) = limit {
            results.truncate(limit);
        }

        results
    }

    /// Parse search results
    fn parse_search_results(&self, output: &str, manager: PackageManager) -> Vec<SearchResult> {
        let mut results = Vec::new();
        
        match manager {
            PackageManager::Npm => {
                for line in output.lines() {
                    if let Ok(json) = serde_json::from_str::<serde_json::Value>(line) {
                        if let Some(name) = json["name"].as_str() {
                            results.push(SearchResult {
                                name: name.to_string(),
                                version: json["version"].as_str().unwrap_or("").to_string(),
                                description: json["description"].as_str().map(|s| s.to_string()),
                                manager,
                                popularity: None,
                                download_count: None,
                                last_updated: None,
                            });
                        }
                    }
                }
            }
            PackageManager::Cargo => {
                // Parse cargo search text output
                for line in output.lines() {
                    if line.contains(" = ") {
                        let parts: Vec<&str> = line.split(" = ").collect();
                        if parts.len() >= 2 {
                            let name_version: Vec<&str> = parts[0].split_whitespace().collect();
                            if let Some(name) = name_version.first() {
                                results.push(SearchResult {
                                    name: name.to_string(),
                                    version: parts[1].trim_matches('"').to_string(),
                                    description: if parts.len() > 2 { Some(parts[2].to_string()) } else { None },
                                    manager,
                                    popularity: None,
                                    download_count: None,
                                    last_updated: None,
                                });
                            }
                        }
                    }
                }
            }
            _ => {}
        }

        results
    }

    /// Update all packages
    pub async fn update_all(&self, manager: PackageManager) -> Vec<InstallResult> {
        let mut results = Vec::new();
        
        let mut cmd = AsyncCommand::new(manager.to_string());
        
        match manager {
            PackageManager::Npm => {
                cmd.args(&["update"]);
            }
            PackageManager::Yarn => {
                cmd.args(&["upgrade"]);
            }
            PackageManager::Pnpm => {
                cmd.args(&["update"]);
            }
            PackageManager::Pip => {
                // Pip doesn't have a built-in update-all command
                let packages = self.list_packages(manager).await;
                for package in packages {
                    let result = self.install_package(
                        &package.name,
                        manager,
                        InstallOptions::default(),
                    ).await;
                    results.push(result);
                }
                return results;
            }
            PackageManager::Poetry => {
                cmd.args(&["update"]);
            }
            PackageManager::Cargo => {
                cmd.args(&["update"]);
            }
            _ => {
                return results;
            }
        }

        let start_time = std::time::Instant::now();
        cmd.current_dir(&self.project_path);
        
        match cmd.output().await {
            Ok(output) => {
                results.push(InstallResult {
                    success: output.status.success(),
                    package_name: "all".to_string(),
                    version: None,
                    output: String::from_utf8_lossy(&output.stdout).to_string(),
                    error: if output.status.success() {
                        None
                    } else {
                        Some(String::from_utf8_lossy(&output.stderr).to_string())
                    },
                    duration: start_time.elapsed(),
                });
            }
            Err(e) => {
                results.push(InstallResult {
                    success: false,
                    package_name: "all".to_string(),
                    version: None,
                    output: String::new(),
                    error: Some(e.to_string()),
                    duration: start_time.elapsed(),
                });
            }
        }

        results
    }

    /// Check if a file exists in the project directory
    async fn file_exists(&self, filename: &str) -> bool {
        let path = self.project_path.join(filename);
        fs::metadata(path).await.is_ok()
    }

    /// Get plugin information
    pub fn get_plugin_info() -> HashMap<String, serde_json::Value> {
        let mut info = HashMap::new();
        
        info.insert("name".to_string(), serde_json::Value::String("package-manager".to_string()));
        info.insert("version".to_string(), serde_json::Value::String("1.0.0".to_string()));
        info.insert("author".to_string(), serde_json::Value::String("Goobits Framework".to_string()));
        info.insert("description".to_string(), serde_json::Value::String("Universal package management across ecosystems".to_string()));
        info.insert("language".to_string(), serde_json::Value::String("rust".to_string()));
        
        let capabilities = vec![
            "multi_manager_support",
            "project_detection", 
            "package_installation",
            "dependency_management",
            "search_functionality",
            "bulk_operations"
        ];
        info.insert("capabilities".to_string(), serde_json::Value::Array(
            capabilities.into_iter().map(|s| serde_json::Value::String(s.to_string())).collect()
        ));

        info
    }
}

/// Installation options
#[derive(Debug, Clone, Default)]
pub struct InstallOptions {
    pub version: Option<String>,
    pub dev: bool,
    pub global: bool,
    pub user: bool,
}

/// CLI Integration hooks
pub async fn on_pkg_install(args: Vec<String>) -> Result<(), Box<dyn std::error::Error>> {
    let mut plugin = PackagePlugin::new(None);
    plugin.initialize().await?;

    if args.is_empty() {
        println!("❌ Package name required");
        return Ok(());
    }

    let package_name = &args[0];
    
    // Detect project managers
    let managers = plugin.detect_project_managers().await;
    
    if managers.is_empty() {
        println!("❌ No supported package managers found in project");
        return Ok(());
    }

    let manager = managers[0]; // Use the first detected manager
    println!("📦 Installing {} using {}...", package_name, manager);

    let result = plugin.install_package(
        package_name,
        manager,
        InstallOptions::default(),
    ).await;

    if result.success {
        println!("✅ Successfully installed {}", package_name);
        if let Some(version) = result.version {
            println!("   Version: {}", version);
        }
        println!("   Duration: {:?}", result.duration);
    } else {
        println!("❌ Failed to install {}", package_name);
        if let Some(error) = result.error {
            println!("   Error: {}", error);
        }
    }

    Ok(())
}

pub async fn on_pkg_list(_args: Vec<String>) -> Result<(), Box<dyn std::error::Error>> {
    let mut plugin = PackagePlugin::new(None);
    plugin.initialize().await?;

    let managers = plugin.detect_project_managers().await;
    
    if managers.is_empty() {
        println!("❌ No supported package managers found");
        return Ok(());
    }

    println!("📋 Installed Packages:");
    
    for manager in managers {
        println!("\n{} packages:", manager);
        let packages = plugin.list_packages(manager).await;
        
        if packages.is_empty() {
            println!("  (none found)");
            continue;
        }

        for package in packages {
            println!("  📦 {} @ {}", package.name, package.version);
            if let Some(desc) = package.description {
                println!("     {}", desc);
            }
        }
    }

    Ok(())
}

pub async fn on_pkg_search(args: Vec<String>) -> Result<(), Box<dyn std::error::Error>> {
    let mut plugin = PackagePlugin::new(None);
    plugin.initialize().await?;

    if args.is_empty() {
        println!("❌ Search query required");
        return Ok(());
    }

    let query = &args[0];
    let managers = plugin.detect_project_managers().await;
    
    if managers.is_empty() {
        println!("❌ No supported package managers found");
        return Ok(());
    }

    println!("🔍 Searching for '{}'...", query);

    for manager in managers {
        println!("\n{} results:", manager);
        let results = plugin.search_packages(query, manager, Some(5)).await;
        
        if results.is_empty() {
            println!("  (no results)");
            continue;
        }

        for result in results {
            println!("  📦 {} @ {}", result.name, result.version);
            if let Some(desc) = result.description {
                println!("     {}", desc);
            }
        }
    }

    Ok(())
}

pub async fn on_pkg_update(_args: Vec<String>) -> Result<(), Box<dyn std::error::Error>> {
    let mut plugin = PackagePlugin::new(None);
    plugin.initialize().await?;

    let managers = plugin.detect_project_managers().await;
    
    if managers.is_empty() {
        println!("❌ No supported package managers found");
        return Ok(());
    }

    println!("🔄 Updating all packages...");

    for manager in managers {
        println!("\nUpdating {} packages...", manager);
        let results = plugin.update_all(manager).await;
        
        for result in results {
            if result.success {
                println!("✅ Updated packages successfully");
                println!("   Duration: {:?}", result.duration);
            } else {
                println!("❌ Update failed");
                if let Some(error) = result.error {
                    println!("   Error: {}", error);
                }
            }
        }
    }

    Ok(())
}