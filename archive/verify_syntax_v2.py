import py_compile
import sys
import os

# 測試編譯主要的 Python 文件
print("正在檢查當前使用的檔案是否有語法錯誤...")

files_to_check = [
    'bot.py',
    'cogs/admin_commands_fixed.py',
    'cogs/info_commands_fixed_v4.py',  # 只檢查最新版本
    'cogs/basic_commands.py',
    'cogs/level_system.py',
    'cogs/monitor_system.py',
    'cogs/voice_system.py',
    'cogs/chat_commands.py',
    'fetch_earthquake_data_fixed.py',
]

all_ok = True

for file in files_to_check:
    try:
        py_compile.compile(file, doraise=True)
        print(f"✅ {file} - 編譯成功")
    except Exception as e:
        all_ok = False
        print(f"❌ {file} - 編譯失敗: {str(e)}")

if all_ok:
    print("\n✅ 所有檔案都編譯成功，沒有語法錯誤！")
else:
    print("\n❌ 有檔案存在語法錯誤，請修復後再試。")
