#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試水庫指令載入
"""

import asyncio
import sys
import os
import logging

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 設定日誌
logging.basicConfig(level=logging.INFO)

async def test_cog_loading():
    """測試 Cog 載入"""
    print("=" * 50)
    print("測試水庫指令 Cog 載入")
    print("=" * 50)
    
    try:
        # 匯入必要模組
        import discord
        from discord.ext import commands
        from cogs.reservoir_commands import ReservoirCommands
        
        print("✅ 成功匯入相關模組")
        
        # 建立 bot
        intents = discord.Intents.default()
        intents.message_content = True
        bot = commands.Bot(command_prefix='!', intents=intents)
        
        print("✅ 成功建立 bot 實例")
        
        # 建立 Cog 實例
        reservoir_cog = ReservoirCommands(bot)
        print("✅ 成功建立 ReservoirCommands Cog 實例")
        
        # 檢查方法是否存在
        methods = ['reservoir_list', 'reservoir', 'reservoir_operation', 'water_cameras']
        for method_name in methods:
            if hasattr(reservoir_cog, method_name):
                method = getattr(reservoir_cog, method_name)
                print(f"✅ 找到方法: {method_name}")
                if hasattr(method, 'callback'):
                    print(f"   - 是 app_command: {method_name}")
                else:
                    print(f"   - 普通方法: {method_name}")
            else:
                print(f"❌ 未找到方法: {method_name}")
        
        # 檢查輔助方法
        helper_methods = ['_get_region_tag', '_get_region_name', 'get_reservoir_data']
        for method_name in helper_methods:
            if hasattr(reservoir_cog, method_name):
                print(f"✅ 找到輔助方法: {method_name}")
            else:
                print(f"❌ 未找到輔助方法: {method_name}")
        
        # 測試 API 連線
        print("\n🔌 測試 API 連線...")
        data = await reservoir_cog.get_reservoir_data()
        if data:
            print(f"✅ API 連線成功，資料筆數: {len(data)}")
        else:
            print("❌ API 連線失敗")
        
        print("\n✅ 所有測試完成！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    asyncio.run(test_cog_loading())

if __name__ == "__main__":
    main()
