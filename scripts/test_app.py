#!/usr/bin/env python3
"""Test script for BabelDOC desktop application."""

import sys
import os
import subprocess
import json
import time

print("BabelDOC Desktop - 测试和运行脚本")
print("=" * 50)

# 检查依赖
print("\n1. 检查依赖...")
try:
    result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
    print(f"✓ Node.js/npm: {result.stdout.strip()}")
except:
    print("✗ npm 未安装")
    sys.exit(1)

try:
    result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
    print(f"✓ Python: {result.stdout.strip()}")
except:
    print("✗ Python3 未安装")
    sys.exit(1)

try:
    result = subprocess.run(['cargo', '--version'], capture_output=True, text=True)
    print(f"✓ Cargo/Rust: {result.stdout.strip()}")
except:
    print("✗ Cargo/Rust 未安装")
    sys.exit(1)

# 检查项目结构
print("\n2. 检查项目结构...")
project_dir = '/Users/chenjiexu/Projects/OpenSource/babeldoc-desktop'
required_dirs = [
    'src', 'src-tauri', 'BabelDOC', 'python-backend'
]
for d in required_dirs:
    path = os.path.join(project_dir, d)
    if os.path.isdir(path):
        print(f"✓ {d}/")
    else:
        print(f"✗ {d}/ 未找到")

# 检查 Node 依赖
print("\n3. 检查 Node 依赖...")
package_file = os.path.join(project_dir, 'package.json')
if os.path.exists(package_file):
    with open(package_file) as f:
        pkg = json.load(f)
    print(f"✓ package.json 存在 ({len(pkg.get('dependencies', {}))} 个依赖)")
else:
    print("✗ package.json 未找到")

# 检查 Python 环境
print("\n4. 检查 Python 环境...")
venv_path = os.path.join(project_dir, 'BabelDOC/.venv')
if os.path.isdir(venv_path):
    print(f"✓ Python 虚拟环境存在")
else:
    print(f"✗ Python 虚拟环境不存在")

# 检查 sidecar 二进制文件
print("\n5. 检查 Sidecar 二进制...")
sidecar_path = os.path.join(
    project_dir, 'src-tauri/binaries/babeldoc-sidecar-aarch64-apple-darwin'
)
if os.path.exists(sidecar_path):
    size_mb = os.path.getsize(sidecar_path) / (1024*1024)
    print(f"✓ sidecar 二进制存在 ({size_mb:.1f} MB)")
else:
    print(f"✗ sidecar 二进制未找到")

# 检查图标
print("\n6. 检查应用图标...")
icons = ['32x32.png', '128x128.png', '128x128@2x.png', 'icon.ico', 'icon.icns']
icons_dir = os.path.join(project_dir, 'src-tauri/icons')
for icon in icons:
    path = os.path.join(icons_dir, icon)
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"✓ {icon} ({size} bytes)")
    else:
        print(f"✗ {icon} 未找到")

print("\n7. 编译与构建状态...")
target_dir = os.path.join(project_dir, 'src-tauri/target/debug/babeldoc-desktop')
if os.path.exists(target_dir):
    size_mb = os.path.getsize(target_dir) / (1024*1024)
    print(f"✓ Tauri 应用已编译 ({size_mb:.1f} MB)")
else:
    print(f"✗ Tauri 应用未编译")

print("\n" + "=" * 50)
print("测试完成！")
print("\n要启动应用，请运行：")
print("  npm run tauri:dev")
print("\n或者构建发布版本：")
print("  npm run tauri:build")
