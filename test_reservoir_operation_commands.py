#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水庫營運狀況指令
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# 設定簡化日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_reservoir_operation_commands():
    """測試水庫營運狀況指令功能"""
    print("🏗️ 測試水庫營運狀況指令...")
    print("=" * 50)
    
    try:
        # 切換工作目錄
        os.chdir(r"c:\Users\xiaoy\Desktop\Discord bot")
        
        # 載入環境變數
        load_dotenv()
        
        # 檢查必要的環境變數
        if not os.getenv('DISCORD_TOKEN'):
            print("❌ 找不到 DISCORD_TOKEN")
            return False
        
        # 測試水庫模組導入
        print("📦 測試水庫模組導入...")
        import cogs.reservoir_commands
        print("✅ 水庫模組導入成功")
        
        # 導入機器人模組
        print("📦 導入機器人模組...")
        from bot import CustomBot
        
        # 創建機器人實例
        print("🤖 創建機器人實例...")
        bot = CustomBot()
        
        # 清理命令樹
        bot.tree.clear_commands(guild=None)
        if hasattr(bot.tree, '_global_commands'):
            bot.tree._global_commands.clear()
        if hasattr(bot.tree, '_guild_commands'):
            bot.tree._guild_commands.clear()
        
        print("✅ 命令樹清理成功")
        
        # 載入水庫指令擴展
        try:
            await bot.load_extension('cogs.reservoir_commands')
            print("✅ 水庫指令擴展載入成功")
        except Exception as e:
            print(f"❌ 水庫指令擴展載入失敗: {str(e)}")
            return False
        
        # 檢查指令註冊
        reservoir_commands = []
        for cmd in bot.tree._global_commands.values():
            if hasattr(cmd, 'name') and 'reservoir' in cmd.name.lower():
                reservoir_commands.append(cmd.name)
        
        print(f"🔍 發現水庫相關指令: {reservoir_commands}")
        
        # 檢查是否包含新的營運狀況指令
        if 'reservoir_operation' in reservoir_commands:
            print("✅ 水庫營運狀況指令成功註冊")
        else:
            print("❌ 水庫營運狀況指令未找到")
        
        # 測試水庫營運 API 連接
        print("\n🔗 測試水庫營運 API 連接...")
        reservoir_cog = bot.get_cog('ReservoirCommands')
        if reservoir_cog:
            # 測試營運資料 API
            operation_data = await reservoir_cog.get_reservoir_operation_data()
            if operation_data:
                print(f"✅ 水庫營運 API 連接成功，獲得 {len(operation_data)} 筆資料")
                
                # 測試資料格式化
                if operation_data:
                    sample_info = reservoir_cog.format_reservoir_operation_info(operation_data[0])
                    if sample_info:
                        print(f"✅ 營運資料格式化成功: {sample_info['name']}")
                        print(f"   📊 蓄水量: {sample_info['capacity']} 萬立方公尺")
                        print(f"   💧 水位: {sample_info['water_level']} 公尺")
                        print(f"   🌧️ 降雨量: {sample_info['rainfall']} 毫米")
                    else:
                        print("⚠️ 營運資料格式化失敗")
            else:
                print("❌ 水庫營運 API 連接失敗")
            
            # 測試原有的水情 API
            water_data = await reservoir_cog.get_reservoir_data()
            if water_data:
                print(f"✅ 水庫水情 API 仍正常，獲得 {len(water_data)} 筆資料")
            else:
                print("⚠️ 水庫水情 API 連接異常")
        else:
            print("❌ 找不到水庫指令 Cog")
        
        # 檢查所有註冊的指令
        print(f"\n📋 所有註冊的指令數量: {len(bot.tree._global_commands)}")
        
        expected_commands = ['reservoir', 'reservoir_list', 'reservoir_operation']
        missing_commands = []
        for cmd in expected_commands:
            if cmd not in reservoir_commands:
                missing_commands.append(cmd)
        
        if not missing_commands:
            print("✅ 所有預期的水庫指令都已註冊")
        else:
            print(f"⚠️ 缺少指令: {missing_commands}")
        
        # 清理資源
        await bot.close()
        
        # 判斷成功標準
        success = (len(reservoir_commands) >= 3 and 
                  'reservoir_operation' in reservoir_commands and
                  operation_data is not None)
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 水庫營運狀況指令測試成功！")
            print("✅ 所有功能載入正常")
            print("🏗️ 水庫營運查詢指令已準備就緒")
            print("🚀 機器人可以安全啟動")
        else:
            print("⚠️ 部分測試未通過")
        
        return success
        
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_reservoir_operation_commands())
    
    print("\n🎯 下一步:")
    if success:
        print("  ✅ 水庫營運狀況功能完成")
        print("  🤖 可以使用 safe_start_bot.bat 啟動機器人")
        print("  📝 新增的水庫指令:")
        print("     - /reservoir: 查詢水庫水情")
        print("     - /reservoir_list: 顯示水庫列表")
        print("     - /reservoir_operation: 查詢水庫營運狀況 ⭐ 新增")
    else:
        print("  ❌ 需要檢查上方錯誤訊息並進行修復")
