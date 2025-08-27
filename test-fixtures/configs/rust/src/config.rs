use serde::{Deserialize, Serialize};
use std::env;
use std::fs;
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {    pub debug: bool,
    pub output_format: String,}

impl Default for Config {
    fn default() -> Self {
        Self {            debug: false,
            output_format: "text".to_string(),        }
    }
}

pub struct ConfigManager {
    config_file: PathBuf,
    config: Config,
}

impl ConfigManager {
    pub fn new(config_file: Option<PathBuf>) -> Result<Self, Box<dyn std::error::Error>> {
        let config_file = config_file.unwrap_or_else(|| Self::get_default_config_path());
        let mut manager = Self {
            config_file,
            config: Config::default(),
        };
        manager.load_config()?;
        Ok(manager)
    }

    fn get_default_config_path() -> PathBuf {
        let home_dir = env::var("HOME").unwrap_or_else(|_| ".".to_string());
        let config_dir = PathBuf::from(home_dir)
            .join(".config")
            .join("test-rust-cli");
        
        if let Err(_) = fs::create_dir_all(&config_dir) {
            eprintln!("Warning: Could not create config directory");
        }
        
        config_dir.join("config.yaml")
    }

    pub fn load_config(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        // Load from config file if it exists
        if self.config_file.exists() {
            let content = fs::read_to_string(&self.config_file)?;
            
            let parse_result = if self.config_file.extension().and_then(|s| s.to_str()) == Some("json") {
                serde_json::from_str::<Config>(&content).map_err(|e| Box::new(e) as Box<dyn std::error::Error>)
            } else {
                serde_yaml::from_str::<Config>(&content).map_err(|e| Box::new(e) as Box<dyn std::error::Error>)
            };
            
            match parse_result {
                Ok(data) => self.config = data,
                Err(e) => eprintln!("Warning: Failed to parse config file: {}", e),
            }
        }

        // Override with environment variables
        let env_prefix = "TEST_RUST_CLI_";        if let Ok(val) = env::var(format!("{}DEBUG", env_prefix)) {
            self.config.debug = ["true", "1", "yes", "on"].contains(&val.to_lowercase().as_str());
        }
        if let Ok(val) = env::var(format!("{}OUTPUT_FORMAT", env_prefix)) {
            self.config.output_format = val;
        }
        Ok(())
    }

    pub fn save_config(&self) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(parent) = self.config_file.parent() {
            fs::create_dir_all(parent)?;
        }

        let content = serde_yaml::to_string(&self.config)?;
        fs::write(&self.config_file, content)?;
        Ok(())
    }

    pub fn get_config(&self) -> &Config {
        &self.config
    }

    pub fn get_config_mut(&mut self) -> &mut Config {
        &mut self.config
    }
}

// Global configuration instance
static mut CONFIG_MANAGER: Option<ConfigManager> = None;
static mut CONFIG_INIT: std::sync::Once = std::sync::Once::new();

pub fn get_config() -> &'static ConfigManager {
    unsafe {
        CONFIG_INIT.call_once(|| {
            CONFIG_MANAGER = Some(ConfigManager::new(None).expect("Failed to initialize config"));
        });
        CONFIG_MANAGER.as_ref().unwrap()
    }
}