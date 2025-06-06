#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Bot 搜尋功能驗證腳本
檢查搜尋功能是否正確整合到Bot中
"""

import os
import sys
import asyncio
import discord
from discord.ext import commands
import aiohttp
from dotenv import load_dotenv
import logging

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_search_cog():
    """測試搜尋功能Cog"""
    print("=== 測試搜尋功能Cog ===")
    
    try:
        # 創建一個測試bot實例
        intents = discord.Intents.default()
        intents.message_content = True
        
        bot = commands.Bot(command_prefix='!', intents=intents)
        
        # 嘗試載入搜尋功能Cog
        await bot.load_extension('cogs.search_commands')
        print("✅ 搜尋功能Cog載入成功")
        
        # 檢查指令是否正確註冊
        search_cog = bot.get_cog('SearchCommands')
        if search_cog:
            print("✅ SearchCommands Cog 已註冊")
            
            # 檢查指令
            commands_to_check = ['search', 'search_summarize', 'search_settings', 'search_stats']
            for cmd_name in commands_to_check:
                cmd = bot.get_app_command(cmd_name)
                if cmd:
                    print(f"   ✅ /{cmd_name} 指令已註冊")
                else:
                    print(f"   ❌ /{cmd_name} 指令未找到")
        else:
            print("❌ SearchCommands Cog 未註冊")
            return False
        
        # 檢查API配置
        google_api_key = search_cog.google_api_key
        search_engine_id = search_cog.search_engine_id
        gemini_model = search_cog.gemini_model
        
        print(f"   Google Search API Key: {'已設定' if google_api_key else '未設定'}")
        print(f"   Search Engine ID: {'已設定' if search_engine_id else '未設定'}")
        print(f"   Gemini Model: {'已初始化' if gemini_model else '未初始化'}")
        
        await bot.close()
        return True
        
    except Exception as e:
        print(f"❌ 搜尋功能Cog測試失敗: {str(e)}")
        return False

async def test_api_endpoints():
    """測試API端點"""
    print("\n=== 測試API端點 ===")
    
    google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    if not google_api_key or not search_engine_id:
        print("❌ Google Search API 配置不完整")
        return False
    
    # 測試Google搜尋API
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": google_api_key,
        "cx": search_engine_id,
        "q": "Discord bot test",
        "num": 1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'items' in data and len(data['items']) > 0:
                        print("✅ Google Search API 測試成功")
                        print(f"   搜尋結果: {data['items'][0]['title'][:50]}...")
                        return True
                    else:
                        print("⚠️ Google Search API 回應正常但無結果")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Google Search API 錯誤: HTTP {response.status}")
                    print(f"   詳情: {error_text[:200]}...")
                    return False
    except asyncio.TimeoutError:
        print("❌ Google Search API 請求超時")
        return False
    except Exception as e:
        print(f"❌ Google Search API 測試錯誤: {str(e)}")
        return False

def test_configuration_files():
    """測試配置文件"""
    print("\n=== 測試配置文件 ===")
    
    # 檢查.env文件
    env_file = ".env"
    if os.path.exists(env_file):
        print("✅ .env 檔案存在")
        
        required_vars = ['DISCORD_TOKEN', 'GOOGLE_API_KEY', 'GOOGLE_SEARCH_API_KEY', 'GOOGLE_SEARCH_ENGINE_ID']
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value or value.strip() == '':
                missing_vars.append(var)
            else:
                print(f"   ✅ {var} 已設定")
        
        if missing_vars:
            print(f"   ❌ 缺少環境變數: {', '.join(missing_vars)}")
            return False
        else:
            print("   ✅ 所有必需環境變數已設定")
            return True
    else:
        print("❌ .env 檔案不存在")
        return False

async def main():
    """主測試函數"""
    print("Discord Bot 搜尋功能整合測試")
    print("=" * 50)
    
    # 執行測試
    config_test = test_configuration_files()
    api_test = await test_api_endpoints()
    cog_test = await test_search_cog()
    
    # 總結
    print("\n" + "=" * 50)
    print("測試結果總結:")
    print(f"配置文件: {'✅ 通過' if config_test else '❌ 失敗'}")
    print(f"API端點: {'✅ 通過' if api_test else '❌ 失敗'}")
    print(f"Cog整合: {'✅ 通過' if cog_test else '❌ 失敗'}")
    
    all_passed = config_test and api_test and cog_test
    
    if all_passed:
        print("\n🎉 所有測試通過！搜尋功能已完全整合並準備就緒。")
        print("\n可用的搜尋指令:")
        print("  /search <關鍵字> - 基本搜尋")
        print("  /search_summarize <關鍵字> - 搜尋並AI總結")
        print("  /search_settings - 管理搜尋設定 (管理員)")
        print("  /search_stats - 查看搜尋統計")
        print("\n您現在可以啟動Discord Bot並使用搜尋功能了！")
    else:
        print("\n⚠️ 部分測試失敗，請檢查上述錯誤並修正。")
    
    return all_passed

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n測試被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n測試過程中發生錯誤: {str(e)}")
        sys.exit(1)
