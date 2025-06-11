import os
import sys

print("=== Discord Bot 系統狀態檢查 ===")
print()

# 檢查當前目錄
print(f"當前工作目錄: {os.getcwd()}")
print()

# 檢查關鍵檔案是否存在
key_files = [
    "bot.py",
    "cogs/info_commands_fixed_v4_clean.py",
    "scripts/auto_restart_bot.bat",
    "config_files/levels.json"
]

print("關鍵檔案檢查:")
for file in key_files:
    exists = os.path.exists(file)
    status = "✅ 存在" if exists else "❌ 不存在"
    print(f"  {file}: {status}")

print()

# 檢查資料夾結構
folders = ["scripts", "config_files", "docs", "api_tests", "cogs"]
print("資料夾結構檢查:")
for folder in folders:
    exists = os.path.exists(folder)
    status = "✅ 存在" if exists else "❌ 不存在"
    print(f"  {folder}/: {status}")

print()
print("檢查完成！")
