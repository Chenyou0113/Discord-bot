#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診斷 reservoir_commands 載入問題
"""

import sys
import os
import traceback

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def diagnose_reservoir_commands():
    """診斷 reservoir_commands 載入問題"""
    print("🔍 診斷 reservoir_commands 載入問題...")
    print("=" * 60)
    
    try:
        print("1️⃣ 測試基本導入...")
        import discord
        from discord.ext import commands
        from discord import app_commands
        print("   ✅ Discord 相關模組導入成功")
        
        print("\n2️⃣ 測試 reservoir_commands 導入...")
        from cogs.reservoir_commands import ReservoirCommands
        print("   ✅ ReservoirCommands 類別導入成功")
        
        print("\n3️⃣ 檢查類別方法...")
        expected_commands = [
            'water_level',
            'water_cameras', 
            'water_disaster_cameras',
            'national_highway_cameras',
            'general_road_cameras'
        ]
        
        found_commands = []
        for cmd in expected_commands:
            if hasattr(ReservoirCommands, cmd):
                method = getattr(ReservoirCommands, cmd)
                if hasattr(method, '__annotations__'):
                    found_commands.append(cmd)
                    print(f"   ✅ {cmd} - 已找到且正確標註")
                else:
                    print(f"   ⚠️ {cmd} - 找到但可能缺少裝飾器")
            else:
                print(f"   ❌ {cmd} - 未找到")
        
        print(f"\n   📊 指令統計: {len(found_commands)}/{len(expected_commands)}")
        
        print("\n4️⃣ 測試 Cog 實例化...")
        class MockBot:
            pass
        
        bot = MockBot()
        cog_instance = ReservoirCommands(bot)
        print("   ✅ Cog 實例化成功")
        
        print("\n5️⃣ 檢查 setup 函數...")
        from cogs.reservoir_commands import setup
        print("   ✅ setup 函數存在")
        
        print("\n6️⃣ 測試檔案語法...")
        import py_compile
        py_compile.compile('cogs/reservoir_commands.py', doraise=True)
        print("   ✅ 檔案語法正確")
        
        print(f"\n🎯 診斷結果:")
        if len(found_commands) == len(expected_commands):
            print("✅ 所有指令都正確定義")
            print("❓ 可能的問題:")
            print("   - 機器人載入時發生運行時錯誤")
            print("   - 需要檢查機器人啟動日誌")
            print("   - API 連接問題導致 cog 載入失敗")
            
            print(f"\n💡 建議:")
            print("   1. 重新啟動機器人")
            print("   2. 檢查 bot.log 中的詳細錯誤訊息")
            print("   3. 暫時註解掉 API 呼叫進行測試")
        else:
            print("❌ 部分指令定義有問題")
            
        return True
        
    except Exception as e:
        print(f"❌ 診斷失敗: {str(e)}")
        print(f"\n完整錯誤資訊:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    diagnose_reservoir_commands()
