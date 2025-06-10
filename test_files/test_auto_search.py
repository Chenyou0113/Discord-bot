#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試自動搜尋功能
"""

import os
import sys
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_auto_search_function():
    """測試自動搜尋功能"""
    print("🔍 測試自動搜尋功能...")
    
    try:
        # 測試模組導入
        from cogs.search_commands import SearchCommands
        print("✅ SearchCommands 模組導入成功")
        
        # 創建測試機器人
        intents = discord.Intents.default()
        intents.message_content = True
        bot = commands.Bot(command_prefix='!', intents=intents)
        
        # 初始化搜尋命令
        search_cog = SearchCommands(bot)
        print("✅ SearchCommands Cog 初始化成功")
        
        # 測試自動搜尋設定
        print(f"📋 預設觸發關鍵字: {search_cog.auto_search_keywords}")
        print(f"📋 自動搜尋狀態: {search_cog.auto_search_enabled}")
        
        # 模擬測試訊息內容
        test_messages = [
            "我想搜尋 Python 教學",
            "幫我搜索一下 Discord Bot",
            "查找 機器學習 相關資料",
            "普通訊息，不包含觸發詞",
        ]
        
        print("\n🧪 測試訊息檢測:")
        for msg in test_messages:
            has_keyword = any(keyword in msg for keyword in search_cog.auto_search_keywords)
            status = "✅ 會觸發" if has_keyword else "❌ 不會觸發"
            print(f"  '{msg}' -> {status}")
        
        # 測試關鍵字提取邏輯
        print("\n🔧 測試關鍵字提取:")
        test_content = "我想搜尋 Python 程式設計教學"
        for keyword in search_cog.auto_search_keywords:
            if keyword in test_content:
                parts = test_content.split(keyword, 1)
                if len(parts) > 1:
                    query = parts[1].strip()
                    print(f"  觸發詞: '{keyword}' -> 查詢: '{query}'")
        
        print("\n✅ 自動搜尋功能測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_environment():
    """測試環境配置"""
    print("🌍 檢查環境配置...")
    
    required_vars = [
        'DISCORD_TOKEN',
        'GOOGLE_API_KEY',
        'GOOGLE_SEARCH_API_KEY',
        'GOOGLE_SEARCH_ENGINE_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var}: 已設定")
    
    if missing_vars:
        print(f"❌ 缺少環境變數: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ 所有環境變數已正確設定")
        return True

async def main():
    """主測試函數"""
    print("🤖 Discord Bot 自動搜尋功能測試")
    print("=" * 50)
    
    # 測試環境
    env_ok = await test_environment()
    if not env_ok:
        print("\n❌ 環境配置測試失敗")
        return False
    
    # 測試自動搜尋功能
    auto_search_ok = await test_auto_search_function()
    if not auto_search_ok:
        print("\n❌ 自動搜尋功能測試失敗")
        return False
    
    print("\n🎉 所有測試通過！")
    print("\n📝 使用說明:")
    print("1. 在Discord伺服器中，管理員使用 /auto_search enable:True 啟用自動搜尋")
    print("2. 用戶在訊息中包含 '搜尋'、'搜索' 或 '查找' 等關鍵字")
    print("3. Bot會自動檢測並執行搜尋，使用表情符號反應提供回饋")
    print("4. 搜尋結果會回覆到原訊息")
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if result:
            print("\n✅ 測試完成 - 自動搜尋功能準備就緒")
            sys.exit(0)
        else:
            print("\n❌ 測試失敗")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ 測試中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 測試過程中發生錯誤: {e}")
        sys.exit(1)
