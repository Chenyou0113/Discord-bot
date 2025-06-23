#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot 啟動測試腳本
檢查 Discord Bot 是否能正常載入所有 Cog
"""

import asyncio
import sys
import os
import discord
from discord.ext import commands

# 添加專案根目錄到 sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

async def test_bot_loading():
    """測試 Bot 載入"""
    print("🤖 測試 Discord Bot 載入...")
    print("=" * 50)
    
    try:
        # 建立測試用 Bot 實例
        intents = discord.Intents.default()
        intents.message_content = True
        bot = commands.Bot(command_prefix='!', intents=intents)
        
        # 載入 InfoCommands Cog
        print("📦 載入 InfoCommands Cog...")
        await bot.load_extension('cogs.info_commands_fixed_v4_clean')
        print("  ✅ InfoCommands Cog 載入成功")
        
        # 檢查指令是否已註冊
        print("\n📋 檢查註冊的指令...")
        for cog_name, cog in bot.cogs.items():
            print(f"  📂 Cog: {cog_name}")
            if hasattr(cog, '__cog_app_commands__'):
                for command in cog.__cog_app_commands__:
                    print(f"    🔗 指令: /{command.name} - {command.description}")
        
        # 測試 Cog 方法
        print("\n🔧 測試 Cog 方法...")
        info_cog = bot.get_cog('InfoCommands')
        if info_cog:
            print("  ✅ InfoCommands Cog 獲取成功")
            
            # 檢查重要方法是否存在
            methods_to_check = [
                'fetch_earthquake_data',
                'fetch_weather_station_data',
                'format_earthquake_data',
                'format_weather_station_data'
            ]
            
            for method_name in methods_to_check:
                if hasattr(info_cog, method_name):
                    print(f"    ✅ 方法 {method_name} 存在")
                else:
                    print(f"    ❌ 方法 {method_name} 不存在")
        else:
            print("  ❌ InfoCommands Cog 獲取失敗")
        
        # 卸載 Cog
        print("\n🔄 卸載 Cog...")
        await bot.unload_extension('cogs.info_commands_fixed_v4_clean')
        print("  ✅ Cog 卸載成功")
        
    except Exception as e:
        print(f"❌ Bot 載入測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("✨ Bot 載入測試完成！")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_bot_loading())
    if success:
        print("🎉 所有測試通過！Bot 準備就緒！")
    else:
        print("⚠️  測試失敗，請檢查錯誤訊息")
