#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新增的水庫指令功能
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# 設定簡化日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_new_reservoir_commands():
    """測試新增的水庫指令功能"""
    print("🆕 測試新增的水庫指令功能...")
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
            if hasattr(cmd, 'name') and ('reservoir' in cmd.name.lower() or 'water' in cmd.name.lower()):
                reservoir_commands.append(cmd.name)
        
        print(f"🔍 發現水庫/水利相關指令: {reservoir_commands}")
        
        # 檢查新指令
        expected_new_commands = ['reservoir_info', 'water_cameras']
        new_commands_found = []
        
        for cmd in expected_new_commands:
            if cmd in reservoir_commands:
                new_commands_found.append(cmd)
                print(f"✅ 新指令 {cmd} 成功註冊")
            else:
                print(f"❌ 新指令 {cmd} 未找到")
        
        # 測試新 API 連接
        print("\n🔗 測試新 API 連接...")
        reservoir_cog = bot.get_cog('ReservoirCommands')
        if reservoir_cog:
            # 測試水庫基本資料 API
            basic_data = await reservoir_cog.get_reservoir_basic_info()
            if basic_data:
                print(f"✅ 水庫基本資料 API 連接成功，獲得 {len(basic_data)} 筆資料")
                
                # 測試資料格式化
                if basic_data:
                    sample_info = reservoir_cog.format_reservoir_basic_info(basic_data[0])
                    if sample_info:
                        print(f"✅ 基本資料格式化成功: {sample_info['name']}")
                        print(f"   📍 位置: {sample_info['location']}")
                        print(f"   🏛️ 壩型: {sample_info['dam_type']}")
                        print(f"   📏 壩高: {sample_info['height']} 公尺")
                    else:
                        print("⚠️ 基本資料格式化失敗")
            else:
                print("❌ 水庫基本資料 API 連接失敗")
            
            # 測試水利防災影像 API
            image_data = await reservoir_cog.get_water_disaster_images()
            if image_data:
                print(f"✅ 水利防災影像 API 連接成功，獲得 {len(image_data)} 筆資料")
                
                # 測試資料格式化
                if image_data:
                    sample_info = reservoir_cog.format_water_image_info(image_data[0])
                    if sample_info:
                        print(f"✅ 防災影像格式化成功: {sample_info['station_name']}")
                        print(f"   📍 位置: {sample_info['location']}")
                        print(f"   🌊 河川: {sample_info['river']}")
                        print(f"   📡 狀態: {sample_info['status']}")
                    else:
                        print("⚠️ 防災影像格式化失敗")
            else:
                print("❌ 水利防災影像 API 連接失敗")
            
            # 測試原有 API 仍正常
            water_data = await reservoir_cog.get_reservoir_data()
            operation_data = await reservoir_cog.get_reservoir_operation_data()
            
            if water_data and operation_data:
                print("✅ 原有水庫 API 仍正常運作")
            else:
                print("⚠️ 部分原有 API 連接異常")
        else:
            print("❌ 找不到水庫指令 Cog")
        
        # 檢查所有註冊的指令
        print(f"\n📋 所有註冊的指令數量: {len(bot.tree._global_commands)}")
        
        expected_all_commands = ['reservoir', 'reservoir_list', 'reservoir_operation', 'reservoir_info', 'water_cameras']
        missing_commands = []
        for cmd in expected_all_commands:
            if cmd not in reservoir_commands:
                missing_commands.append(cmd)
        
        if not missing_commands:
            print("✅ 所有預期的水庫指令都已註冊")
        else:
            print(f"⚠️ 缺少指令: {missing_commands}")
        
        # 清理資源
        await bot.close()
        
        # 判斷成功標準
        success = (len(new_commands_found) == len(expected_new_commands) and 
                  basic_data is not None and
                  image_data is not None)
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 新增水庫指令測試成功！")
            print("✅ 所有新功能載入正常")
            print("🆕 新增指令已準備就緒")
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
    success = asyncio.run(test_new_reservoir_commands())
    
    print("\n🎯 下一步:")
    if success:
        print("  ✅ 新增水庫功能完成")
        print("  🤖 可以使用 safe_start_bot.bat 啟動機器人")
        print("  📝 完整的水庫指令集:")
        print("     - /reservoir: 查詢水庫水情")
        print("     - /reservoir_list: 顯示水庫列表")
        print("     - /reservoir_operation: 查詢水庫營運狀況")
        print("     - /reservoir_info: 查詢水庫基本資料 ⭐ 新增")
        print("     - /water_cameras: 查詢水利防災監控影像 ⭐ 新增")
    else:
        print("  ❌ 需要檢查上方錯誤訊息並進行修復")
