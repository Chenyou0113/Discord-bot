#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord 機器人專案最終驗證腳本
檢查所有必要檔案和模組是否正常
"""

import os
import sys
import importlib.util

def check_file_exists(file_path, description):
    """檢查檔案是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} 不存在: {file_path}")
        return False

def check_module_syntax(module_path, module_name):
    """檢查模組語法是否正確"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ {module_name} 語法正確")
        return True
    except Exception as e:
        print(f"❌ {module_name} 語法錯誤: {str(e)}")
        return False

def main():
    print("=== Discord 機器人專案最終驗證 ===\n")
    
    # 檢查核心檔案
    print("1. 檢查核心檔案:")
    core_files = [
        ("bot.py", "主要機器人檔案"),
        (".env", "環境設定檔"),
        ("requirements.txt", "依賴套件列表"),
        ("start_bot.bat", "啟動腳本"),
        ("stop_bot.bat", "停止腳本")
    ]
    
    all_core_files_exist = True
    for file_path, description in core_files:
        if not check_file_exists(file_path, description):
            all_core_files_exist = False
    
    print()
    
    # 檢查 cogs 模組
    print("2. 檢查 cogs 模組:")
    cogs_modules = [
        ("cogs/admin_commands_fixed.py", "admin_commands_fixed"),
        ("cogs/basic_commands.py", "basic_commands"),
        ("cogs/chat_commands.py", "chat_commands"),
        ("cogs/info_commands_fixed_v4_clean.py", "info_commands_fixed_v4_clean"),
        ("cogs/level_system.py", "level_system"),
        ("cogs/monitor_system.py", "monitor_system"),
        ("cogs/voice_system.py", "voice_system")
    ]
    
    all_modules_valid = True
    for module_path, module_name in cogs_modules:
        if check_file_exists(module_path, f"{module_name} 模組"):
            if not check_module_syntax(module_path, module_name):
                all_modules_valid = False
        else:
            all_modules_valid = False
    
    print()
    
    # 檢查主要機器人檔案語法
    print("3. 檢查主要機器人檔案:")
    if check_module_syntax("bot.py", "bot"):
        print("✅ bot.py 語法正確")
    else:
        print("❌ bot.py 語法有問題")
        all_modules_valid = False
    
    print()
    
    # 最終結果
    print("=== 驗證結果 ===")
    if all_core_files_exist and all_modules_valid:
        print("🎉 所有檢查通過！機器人專案已準備就緒。")
        print("💡 您可以執行 start_bot.bat 來啟動機器人。")
        return True
    else:
        print("⚠️  發現問題，請檢查上述錯誤訊息。")
        return False

if __name__ == "__main__":
    main()
