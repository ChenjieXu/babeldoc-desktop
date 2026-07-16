# PyInstaller runtime hook for tiktoken
# 修复 tiktoken 在打包环境中找不到编码的问题

import sys

if hasattr(sys, '_MEIPASS'):
    # 在 PyInstaller 环境中，手动注册 tiktoken 编码
    def _register_tiktoken_encodings():
        try:
            import tiktoken.registry as registry
            from tiktoken_ext import openai_public

            # 定义所有编码构造函数
            ENCODING_CONSTRUCTORS = {
                "gpt2": openai_public.gpt2,
                "r50k_base": openai_public.r50k_base,
                "p50k_base": openai_public.p50k_base,
                "p50k_edit": openai_public.p50k_edit,
                "cl100k_base": openai_public.cl100k_base,
                "o200k_base": openai_public.o200k_base,
            }

            # 尝试添加 o200k_harmony（如果存在）
            if hasattr(openai_public, 'o200k_harmony'):
                ENCODING_CONSTRUCTORS["o200k_harmony"] = openai_public.o200k_harmony

            # 直接设置 registry 的编码构造函数
            registry.ENCODING_CONSTRUCTORS = ENCODING_CONSTRUCTORS

        except ImportError as e:
            print(f"Warning: tiktoken_ext not found: {e}")
        except Exception as e:
            print(f"Warning: Failed to register tiktoken encodings: {e}")

    _register_tiktoken_encodings()
