#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
終極修復驗證測試
測試指令重複註冊問題是否已徹底解決
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# 設定簡化日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_ultimate_fix():
    """測試終極修復方案"""
    print("🧪 開始終極修復驗證測試...")
    print("=" * 60)
    
    try:
        # 載入環境變數
        load_dotenv()
        
        # 檢查必要的環境變數
        discord_token = os.getenv('DISCORD_TOKEN')
        if not discord_token:
            print("❌ 找不到 DISCORD_TOKEN，無法進行測試")
            return False
        
        print("✅ 環境變數檢查通過")
        
        # 導入機器人模組
        print("📦 導入機器人模組...")
        from bot import CustomBot
        
        # 創建機器人實例
        print("🤖 創建機器人實例...")
        bot = CustomBot()
        
        # 手動執行 setup_hook (不連接到 Discord)
        print("⚙️ 執行設置流程...")
        await bot.setup_hook()
        
        # 驗證結果
        print("\n📊 驗證結果:")
        print(f"  載入的 Cogs: {len(bot.cogs)}")
        print(f"  載入記錄: {len(bot._loaded_cogs)}")
        print(f"  擴展字典: {len([e for e in bot.extensions.keys() if e.startswith('cogs.')])}")
        
        # 檢查 Cogs
        if bot.cogs:
            print(f"  📋 已載入的 Cogs:")
            for cog_name in bot.cogs.keys():
                print(f"    - {cog_name}")
        
        # 檢查指令
        all_commands = bot.tree._global_commands
        if all_commands:
            print(f"  📋 註冊的指令 ({len(all_commands)}):")
            command_names = [cmd.name for cmd in all_commands.values()]
            for i, cmd_name in enumerate(sorted(command_names), 1):
                print(f"    {i:2d}. {cmd_name}")
        
        # 清理資源
        await bot.close()
        
        # 判斷測試結果
        expected_cogs = 12  # 預期的 Cog 數量
        success = (len(bot.cogs) == expected_cogs and 
                  len(bot._loaded_cogs) == expected_cogs and
                  len(all_commands) > 0)
        
        print("\n" + "=" * 60)
        if success:
            print("✅ 終極修復驗證測試 - 成功！")
            print("🎉 所有 Cogs 載入正常，沒有指令重複註冊錯誤")
            print("🚀 機器人已準備好正式啟動")
        else:
            print("❌ 終極修復驗證測試 - 部分問題")
            print(f"   預期 Cogs: {expected_cogs}, 實際: {len(bot.cogs)}")
            print("🔧 可能需要進一步調整")
        
        return success
        
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    # 切換到正確的工作目錄
    os.chdir(r"c:\Users\xiaoy\Desktop\Discord bot")
    
    # 執行測試
    success = asyncio.run(test_ultimate_fix())
    
    if success:
        print("\n🎯 下一步:")
        print("  執行 safe_start_bot.bat 或 start_weather_bot.bat 啟動機器人")
    else:
        print("\n🔧 建議:")
        print("  檢查上方的錯誤訊息並進行相應的修復")
