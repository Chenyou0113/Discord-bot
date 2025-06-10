#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的Bot啟動測試腳本
測試Bot是否能正常啟動並載入搜尋功能
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """測試所有必要的模組導入"""
    print("=== 測試模組導入 ===")
    
    try:
        import discord
        from discord.ext import commands
        print(f"✅ Discord.py version: {discord.__version__}")
        
        import aiohttp
        print("✅ aiohttp 導入成功")
        
        import google.generativeai as genai
        print("✅ Google Generative AI 導入成功")
        
        # 測試搜尋模組導入
        from cogs.search_commands import SearchCommands
        print("✅ SearchCommands 模組導入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模組導入失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ 導入測試錯誤: {e}")
        return False

def test_environment():
    """測試環境變數"""
    print("\n=== 測試環境變數 ===")
    
    required_vars = [
        'DISCORD_TOKEN',
        'GOOGLE_API_KEY', 
        'GOOGLE_SEARCH_API_KEY',
        'GOOGLE_SEARCH_ENGINE_ID'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value and value.strip():
            if 'TOKEN' in var or 'KEY' in var:
                masked = value[:8] + '...' + value[-4:]
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: 未設定")
            missing.append(var)
    
    return len(missing) == 0

async def test_bot_creation():
    """測試Bot創建和Cog載入"""
    print("\n=== 測試Bot創建 ===")
    
    try:
        import discord
        from discord.ext import commands
        
        # 創建Bot實例
        intents = discord.Intents.default()
        intents.message_content = True
        
        bot = commands.Bot(command_prefix='!', intents=intents)
        print("✅ Bot實例創建成功")
        
        # 嘗試載入搜尋Cog
        await bot.load_extension('cogs.search_commands')
        print("✅ SearchCommands Cog載入成功")
        
        # 檢查指令註冊
        search_cog = bot.get_cog('SearchCommands')
        if search_cog:
            print("✅ SearchCommands Cog已註冊")
            
            # 檢查API配置
            if hasattr(search_cog, 'google_api_key') and search_cog.google_api_key:
                print("✅ Google Search API已配置")
            else:
                print("❌ Google Search API未配置")
                
            if hasattr(search_cog, 'gemini_model') and search_cog.gemini_model:
                print("✅ Gemini AI已配置")
            else:
                print("❌ Gemini AI未配置")
        else:
            print("❌ SearchCommands Cog註冊失敗")
            return False
        
        # 清理
        await bot.close()
        print("✅ Bot測試完成並正常關閉")
        return True
        
    except Exception as e:
        print(f"❌ Bot創建測試失敗: {e}")
        return False

def test_file_structure():
    """測試文件結構"""
    print("\n=== 測試文件結構 ===")
    
    required_files = [
        'bot.py',
        '.env',
        'cogs/search_commands.py',
        'requirements.txt'
    ]
    
    missing = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} 存在")
        else:
            print(f"❌ {file_path} 不存在")
            missing.append(file_path)
    
    return len(missing) == 0

async def main():
    """主測試函數"""
    print("Discord Bot 搜尋功能啟動測試")
    print("=" * 40)
    
    # 執行所有測試
    file_test = test_file_structure()
    env_test = test_environment()
    import_test = test_imports()
    bot_test = await test_bot_creation()
    
    # 總結結果
    print("\n" + "=" * 40)
    print("測試結果總結:")
    print(f"文件結構: {'✅ 通過' if file_test else '❌ 失敗'}")
    print(f"環境變數: {'✅ 通過' if env_test else '❌ 失敗'}")
    print(f"模組導入: {'✅ 通過' if import_test else '❌ 失敗'}")
    print(f"Bot創建: {'✅ 通過' if bot_test else '❌ 失敗'}")
    
    all_passed = file_test and env_test and import_test and bot_test
    
    if all_passed:
        print("\n🎉 所有測試通過！")
        print("Discord Bot搜尋功能已準備就緒，可以正常啟動。")
        print("\n可用的搜尋指令:")
        print("  /search - 網路搜尋")
        print("  /search_summarize - AI總結搜尋")
        print("  /search_settings - 管理員設定")
        print("  /search_stats - 搜尋統計")
    else:
        print("\n⚠️ 部分測試失敗，請檢查上述問題。")
    
    return all_passed

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        print(f"\n測試完成，結果: {'成功' if result else '失敗'}")
    except KeyboardInterrupt:
        print("\n測試被用戶中斷")
    except Exception as e:
        print(f"\n測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
