#!/usr/bin/env python3
"""
BabelDOC Desktop - 依赖诊断脚本
用于检查所有必需的依赖是否正确安装
"""

import sys
import importlib


def check_import(module_name, description):
    """检查模块是否可以导入"""
    try:
        mod = importlib.import_module(module_name)
        version = getattr(mod, "__version__", "unknown")
        print(f"✓ {description}: {version}")
        return True
    except ImportError as e:
        print(f"✗ {description}: 导入失败 - {str(e)}")
        return False
    except Exception as e:
        print(f"⚠ {description}: 部分失败 - {str(e)}")
        return False


def main():
    """主函数"""
    print("BabelDOC Desktop - 依赖检查")
    print("=" * 60)

    all_ok = True

    # 核心依赖
    print("\n核心依赖:")
    all_ok &= check_import("PySide6", "PySide6 (Qt)")
    all_ok &= check_import("babeldoc", "BabelDOC")

    # AI/ML 依赖
    print("\nAI/ML 依赖:")
    all_ok &= check_import("numpy", "NumPy")
    all_ok &= check_import("cv2", "OpenCV")
    all_ok &= check_import("onnxruntime", "ONNX Runtime")
    all_ok &= check_import("PIL", "Pillow")

    # BabelDOC 子模块
    print("\nBabelDOC 子模块:")
    all_ok &= check_import("babeldoc.format.pdf.high_level", "PDF 高级接口")
    all_ok &= check_import("babeldoc.translator.translator", "翻译器")
    all_ok &= check_import("babeldoc.docvision.doclayout", "DocLayout 模型")

    # 测试 ONNX 模型加载
    print("\n测试 ONNX 模型加载:")
    try:
        from babeldoc.docvision.doclayout import DocLayoutModel

        print("  正在加载模型...")
        DocLayoutModel.load_onnx()
        print("✓ ONNX 模型加载成功")
    except Exception as e:
        print(f"✗ ONNX 模型加载失败: {str(e)}")
        all_ok = False

    # 总结
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ 所有依赖检查通过！")
        return 0
    else:
        print("✗ 部分依赖检查失败，请查看上面的错误信息")
        print("\n建议:")
        print("1. 运行 'uv sync' 重新安装依赖")
        print("2. 检查 Python 版本 (需要 3.10+)")
        print("3. 查看详细错误日志")
        return 1


if __name__ == "__main__":
    sys.exit(main())
