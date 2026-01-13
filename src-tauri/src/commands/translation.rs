use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::sync::Mutex;
use tauri::{command, AppHandle, Emitter};
use tauri_plugin_shell::ShellExt;

// 存储活跃的翻译任务
static ACTIVE_TASKS: Mutex<Option<HashMap<String, bool>>> = Mutex::new(None);

fn get_tasks() -> &'static Mutex<Option<HashMap<String, bool>>> {
    &ACTIVE_TASKS
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TranslationConfig {
    pub input_file: String,
    pub lang_in: String,
    pub lang_out: String,
    pub model: String,
    pub api_key: String,
    pub base_url: Option<String>,
    pub pages: Option<String>,
    pub output_dir: Option<String>,
    pub output_dual: bool,
    pub output_mono: bool,
    // PDF 设置
    pub watermark_mode: Option<String>,
    pub enhance_compatibility: Option<bool>,
    pub skip_clean: Option<bool>,
    // 翻译设置
    pub qps: Option<i32>,
    pub auto_extract_glossary: Option<bool>,
    pub ignore_cache: Option<bool>,
    // 模型设置
    pub enable_json_mode: Option<bool>,
    pub send_dashscope_header: Option<bool>,
    pub no_send_temperature: Option<bool>,
}

#[command]
pub async fn start_translation(
    app: AppHandle,
    config: TranslationConfig,
) -> Result<String, String> {
    let task_id = uuid::Uuid::new_v4().to_string();

    // 初始化任务映射
    {
        let mut tasks = get_tasks().lock().unwrap();
        if tasks.is_none() {
            *tasks = Some(HashMap::new());
        }
        tasks.as_mut().unwrap().insert(task_id.clone(), true);
    }

    let task_id_clone = task_id.clone();
    let app_handle = app.clone();

    // 在后台启动翻译
    tauri::async_runtime::spawn(async move {
        if let Err(e) = run_translation(&app_handle, &task_id_clone, config).await {
            // 发送错误事件
            let _ = app_handle.emit(
                &format!("translation-event-{}", task_id_clone),
                serde_json::json!({
                    "type": "error",
                    "error": e
                }),
            );
        }

        // 清理任务
        let mut tasks = get_tasks().lock().unwrap();
        if let Some(ref mut map) = *tasks {
            map.remove(&task_id_clone);
        }
    });

    Ok(task_id)
}

async fn run_translation(
    app: &AppHandle,
    task_id: &str,
    config: TranslationConfig,
) -> Result<(), String> {
    // 获取 sidecar 命令
    let sidecar = app
        .shell()
        .sidecar("babeldoc-sidecar")
        .map_err(|e| format!("Failed to create sidecar: {}", e))?;

    let (mut rx, mut child) = sidecar
        .spawn()
        .map_err(|e| format!("Failed to spawn sidecar: {}", e))?;

    // 发送初始化请求
    let init_request = serde_json::json!({
        "jsonrpc": "2.0",
        "method": "initialize",
        "id": "1"
    });

    child
        .write(format!("{}\n", init_request).as_bytes())
        .map_err(|e| format!("Failed to write to sidecar: {}", e))?;

    // 等待初始化响应，添加300秒超时（5分钟）
    use tauri_plugin_shell::process::CommandEvent;
    use tokio::time::{timeout, Duration};

    let init_timeout = Duration::from_secs(300);
    let mut initialization_complete = false;

    match timeout(init_timeout, async {
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => {
                    if let Ok(response) = serde_json::from_slice::<Value>(&line) {
                        // 检查是否是初始化响应
                        if response.get("id").and_then(|id| id.as_str()) == Some("1") {
                            if response.get("result").is_some() {
                                return Ok::<(), String>(());
                            } else if let Some(error) = response.get("error") {
                                return Err(format!("Initialization failed: {}", error));
                            }
                        }
                    }
                }
                CommandEvent::Stderr(line) => {
                    let stderr_msg = String::from_utf8_lossy(&line);
                    eprintln!("Sidecar stderr (init): {}", stderr_msg);
                    // 将stderr也传递给前端，方便调试
                    let _ = app.emit(
                        &format!("translation-event-{}", task_id),
                        serde_json::json!({
                            "type": "log",
                            "message": stderr_msg.to_string()
                        })
                    );
                }
                CommandEvent::Error(e) => {
                    return Err(format!("Sidecar error during init: {}", e));
                }
                CommandEvent::Terminated(status) => {
                    if let Some(code) = status.code {
                        if code != 0 {
                            return Err(format!("Sidecar terminated during init with code: {}", code));
                        }
                    }
                    return Err("Sidecar terminated unexpectedly during init".to_string());
                }
                _ => {}
            }
        }
        Err("Sidecar closed connection during init".to_string())
    }).await {
        Ok(result) => {
            result.map_err(|e| format!("Initialization error: {}", e))?;
            initialization_complete = true;
        }
        Err(_) => {
            let _ = child.kill();
            return Err("Sidecar initialization timeout (300s) - 可能是模型下载时间过长，请检查网络连接或稍后重试".to_string());
        }
    }

    // 发送翻译请求
    let translate_request = serde_json::json!({
        "jsonrpc": "2.0",
        "method": "translate",
        "params": config,
        "id": "2"
    });

    child
        .write(format!("{}\n", translate_request).as_bytes())
        .map_err(|e| format!("Failed to write translate request: {}", e))?;

    // 读取并转发事件
    while let Some(event) = rx.recv().await {
        match event {
            CommandEvent::Stdout(line) => {
                if let Ok(response) = serde_json::from_slice::<Value>(&line) {
                    // 检查是否是通知（有 method 字段但没有 id 字段）
                    if response.get("method").is_some() {
                        if let Some(params) = response.get("params") {
                            // 发送事件到前端
                            let _ = app.emit(&format!("translation-event-{}", task_id), params);

                            // 检查是否完成
                            if let Some(event_type) = params.get("type").and_then(|t| t.as_str()) {
                                if event_type == "finish" || event_type == "error" {
                                    break;
                                }
                            }
                        }
                    }
                }
            }
            CommandEvent::Stderr(line) => {
                let stderr_msg = String::from_utf8_lossy(&line);
                eprintln!("Sidecar stderr: {}", stderr_msg);
                // 将stderr也传递给前端，方便调试
                let _ = app.emit(
                    &format!("translation-event-{}", task_id),
                    serde_json::json!({
                        "type": "log",
                        "message": stderr_msg.to_string()
                    })
                );
            }
            CommandEvent::Error(e) => {
                return Err(format!("Sidecar error: {}", e));
            }
            CommandEvent::Terminated(status) => {
                if let Some(code) = status.code {
                    if code != 0 {
                        return Err(format!("Sidecar terminated with status code: {}", code));
                    }
                }
                break;
            }
            _ => {}
        }

        // 检查是否被取消
        let is_cancelled = {
            let tasks = get_tasks().lock().unwrap();
            tasks
                .as_ref()
                .map(|m| !m.contains_key(task_id))
                .unwrap_or(true)
        };

        if is_cancelled {
            let _ = child.kill();
            return Err("Translation cancelled".to_string());
        }
    }

    Ok(())
}

#[command]
pub async fn cancel_translation(task_id: String) -> Result<(), String> {
    let mut tasks = get_tasks().lock().unwrap();
    if let Some(ref mut map) = *tasks {
        map.remove(&task_id);
    }
    Ok(())
}
