#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水庫指令載入與功能
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# 設定簡化日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_reservoir_commands():
    """測試水庫指令功能"""
    print("🏞️ 測試水庫指令載入與功能...")
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
        
        # 導入機器人模組
        print("📦 導入機器人模組...")
        from bot import CustomBot
        
        # 創建機器人實例
        print("🤖 創建機器人實例...")
        bot = CustomBot()
        
        # 檢查水庫指令是否在初始擴展中
        if 'cogs.reservoir_commands' in bot.initial_extensions:
            print("✅ 水庫指令已加入初始擴展列表")
        else:
            print("❌ 水庫指令未在初始擴展列表中")
            return False
        
        # 清理命令樹
        bot.tree.clear_commands(guild=None)
        if hasattr(bot.tree, '_global_commands'):
            bot.tree._global_commands.clear()
        if hasattr(bot.tree, '_guild_commands'):
            bot.tree._guild_commands.clear()
        
        print("✅ 命令樹清理成功")
        
        # 測試載入所有擴展
        successful_loads = 0
        failed_loads = []
        
        for extension in bot.initial_extensions:
            try:
                await bot.load_extension(extension)
                successful_loads += 1
                print(f"  ✅ {extension}")
            except Exception as e:
                failed_loads.append(extension)
                print(f"  ❌ {extension}: {str(e)}")
        
        # 檢查水庫指令是否成功載入
        if 'ReservoirCommands' in [cog.__class__.__name__ for cog in bot.cogs.values()]:
            print("✅ 水庫指令 Cog 成功載入")
        else:
            print("❌ 水庫指令 Cog 載入失敗")
        
        # 檢查指令註冊
        reservoir_commands = []
        for cmd in bot.tree._global_commands.values():
            if hasattr(cmd, 'name') and 'reservoir' in cmd.name.lower():
                reservoir_commands.append(cmd.name)
        
        if reservoir_commands:
            print(f"✅ 發現水庫相關指令: {', '.join(reservoir_commands)}")
        else:
            print("⚠️ 未發現水庫相關指令")
        
        # 測試水庫指令的 API 連接
        print("\n🔗 測試水庫 API 連接...")
        reservoir_cog = bot.get_cog('ReservoirCommands')
        if reservoir_cog:
            test_data = await reservoir_cog.get_reservoir_data()
            if test_data:
                print(f"✅ 水庫 API 連接成功，獲得 {len(test_data)} 筆資料")
                
                # 測試資料格式化
                if test_data:
                    sample_info = reservoir_cog.format_reservoir_info(test_data[0])
                    if sample_info:
                        print(f"✅ 資料格式化成功: {sample_info['name']}")
                    else:
                        print("⚠️ 資料格式化失敗")
            else:
                print("❌ 水庫 API 連接失敗")
        else:
            print("❌ 找不到水庫指令 Cog")
        
        # 檢查最終狀態
        print(f"\n📊 最終狀態:")
        print(f"  - 成功載入: {successful_loads}/{len(bot.initial_extensions)}")
        print(f"  - 載入的 Cogs: {len(bot.cogs)}")
        print(f"  - 註冊的指令: {len(bot.tree._global_commands)}")
        
        if failed_loads:
            print(f"  - 失敗的擴展: {', '.join(failed_loads)}")
        
        # 列出所有載入的 Cogs
        if bot.cogs:
            print(f"\n🎯 載入的 Cogs:")
            for i, cog_name in enumerate(bot.cogs.keys(), 1):
                print(f"  {i:2d}. {cog_name}")
        
        # 列出所有註冊的指令
        if bot.tree._global_commands:
            print(f"\n📋 註冊的指令:")
            command_names = [cmd.name for cmd in bot.tree._global_commands.values()]
            for i, cmd_name in enumerate(sorted(command_names), 1):
                print(f"  {i:2d}. {cmd_name}")
        
        # 清理資源
        await bot.close()
        
        # 判斷成功標準
        success = (successful_loads == len(bot.initial_extensions) and 
                  len(bot.cogs) == len(bot.initial_extensions) and
                  len(bot.tree._global_commands) > 0 and
                  'ReservoirCommands' in [cog.__class__.__name__ for cog in bot.cogs.values()])
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 水庫指令測試成功！")
            print("✅ 所有功能載入正常")
            print("🏞️ 水庫查詢指令已準備就緒")
            print("🚀 機器人可以安全啟動")
        else:
            print("⚠️ 部分測試未通過")
            if failed_loads:
                print(f"  失敗的擴展: {', '.join(failed_loads)}")
        
        return success
        
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_reservoir_commands())
    
    print("\n🎯 下一步:")
    if success:
        print("  ✅ 水庫指令功能完成")
        print("  🤖 可以使用 safe_start_bot.bat 啟動機器人")
        print("  📝 可用的水庫指令:")
        print("     - /reservoir: 查詢水庫水情")
        print("     - /reservoir_list: 顯示水庫列表")
    else:
        print("  ❌ 需要檢查上方錯誤訊息並進行修復")
