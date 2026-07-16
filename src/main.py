"""
BabelDOC Desktop - PySide6 版本
应用入口
"""

import multiprocessing
import sys

# PyInstaller child processes re-enter this file. Dispatch resource trackers and
# spawned workers before importing OpenCV/PySide6, otherwise every child checks
# in with macOS as another foreground BabelDOC application.
if __name__ == "__main__":
    multiprocessing.freeze_support()

import logging
import os
from pathlib import Path
from datetime import datetime

# 增加 Python 递归深度限制，避免深度递归导致的错误
# OpenCV 和其他图像处理库可能需要更深的递归深度
sys.setrecursionlimit(10000)


# ============================================
# 修复 OpenCV 递归检测问题（必须在导入 cv2 之前执行）
# ============================================
def _fix_opencv_recursion():
    """修复 OpenCV 在 PyInstaller 环境中的递归检测问题"""
    # 确保 OpenCV_LOADER 标志不存在
    if hasattr(sys, "OpenCV_LOADER"):
        delattr(sys, "OpenCV_LOADER")

    # 预先导入 cv2，确保在主线程中完成初始化
    try:
        import cv2

        logging.debug(f"OpenCV 预加载成功: {cv2.__version__}")
    except ImportError as e:
        if "recursion" in str(e).lower():
            # 如果是递归错误，尝试清除标志后重新导入
            if hasattr(sys, "OpenCV_LOADER"):
                delattr(sys, "OpenCV_LOADER")
            import cv2
        else:
            raise


# 在主线程中预先处理 OpenCV
_fix_opencv_recursion()

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtGui import QIcon  # noqa: E402
from src.app import BabelDocApp  # noqa: E402
from src.utils.file_utils import get_resource_path  # noqa: E402
from src.version import __version__  # noqa: E402


def setup_logging():
    """设置日志记录"""
    # 日志文件路径（用户目录）
    log_dir = Path.home() / ".babeldoc-desktop" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"babeldoc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info(f"日志文件: {log_file}")
    return logger


def exception_hook(exc_type, exc_value, exc_traceback):
    """全局异常处理器"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger(__name__)
    logger.error("未捕获的异常:", exc_info=(exc_type, exc_value, exc_traceback))

    # 尝试显示错误对话框
    try:
        QMessageBox.critical(
            None,
            "程序错误",
            f"程序遇到错误:\n\n{str(exc_value)}\n\n详细信息已保存到日志文件。",
        )
    except Exception:
        pass


def main():
    """主函数"""
    smoke_test = "--smoke-test" in sys.argv
    multiprocessing_smoke_test = "--multiprocessing-smoke-test" in sys.argv
    hidden_args = {"--smoke-test", "--multiprocessing-smoke-test"}
    app_argv = [arg for arg in sys.argv if arg not in hidden_args]

    # 设置日志
    logger = setup_logging()
    logger.info("启动 BabelDOC Desktop")

    # 设置全局异常处理器
    sys.excepthook = exception_hook

    try:
        # 设置高 DPI 缩放
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        app = QApplication(app_argv)
        app.setApplicationName("BabelDOC Desktop")
        app.setOrganizationName("BabelDOC")
        app.setApplicationVersion(__version__)
        app.setWindowIcon(
            QIcon(str(get_resource_path("resources/icons/icon.png")))
        )

        # 创建主应用
        babeldoc_app = BabelDocApp(app)
        babeldoc_app.show()

        logger.info("主窗口已显示")
        if multiprocessing_smoke_test:
            from src.utils.multiprocessing_smoke import smoke_worker

            child_ready_file = os.environ.get(
                "BABELDOC_MULTIPROCESS_SMOKE_READY_FILE", ""
            )
            hold_seconds = float(
                os.environ.get("BABELDOC_MULTIPROCESS_SMOKE_HOLD_SECONDS", "0")
            )
            context = multiprocessing.get_context("spawn")
            child = context.Process(
                target=smoke_worker,
                args=(child_ready_file, hold_seconds),
            )
            child.start()
            child.join(timeout=max(10.0, hold_seconds + 5.0))
            if child.is_alive():
                child.terminate()
                child.join()
                raise RuntimeError("multiprocessing smoke worker timed out")
            if child.exitcode != 0:
                raise RuntimeError(
                    f"multiprocessing smoke worker exited with {child.exitcode}"
                )

        if smoke_test or multiprocessing_smoke_test:
            app.processEvents()
            ready_file = os.environ.get("BABELDOC_SMOKE_READY_FILE")
            if ready_file:
                Path(ready_file).write_text("BABELDOC_SMOKE_READY\n", encoding="utf-8")
            logger.info("BABELDOC_SMOKE_READY")
            babeldoc_app.main_window.close()
            app.processEvents()
            return 0
        return app.exec()

    except Exception as e:
        logger.error(f"启动失败: {e}", exc_info=True)
        if not smoke_test:
            QMessageBox.critical(
                None,
                "启动失败",
                f"程序启动失败:\n\n{str(e)}\n\n请查看日志文件获取详细信息。",
            )
        return 1


if __name__ == "__main__":
    sys.exit(main())
