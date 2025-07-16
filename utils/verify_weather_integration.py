#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證天氣指令是否正確整合到機器人中
"""

import os
import re

def check_weather_commands_integration():
    """檢查天氣指令整合狀況"""
    print("🔍 檢查天氣指令整合狀況")
    print("=" * 50)
    
    # 檢查 weather_commands.py 檔案
    weather_file = "cogs/weather_commands.py"
    
    if not os.path.exists(weather_file):
        print("❌ weather_commands.py 檔案不存在")
        return False
    
    print("✅ weather_commands.py 檔案存在")
    
    # 讀取檔案內容
    with open(weather_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查重要元素
    checks = [
        ("WeatherCommands 類別", "class WeatherCommands"),
        ("setup 函數", "async def setup(bot)"),
        ("天氣查詢指令", "@app_commands.command(name=\"weather\""),
        ("fetch_weather_observation_data 方法", "async def fetch_weather_observation_data"),
        ("search_weather_stations 方法", "def search_weather_stations"),
        ("format_weather_data_embed 方法", "def format_weather_data_embed"),
        ("SSL 設定", "ssl_context.check_hostname = False"),
        ("O-A0001-001 API", "O-A0001-001")
    ]
    
    print("\n📋 功能檢查:")
    for check_name, pattern in checks:
        if pattern in content:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
    
    # 檢查機器人載入
    bot_file = "bot.py"
    if os.path.exists(bot_file):
        with open(bot_file, 'r', encoding='utf-8') as f:
            bot_content = f.read()
        
        print(f"\n🤖 機器人整合檢查:")
        if "'cogs.weather_commands'" in bot_content:
            print("✅ weather_commands 已載入到機器人")
        else:
            print("❌ weather_commands 未載入到機器人")
    
    # 統計指令數量
    weather_commands = re.findall(r'@app_commands\.command\(name="([^"]+)"', content)
    print(f"\n📊 天氣相關指令統計:")
    for i, cmd in enumerate(weather_commands, 1):
        print(f"  {i}. /{cmd}")
    
    print(f"\n📈 總共找到 {len(weather_commands)} 個天氣指令")
    
    return True

def show_weather_command_usage():
    """顯示天氣指令使用方式"""
    print("\n" + "=" * 50)
    print("💡 天氣指令使用方式")
    print("=" * 50)
    
    usage_examples = [
        ("基本天氣查詢", "/weather", "顯示熱門地點的天氣資訊"),
        ("指定地點查詢", "/weather 板橋", "查詢板橋的天氣資訊"),
        ("多個地點查詢", "/weather 台北", "查詢包含'台北'的所有測站"),
        ("測站資料查詢", "/weather_station 板橋", "查詢測站基本資料"),
        ("縣市測站查詢", "/weather_station_by_county 新北市", "查詢特定縣市的測站"),
        ("測站詳細資訊", "/weather_station_info C0AJ80", "查詢特定測站的詳細資訊")
    ]
    
    for title, command, description in usage_examples:
        print(f"🌤️ {title}")
        print(f"   指令: {command}")
        print(f"   說明: {description}")
        print()

def main():
    """主函數"""
    success = check_weather_commands_integration()
    
    if success:
        show_weather_command_usage()
        
        print("=" * 50)
        print("🎯 下一步建議:")
        print("  1. 啟動機器人測試天氣指令")
        print("  2. 使用 /weather 指令查詢天氣")
        print("  3. 測試不同地點的查詢功能")
        print("=" * 50)
    else:
        print("❌ 整合檢查失敗，需要修復問題")

if __name__ == "__main__":
    main()
