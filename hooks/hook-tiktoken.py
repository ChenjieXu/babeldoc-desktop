# PyInstaller hook for tiktoken
# 确保 tiktoken 的编码数据文件被正确收集

from PyInstaller.utils.hooks import collect_data_files, copy_metadata

# 收集 tiktoken 的数据文件（包括编码文件）
datas = collect_data_files('tiktoken')
datas += collect_data_files('tiktoken_ext', include_py_files=True)

# 收集 tiktoken 的元数据（需要用于 entry_points）
datas += copy_metadata('tiktoken')

# 隐藏导入
hiddenimports = [
    'tiktoken_ext',
    'tiktoken_ext.openai_public',
]
