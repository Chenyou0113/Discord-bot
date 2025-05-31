import sys
import os

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# 嘗試導入模組
try:    # 檢查文件是否存在
    module_path = os.path.join(parent_dir, "cogs", "info_commands_fixed_v4_clean.py")
    if not os.path.exists(module_path):
        print(f"❌ 模組文件不存在: {module_path}")
        raise FileNotFoundError(f"模組文件不存在: {module_path}")
    
    # 使用 importlib 動態導入模組
    import importlib.util
    spec = importlib.util.spec_from_file_location("info_commands_fixed_v4_clean", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    InfoCommands = module.InfoCommands
    print("✅ 成功導入 InfoCommands 模組！")
    print("語法檢查通過")
except SyntaxError as e:
    print(f"❌ 語法錯誤: {e}")
except ImportError as e:
    print(f"❌ 導入錯誤: {e}")
except Exception as e:
    print(f"❌ 其他錯誤: {e}")
