#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速驗證修復是否成功
僅測試 setup_hook 而不實際連接 Discord
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# 設定簡化日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def quick_verification():
    """快速驗證修復"""
    print("🔍 快速驗證終極修復...")
    print("=" * 40)
    
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
        
        # 檢查初始狀態
        print(f"📋 初始狀態:")
        print(f"  - Cogs: {len(bot.cogs)}")
        print(f"  - 擴展: {len([e for e in bot.extensions.keys() if e.startswith('cogs.')])}")
        print(f"  - 指令: {len(bot.tree._global_commands)}")
        
        # 手動執行 setup_hook 的關鍵部分（不連接 Discord）
        print("⚙️ 執行設置流程測試...")
        
        # 模擬清理過程
        bot.tree.clear_commands(guild=None)
        if hasattr(bot.tree, '_global_commands'):
            bot.tree._global_commands.clear()
        if hasattr(bot.tree, '_guild_commands'):
            bot.tree._guild_commands.clear()
        
        print("✅ 命令樹清理成功")
        
        # 測試載入擴展
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
            
            # 特別檢查水庫指令
            reservoir_commands = [cmd for cmd in command_names if 'reservoir' in cmd.lower()]
            if reservoir_commands:
                print(f"\n🏞️ 水庫相關指令: {', '.join(reservoir_commands)}")
                
                # 檢查是否包含新的營運狀況指令
                if 'reservoir_operation' in reservoir_commands:
                    print("✅ 水庫營運狀況指令已成功註冊")
                else:
                    print("⚠️ 水庫營運狀況指令未找到")
        
        # 清理資源
        await bot.close()
        
        # 判斷成功標準
        success = (successful_loads == len(bot.initial_extensions) and 
                  len(bot.cogs) == len(bot.initial_extensions) and
                  len(bot.tree._global_commands) > 0)
        
        print("\n" + "=" * 40)
        if success:
            print("✅ 驗證成功！")
            print("🎉 所有擴展載入正常，無指令重複註冊錯誤")
            print("🚀 機器人已準備好正式啟動")
        else:
            print("⚠️ 部分驗證未通過")
            if failed_loads:
                print(f"  失敗的擴展: {', '.join(failed_loads)}")
        
        return success
        
    except Exception as e:
        print(f"❌ 驗證過程發生錯誤: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_verification())
    
    print("\n🎯 下一步:")
    if success:
        print("  可以安全使用 safe_start_bot.bat 啟動機器人")
    else:
        print("  需要檢查上方錯誤訊息並進行修復")
