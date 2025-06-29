#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新的天氣查詢功能
"""

import asyncio
import sys
import os

# 將 cogs 目錄加入路徑
sys.path.insert(0, os.path.join(os.getcwd(), 'cogs'))

async def test_weather_commands():
    """測試天氣指令功能"""
    print("🌤️ 測試天氣查詢指令功能")
    print("=" * 50)
    
    try:
        # 導入天氣指令模組
        from weather_commands import WeatherCommands
        
        # 建立模擬 bot
        class MockBot:
            pass
        
        mock_bot = MockBot()
        weather_cog = WeatherCommands(mock_bot)
        
        print("✅ WeatherCommands 實例建立成功")
        
        # 測試 API 資料獲取
        print("\n📡 測試 API 資料獲取...")
        data = await weather_cog.fetch_weather_observation_data()
        
        if data:
            print("✅ API 資料獲取成功")
            
            stations = data.get('records', {}).get('Station', [])
            print(f"📊 獲得 {len(stations)} 個氣象測站資料")
            
            # 測試搜尋功能
            print("\n🔍 測試搜尋功能...")
            
            search_terms = ["板橋", "淡水", "桃園"]
            for term in search_terms:
                matches = weather_cog.search_weather_stations(stations, term)
                print(f"搜尋 '{term}': 找到 {len(matches)} 個結果")
                
                if matches:
                    for match in matches[:1]:  # 顯示第一個結果
                        name = match.get('StationName', 'N/A')
                        station_id = match.get('StationId', 'N/A')
                        weather = match.get('WeatherElement', {})
                        temp = weather.get('AirTemperature', 'N/A')
                        print(f"  • {name} ({station_id}) - 溫度: {temp}°C")
            
            # 測試 Embed 格式化
            print("\n📝 測試 Embed 格式化...")
            test_stations = weather_cog.search_weather_stations(stations, "板橋")
            
            if test_stations:
                embed = weather_cog.format_weather_data_embed(test_stations, "板橋")
                print("✅ Embed 格式化成功")
                print(f"標題: {embed.title}")
                print(f"顏色: {embed.color}")
                print(f"欄位數量: {len(embed.fields)}")
                
                # 顯示第一個欄位的內容
                if embed.fields:
                    first_field = embed.fields[0]
                    print(f"第一個欄位: {first_field.name}")
                    print(f"內容預覽: {first_field.value[:100]}...")
            else:
                print("❌ 沒有找到板橋測站")
            
        else:
            print("❌ API 資料獲取失敗")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print(f"開始時間: {asyncio.get_event_loop().time()}")
    
    success = asyncio.run(test_weather_commands())
    
    if success:
        print("\n🎉 天氣查詢功能測試成功！")
        print("💡 現在可以使用 /weather 指令查詢天氣了")
    else:
        print("\n❌ 測試失敗，需要修復問題")

if __name__ == "__main__":
    main()
