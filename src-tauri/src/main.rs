#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;

use commands::{files, settings, translation};

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            settings::load_settings,
            settings::save_settings,
            files::select_files,
            files::open_file_location,
            files::get_file_info,
            translation::start_translation,
            translation::cancel_translation,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
