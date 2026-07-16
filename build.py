"""
BabelDOC Desktop - 打包脚本
使用 PyInstaller 打包应用
"""

import subprocess
import sys
import platform
import shutil
import plistlib
from pathlib import Path

from src.version import __version__


def get_platform_info():
    """获取平台信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin":
        return "macos", machine
    elif system == "windows":
        return "windows", machine
    elif system == "linux":
        return "linux", machine
    else:
        return system, machine


def remove_macos_collected_directory(project_root: Path) -> None:
    """Keep only the Finder-launchable app, not the terminal-backed raw binary."""
    app_bundle = project_root / "dist" / "BabelDOC.app"
    collected_directory = project_root / "dist" / "BabelDOC"
    if app_bundle.is_dir() and collected_directory.is_dir():
        shutil.rmtree(collected_directory)


def update_macos_bundle_metadata(project_root: Path) -> None:
    """Write release version metadata and restore the app's ad-hoc signature."""
    app_bundle = project_root / "dist" / "BabelDOC.app"
    info_plist = app_bundle / "Contents" / "Info.plist"
    with info_plist.open("rb") as file_handle:
        metadata = plistlib.load(file_handle)
    metadata.update(
        {
            "CFBundleIdentifier": "com.babeldoc.desktop",
            "CFBundleShortVersionString": __version__,
            "CFBundleVersion": __version__,
        }
    )
    with info_plist.open("wb") as file_handle:
        plistlib.dump(metadata, file_handle)
    subprocess.run(
        ["codesign", "--force", "--deep", "--sign", "-", str(app_bundle)],
        check=True,
    )


def build_with_pyinstaller():
    """使用 PyInstaller 打包"""
    print("Building with PyInstaller...")

    # 获取项目根目录
    project_root = Path(__file__).parent.absolute()
    platform_name, arch = get_platform_info()

    print(f"Platform: {platform_name}, Architecture: {arch}")

    # 根据平台选择图标
    if platform_name == "macos":
        icon_file = project_root / "resources" / "icons" / "icon.icns"
    elif platform_name == "windows":
        icon_file = project_root / "resources" / "icons" / "icon.ico"
    else:
        icon_file = project_root / "resources" / "icons" / "icon.png"

    # 根据平台选择数据分隔符
    data_sep = ";" if platform_name == "windows" else ":"

    # PyInstaller 基础命令
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(project_root / "src" / "main.py"),
        "--name=BabelDOC",
        "--windowed",
        f"--icon={icon_file}",
        f"--add-data={project_root / 'resources'}{data_sep}resources",
        f"--add-data={project_root / 'src'}{data_sep}src",  # 包含 src 目录（含样式文件）
        f"--additional-hooks-dir={project_root / 'hooks'}",  # 自定义 hooks 目录
        f"--runtime-hook={project_root / 'hooks' / 'pyi_rth_tiktoken.py'}",  # tiktoken 运行时 hook
        "--hidden-import=babeldoc",
        "--hidden-import=babeldoc.format.pdf.high_level",
        "--hidden-import=babeldoc.translator.translator",
        "--hidden-import=babeldoc.docvision.doclayout",
        # OpenCV - 使用 PyInstaller hooks contrib 提供的官方 hook
        "--hidden-import=cv2",
        "--collect-all=babeldoc",
        "--collect-data=babeldoc",
        # ONNX Runtime - 必需的依赖
        "--hidden-import=onnxruntime",
        "--collect-data=onnxruntime",
        "--collect-binaries=onnxruntime",
        # tiktoken - 编码文件
        "--hidden-import=tiktoken",
        "--hidden-import=tiktoken_ext",
        "--hidden-import=tiktoken_ext.openai_public",
        "--collect-data=tiktoken",
        "--collect-data=tiktoken_ext",
        # 其他可能需要的依赖
        "--hidden-import=PIL",
        "--hidden-import=numpy",
        "--clean",
        "--noconfirm",
    ]

    # macOS 使用 onedir 模式（PyInstaller v7.0 将不再支持 onefile + app bundle）
    # Windows 和 Linux 可以使用 onefile 模式
    if platform_name != "macos":
        cmd.append("--onefile")
    elif platform_name == "macos":
        cmd.append("--osx-bundle-identifier=com.babeldoc.desktop")

    if platform_name == "windows":
        cmd.append(f"--version-file={project_root / 'resources' / 'version_info.txt'}")

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("Build completed!")

    if platform_name == "macos":
        update_macos_bundle_metadata(project_root)
        remove_macos_collected_directory(project_root)
        print(f"Output: {project_root / 'dist' / 'BabelDOC.app'}")
    else:
        print(f"Output: {project_root / 'dist' / 'BabelDOC'}")


def build_with_nuitka():
    """使用 Nuitka 打包"""
    print("Building with Nuitka...")

    # 获取项目根目录
    project_root = Path(__file__).parent.absolute()

    platform_name, _ = get_platform_info()

    # Nuitka 命令
    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--onefile",
        "--enable-plugin=pyside6",
        "--include-package=babeldoc",
        f"--include-data-dir={project_root / 'resources'}=resources",
        f"--include-data-dir={project_root / 'src' / 'ui' / 'styles'}=src/ui/styles",
        f"--output-dir={project_root / 'dist'}",
        "--remove-output",
        str(project_root / "src" / "main.py"),
    ]

    if platform_name == "windows":
        cmd.append(
            f"--windows-icon-from-ico={project_root / 'resources' / 'icons' / 'icon.ico'}"
        )

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("Build completed!")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="BabelDOC Desktop 打包脚本")
    parser.add_argument(
        "--nuitka", action="store_true", help="使用 Nuitka 而不是 PyInstaller"
    )
    args = parser.parse_args()

    if args.nuitka:
        build_with_nuitka()
    else:
        build_with_pyinstaller()


if __name__ == "__main__":
    main()
