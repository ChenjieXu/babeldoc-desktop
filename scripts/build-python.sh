#!/bin/bash
set -e

echo "Building BabelDOC Python sidecar..."

cd "$(dirname "$0")/../python-backend"

# 使用uv创建虚拟环境（Python 3.12）
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with Python 3.12..."
    uv venv --python 3.12
fi

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
uv pip install -r requirements.txt
uv pip install pyinstaller

# 获取平台信息
PLATFORM=$(uname -s)
ARCH=$(uname -m)

if [ "$PLATFORM" = "Darwin" ]; then
    if [ "$ARCH" = "arm64" ]; then
        TARGET="aarch64-apple-darwin"
    else
        TARGET="x86_64-apple-darwin"
    fi
elif [ "$PLATFORM" = "Linux" ]; then
    TARGET="x86_64-unknown-linux-gnu"
elif [ "$PLATFORM" = "MINGW64_NT" ] || [ "$PLATFORM" = "MSYS_NT" ]; then
    TARGET="x86_64-pc-windows-msvc"
else
    echo "Unsupported platform: $PLATFORM"
    exit 1
fi

echo "Building for target: $TARGET"

# 设置PyInstaller选项
PYINSTALLER_OPTS="--onefile --name babeldoc-sidecar --distpath ../src-tauri/binaries"

# Windows特殊处理
if [ "$PLATFORM" = "MINGW64_NT" ] || [ "$PLATFORM" = "MSYS_NT" ]; then
    PYINSTALLER_OPTS="$PYINSTALLER_OPTS --windowed"
fi

# 打包
pyinstaller $PYINSTALLER_OPTS main.py

echo "Build complete! Binary at: src-tauri/binaries/babeldoc-sidecar"
