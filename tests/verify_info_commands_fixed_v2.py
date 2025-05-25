import sys
import os

# 添加父目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 嘗試導入模組
try:
    from cogs.info_commands_fixed_v2 import InfoCommands
    print("✅ 成功導入 InfoCommands 模組！")
    print("語法檢查通過")
except SyntaxError as e:
    print(f"❌ 語法錯誤: {e}")
except ImportError as e:
    print(f"❌ 導入錯誤: {e}")
except Exception as e:
    print(f"❌ 其他錯誤: {e}")
