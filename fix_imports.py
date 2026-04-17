# fix_imports.py
import sys
import os
import logging  # 提前导入标准库 logging，避免自定义模块干扰

def add_path_recursive(root_dir, max_depth=3):
    """
    递归地将 root_dir 下所有包含 .py 文件且没有 __init__.py 的目录的父目录加入 sys.path。
    这可以解决 paddleocr 内部各种绝对导入问题（如 import extract_textpoint_slow）。
    """
    if not os.path.exists(root_dir):
        return
    for root, dirs, files in os.walk(root_dir):
        depth = root[len(root_dir):].count(os.sep)
        if depth > max_depth:
            continue
        # 如果该目录下有 .py 文件但没有 __init__.py，则将其父目录加入 path
        if any(f.endswith('.py') for f in files) and '__init__.py' not in files:
            parent = os.path.dirname(root)
            if parent not in sys.path:
                sys.path.insert(0, parent)
                print(f"Added {parent} to sys.path for absolute imports")

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
        print(f"Added {base_path} to sys.path")

    # === 关键修复：将 e2e_utils 目录本身加入 sys.path，使 `import extract_textpoint_slow` 能直接找到 ===
    e2e_utils_path = os.path.join(base_path, 'paddleocr', 'ppocr', 'utils', 'e2e_utils')
    if os.path.exists(e2e_utils_path) and e2e_utils_path not in sys.path:
        sys.path.insert(0, e2e_utils_path)
        print(f"Added {e2e_utils_path} to sys.path (for direct import of e2e_utils modules)")

    # 同时保留添加父目录的代码，以应对其他可能的导入方式
    parent_of_e2e = os.path.dirname(e2e_utils_path)
    if os.path.exists(parent_of_e2e) and parent_of_e2e not in sys.path:
        sys.path.insert(0, parent_of_e2e)
        print(f"Added {parent_of_e2e} to sys.path (for e2e_utils parent)")

    # 递归处理其他可能需要添加路径的目录
    paddleocr_root = os.path.join(base_path, 'paddleocr')
    if os.path.exists(paddleocr_root):
        add_path_recursive(paddleocr_root, max_depth=4)