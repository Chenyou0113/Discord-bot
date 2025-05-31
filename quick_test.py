#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速驗證 Discord 機器人模組
"""

import sys
import os

# 添加專案目錄到 Python 路徑
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def test_module_import():
    """測試所有 cogs 模組的導入"""
    modules_to_test = [
        ('cogs.admin_commands_fixed', 'AdminCommands'),
        ('cogs.basic_commands', 'BasicCommands'),
        ('cogs.chat_commands', 'ChatCommands'),
        ('cogs.info_commands_fixed_v4_clean', 'InfoCommands'),
        ('cogs.level_system', 'LevelSystem'),
        ('cogs.monitor_system', 'MonitorSystem'),
        ('cogs.voice_system', 'VoiceSystem')
    ]
    
    print("🔍 測試模組導入...")
    success_count = 0
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {module_name} -> {class_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ {module_name} -> {class_name}: {str(e)}")
    
    print(f"\n📊 結果: {success_count}/{len(modules_to_test)} 個模組導入成功")
    return success_count == len(modules_to_test)

def test_bot_syntax():
    """測試主機器人檔案語法"""
    print("\n🔍 測試主機器人檔案語法...")
    try:
        import bot
        print("✅ bot.py 語法正確")
        return True
    except Exception as e:
        print(f"❌ bot.py 語法錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== 快速驗證 Discord 機器人 ===\n")
    
    modules_ok = test_module_import()
    bot_ok = test_bot_syntax()
    
    print("\n" + "="*40)
    if modules_ok and bot_ok:
        print("🎉 所有檢查通過！機器人已準備就緒。")
        print("💡 可以執行 start_bot.bat 來啟動機器人。")
    else:
        print("⚠️  發現問題，請檢查上述錯誤。")
