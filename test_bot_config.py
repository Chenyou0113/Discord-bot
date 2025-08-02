#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord 機器人啟動測試腳本
檢查所有依賴項和配置是否正確
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """測試所有必要的模組導入"""
    print("🔍 測試模組導入...")
    
    try:
        import discord
        print("  ✅ discord.py")
    except ImportError as e:
        print(f"  ❌ discord.py: {e}")
        return False
    
    try:
        import aiohttp
        print("  ✅ aiohttp")
    except ImportError as e:
        print(f"  ❌ aiohttp: {e}")
        return False
    
    try:
        import google.generativeai as genai
        print("  ✅ google.generativeai")
    except ImportError as e:
        print(f"  ❌ google.generativeai: {e}")
        return False
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        print("  ✅ reservoir_commands")
    except ImportError as e:
        print(f"  ❌ reservoir_commands: {e}")
        return False
    
    return True

def test_environment():
    """測試環境變數設定"""
    print("\n🔍 測試環境變數...")
    
    load_dotenv()
    
    required_vars = {
        'DISCORD_TOKEN': 'Discord 機器人 Token',
        'GOOGLE_API_KEY': 'Google API 金鑰',
        'CWA_API_KEY': '中央氣象署 API 金鑰',
        'TDX_CLIENT_ID': 'TDX 客戶端 ID',
        'TDX_CLIENT_SECRET': 'TDX 客戶端密鑰'
    }
    
    all_set = True
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: 已設定 ({desc})")
        else:
            print(f"  ❌ {var}: 未設定 ({desc})")
            all_set = False
    
    return all_set

def test_bot_config():
    """測試機器人配置"""
    print("\n🔍 測試機器人配置...")
    
    try:
        from bot import CustomBot
        print("  ✅ CustomBot 類別可以導入")
        
        # 檢查初始擴展列表
        bot = CustomBot()
        if hasattr(bot, 'initial_extensions'):
            print(f"  ✅ 初始擴展列表: {len(bot.initial_extensions)} 個")
            for ext in bot.initial_extensions:
                print(f"    - {ext}")
        else:
            print("  ❌ 找不到初始擴展列表")
            return False
        
        return True
        
    except ImportError as e:
        print(f"  ❌ CustomBot 導入失敗: {e}")
        return False
    except Exception as e:
        print(f"  ❌ 機器人配置錯誤: {e}")
        return False

def main():
    """主測試函數"""
    print("🤖 Discord 機器人啟動測試")
    print("=" * 50)
    
    tests = [
        ("模組導入", test_imports),
        ("環境變數", test_environment),
        ("機器人配置", test_bot_config)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        result = test_func()
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有測試通過！機器人已準備就緒。")
        print("\n下一步:")
        print("1. 執行 python bot.py 啟動機器人")
        print("2. 或執行指令同步: python sync_commands.py")
    else:
        print("❌ 部分測試失敗，請檢查上述錯誤並修復。")
    
    return all_passed

if __name__ == "__main__":
    main()
