use serde_json::Value;
use std::fs;
use std::path::PathBuf;
use tauri::command;

fn get_settings_path() -> PathBuf {
    let config_dir = dirs::config_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join("babeldoc-webui");

    fs::create_dir_all(&config_dir).ok();
    config_dir.join("settings.json")
}

#[command]
pub fn load_settings() -> Result<Value, String> {
    let path = get_settings_path();

    if !path.exists() {
        return Ok(Value::Null);
    }

    let content =
        fs::read_to_string(&path).map_err(|e| format!("Failed to read settings: {}", e))?;

    let settings: Value =
        serde_json::from_str(&content).map_err(|e| format!("Failed to parse settings: {}", e))?;

    Ok(settings)
}

#[command]
pub fn save_settings(settings: Value) -> Result<(), String> {
    let path = get_settings_path();

    let content = serde_json::to_string_pretty(&settings)
        .map_err(|e| format!("Failed to serialize settings: {}", e))?;

    fs::write(&path, content).map_err(|e| format!("Failed to write settings: {}", e))?;

    Ok(())
}
