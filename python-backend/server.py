"""JSON-RPC over stdio 服务器"""

import asyncio
import json
import sys
from typing import Any

# 输出到 stderr 用于调试
def log(msg: str):
    print(f"[SIDECAR] {msg}", file=sys.stderr, flush=True)

from translator import TranslationService


class JsonRpcServer:
    """JSON-RPC over stdio 服务器"""

    def __init__(self):
        log("JsonRpcServer initializing...")
        self.service = TranslationService()
        self.running = True
        self._current_task: asyncio.Task | None = None
        log("JsonRpcServer initialized")

    async def handle_request(self, request: dict) -> dict:
        """处理 JSON-RPC 请求"""
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")
        log(f"Handling request: method={method}, id={req_id}")

        try:
            if method == "initialize":
                log("Starting service initialization...")
                # 添加60秒超时
                try:
                    await asyncio.wait_for(self.service.initialize(), timeout=60.0)
                    log("Service initialization complete")
                    return {"jsonrpc": "2.0", "id": req_id, "result": {"status": "ok"}}
                except asyncio.TimeoutError:
                    log("Service initialization timeout - 可能是模型下载时间过长")
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32001,
                            "message": "Initialization timeout (60s) - 可能是模型下载时间过长，请检查网络连接或稍后重试"
                        }
                    }
                except Exception as e:
                    log(f"Service initialization failed: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc(file=sys.stderr)
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32000,
                            "message": f"Initialization failed: {type(e).__name__}: {str(e)}"
                        }
                    }

            elif method == "translate":
                log(f"Starting translation task...")
                # 翻译是流式的，通过事件推送
                self._current_task = asyncio.create_task(
                    self._stream_translation(req_id, params)
                )
                return {"jsonrpc": "2.0", "id": req_id, "result": {"status": "started"}}


            elif method == "cancel":
                if self._current_task:
                    self._current_task.cancel()
                    self._current_task = None
                return {"jsonrpc": "2.0", "id": req_id, "result": {"status": "cancelled"}}

            elif method == "shutdown":
                self.running = False
                return {"jsonrpc": "2.0", "id": req_id, "result": {"status": "shutdown"}}

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(e)},
            }

    async def _stream_translation(self, req_id: str, params: dict):
        """流式翻译并发送事件"""
        try:
            log("Starting stream translation...")
            async for event in self.service.translate(params):
                log(f"Translation event: {event.get('type', 'unknown')}")
                self._send_notification("translation_event", event)
        except asyncio.CancelledError:
            log("Translation cancelled")
            self._send_notification(
                "translation_event", {"type": "error", "error": "Translation cancelled"}
            )
        except Exception as e:
            log(f"Translation error: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            self._send_notification(
                "translation_event", {"type": "error", "error": str(e)}
            )
        finally:
            self._current_task = None

    def _send_notification(self, method: str, params: dict):
        """发送 JSON-RPC 通知"""
        notification = {"jsonrpc": "2.0", "method": method, "params": params}
        log(f"Sending notification: {method}")
        print(json.dumps(notification), flush=True)

    async def run(self):
        """运行服务器主循环"""
        log("Server starting...")
        # 不再自动初始化，等待客户端发送 initialize 请求

        while self.running:
            try:
                # 异步读取 stdin，添加30秒超时
                log("Waiting for input...")
                try:
                    line = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline),
                        timeout=30.0
                    )
                except asyncio.TimeoutError:
                    log("Timeout waiting for input, continuing...")
                    continue

                if not line:
                    log("EOF received, exiting")
                    break

                line = line.strip()
                if not line:
                    continue

                log(f"Received: {line[:100]}...")
                try:
                    request = json.loads(line)
                    response = await self.handle_request(request)
                    log(f"Sending response for id={request.get('id')}")
                    print(json.dumps(response), flush=True)
                except json.JSONDecodeError as e:
                    log(f"JSON decode error: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": "Parse error"},
                        "id": None,
                    }
                    print(json.dumps(error_response), flush=True)
            except KeyboardInterrupt:
                log("Keyboard interrupt, shutting down...")
                self.running = False
            except Exception as e:
                log(f"Error in main loop: {e}")
                import traceback
                traceback.print_exc(file=sys.stderr)
                # 发送错误通知
                self._send_notification(
                    "translation_event", {"type": "error", "error": str(e)}
                )


def main():
    """Main entry point for the sidecar."""
    log("Sidecar starting...")
    server = JsonRpcServer()
    asyncio.run(server.run())
    log("Sidecar exiting...")
