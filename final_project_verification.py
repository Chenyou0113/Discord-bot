#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Discord 機器人專案最終驗證腳本
檢查所有主要功能是否正常運作
"""

import asyncio
import sys
import os
import traceback
import discord
import logging
from datetime import datetime

# 設定基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 確保可以匯入 cogs 模組
sys.path.append(os.getcwd())

class MockBot:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        
    async def wait_until_ready(self):
        pass
        
    def is_closed(self):
        return False

async def test_import_modules():
    """測試所有模組匯入"""
    print("🔍 測試模組匯入...")
    
    try:
        from cogs.info_commands_fixed_v4 import InfoCommands
        print("  ✅ info_commands_fixed_v4")
        
        from cogs.level_system import LevelSystem
        print("  ✅ level_system")
        
        from cogs.admin_commands_fixed import AdminCommands
        print("  ✅ admin_commands_fixed")
        
        from cogs.basic_commands import BasicCommands
        print("  ✅ basic_commands")
        
        from cogs.chat_commands import ChatCommands
        print("  ✅ chat_commands")
        
        from cogs.voice_system import VoiceSystem
        print("  ✅ voice_system")
        
        from cogs.monitor_system import MonitorSystem
        print("  ✅ monitor_system")
        
        return True
    except Exception as e:
        print(f"  ❌ 模組匯入失敗: {str(e)}")
        traceback.print_exc()
        return False

async def test_weather_function():
    """測試天氣預報功能"""
    print("\n🌤️ 測試天氣預報功能...")
    
    try:
        from cogs.info_commands_fixed_v4 import InfoCommands
        
        bot = MockBot()
        info_cog = InfoCommands(bot)
        
        # 模擬天氣資料
        mock_data = {
            "records": {
                "location": [
                    {
                        "locationName": "臺北市",
                        "weatherElement": [
                            {
                                "elementName": "Wx",
                                "time": [
                                    {
                                        "startTime": "2025-05-27 18:00:00",
                                        "endTime": "2025-05-28 06:00:00",
                                        "parameter": {
                                            "parameterName": "晴時多雲"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        # 替換 fetch_weather_data 方法
        async def mock_fetch_weather_data():
            return mock_data
            
        info_cog.fetch_weather_data = mock_fetch_weather_data
        
        # 測試格式化功能
        embed = await info_cog.format_weather_data("臺北市")
        
        if embed and embed.title and len(embed.fields) > 0:
            print("  ✅ 天氣預報格式化功能正常")
            print(f"     - 標題: {embed.title}")
            print(f"     - 欄位數: {len(embed.fields)}")
            
            # 如果 session 已被初始化，則關閉它
            if hasattr(info_cog, 'session') and info_cog.session and not info_cog.session.closed:
                await info_cog.session.close()
                print("  ✅ 已關閉 aiohttp 工作階段")
                
            return True
        else:
            print("  ❌ 天氣預報格式化失敗")
            return False
            
    except Exception as e:
        print(f"  ❌ 天氣預報測試失敗: {str(e)}")
        traceback.print_exc()
        return False

async def test_level_system():
    """測試等級系統"""
    print("\n📊 測試等級系統...")
    
    try:
        from cogs.level_system import LevelSystem
        
        bot = MockBot()
        level_cog = LevelSystem(bot)
        
        # 測試等級計算
        test_level = 5
        required_xp = level_cog.get_xp_for_level(test_level)
        
        if required_xp > 0:
            print(f"  ✅ 等級計算功能正常 (等級 {test_level} 需要 {required_xp} 經驗值)")
            
            # 測試用戶資料獲取
            test_user_id = 123456789
            test_guild_id = 987654321
            user_data = level_cog.get_user_data(test_user_id, test_guild_id)
            
            if user_data and 'level' in user_data and 'xp' in user_data:
                print("  ✅ 用戶資料獲取功能正常")
                return True
            else:
                print("  ❌ 用戶資料獲取異常")
                return False
        else:
            print("  ❌ 等級計算異常")
            return False
            
    except Exception as e:
        print(f"  ❌ 等級系統測試失敗: {str(e)}")
        traceback.print_exc()
        return False

def test_file_structure():
    """檢查檔案結構"""
    print("\n📁 檢查檔案結構...")
    
    required_files = [
        "bot.py",
        "requirements.txt",
        "start_bot_unified.bat",
        "cogs/info_commands_fixed_v4.py",
        "cogs/level_system.py",
        "cogs/admin_commands_fixed.py",
        "cogs/basic_commands.py",
        "cogs/chat_commands.py",
        "cogs/voice_system.py",
        "cogs/monitor_system.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("  ❌ 缺少檔案:")
        for file in missing_files:
            print(f"     - {file}")
        return False
    else:
        print("  ✅ 所有必要檔案都存在")
        return True

def test_cleanup_result():
    """檢查清理結果"""
    print("\n🧹 檢查專案清理結果...")
    
    # 檢查重複檔案是否已移動
    if os.path.exists("redundant_files") and os.path.exists("cogs/old_versions"):
        print("  ✅ 重複檔案已正確歸檔")
        
        # 計算歸檔的檔案數量
        redundant_count = len([f for f in os.listdir("redundant_files") if f.endswith('.py') or f.endswith('.bat')])
        old_versions_count = len([f for f in os.listdir("cogs/old_versions") if f.endswith('.py')])
        
        print(f"     - redundant_files: {redundant_count} 個檔案")
        print(f"     - cogs/old_versions: {old_versions_count} 個檔案")
        return True
    else:
        print("  ❌ 歸檔資料夾不存在")
        return False

async def main():
    """主測試函數"""
    print("=" * 60)
    print("Discord 機器人專案最終驗證")
    print("=" * 60)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # 執行各項測試
    test_results.append(await test_import_modules())
    test_results.append(await test_weather_function())
    test_results.append(await test_level_system())
    test_results.append(test_file_structure())
    test_results.append(test_cleanup_result())
    
    # 統計結果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 60)
    print("📋 測試結果摘要")
    print("=" * 60)
    print(f"✅ 通過測試: {passed}/{total}")
    print(f"❌ 失敗測試: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有測試通過！專案已準備就緒。")
        print("\n📝 可以使用的啟動命令:")
        print("   - start_bot_unified.bat")
        print("   - python bot.py")
    else:
        print(f"\n⚠️ 還有 {total - passed} 個問題需要解決。")
    
    print("\n✨ 專案清理和優化已完成！")

if __name__ == "__main__":
    asyncio.run(main())
