#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查所有可用的 Discord 指令
"""

import sys
import os

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_all_commands():
    """檢查所有可用指令"""
    print("🎯 Discord 機器人指令清單")
    print("=" * 60)
    
    commands_found = []
    
    try:
        # 檢查 ReservoirCommands
        print("💧 水利相關指令 (ReservoirCommands):")
        from cogs.reservoir_commands import ReservoirCommands
        reservoir_cog = ReservoirCommands(None)
        
        reservoir_commands = [
            ('reservoir_list', '查詢水庫資訊'),
            ('water_disaster_cameras', '水利監視器'),
            ('river_levels', '河川水位'),
            ('highway_cameras', '公路監視器'),
            ('check_permissions', '權限檢查')
        ]
        
        for cmd_name, description in reservoir_commands:
            if hasattr(reservoir_cog, cmd_name):
                print(f"   ✅ /{cmd_name} - {description}")
                commands_found.append(f"/{cmd_name}")
            else:
                print(f"   ❌ /{cmd_name} - {description} (未找到)")
        
    except Exception as e:
        print(f"   ❌ ReservoirCommands 載入失敗: {str(e)}")
    
    try:
        # 檢查 WeatherCommands  
        print(f"\n🌤️ 天氣相關指令 (WeatherCommands):")
        from cogs.weather_commands import WeatherCommands
        weather_cog = WeatherCommands(None)
        
        if hasattr(weather_cog, 'weather'):
            print(f"   ✅ /weather - 天氣查詢")
            commands_found.append("/weather")
        else:
            print(f"   ❌ /weather - 天氣查詢 (未找到)")
        
    except Exception as e:
        print(f"   ❌ WeatherCommands 載入失敗: {str(e)}")
    
    try:
        # 檢查 InfoCommands
        print(f"\nℹ️ 基本資訊指令 (InfoCommands):")
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        info_cog = InfoCommands(None)
        
        info_commands = [
            ('ping', '測試機器人回應'),
            ('help', '幫助資訊'),
            ('about', '關於機器人')
        ]
        
        for cmd_name, description in info_commands:
            if hasattr(info_cog, cmd_name):
                print(f"   ✅ /{cmd_name} - {description}")
                commands_found.append(f"/{cmd_name}")
            else:
                print(f"   ❌ /{cmd_name} - {description} (未找到)")
        
    except Exception as e:
        print(f"   ❌ InfoCommands 載入失敗: {str(e)}")
    
    # 總結
    print(f"\n" + "=" * 60)
    print("📊 指令統計")
    print("=" * 60)
    print(f"✅ 找到 {len(commands_found)} 個可用指令:")
    
    for cmd in sorted(commands_found):
        print(f"   {cmd}")
    
    print(f"\n💡 同步指令到 Discord:")
    print("   1. 確保 .env 檔案中有 DISCORD_TOKEN")
    print("   2. 執行: python sync_commands.py")
    print("   3. 或執行: python setup_bot.py")
    
    print(f"\n🎯 重要提醒:")
    print("   - 機器人需要 '使用斜線指令' 權限")
    print("   - 機器人需要 '嵌入連結' 權限 (顯示圖片)")
    print("   - 使用 /check_permissions 檢查權限狀態")

def main():
    """主函數"""
    check_all_commands()

if __name__ == "__main__":
    main()
