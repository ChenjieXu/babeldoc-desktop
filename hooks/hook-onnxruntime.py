# PyInstaller hook for onnxruntime
# 确保 onnxruntime 的所有必要文件被正确收集

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# 收集 onnxruntime 的数据文件
datas = collect_data_files("onnxruntime", include_py_files=True)

# 收集 onnxruntime 的动态库
binaries = collect_dynamic_libs("onnxruntime")

# 隐藏导入
hiddenimports = [
    "onnxruntime.capi",
    "onnxruntime.capi._pybind_state",
]
