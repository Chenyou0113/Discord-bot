#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
氣象站觀測資料功能測試
測試新添加的氣象站觀測資料指令
"""

import sys
import os
import asyncio
import logging

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_weather_station_functionality():
    """測試氣象站觀測資料功能"""
    print("🌡️ 測試氣象站觀測資料功能")
    print("=" * 60)
    
    try:
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        from unittest.mock import MagicMock, AsyncMock
        import aiohttp
        import ssl
        
        # 創建模擬 Discord 交互
        mock_interaction = MagicMock()
        mock_interaction.response = MagicMock()
        mock_interaction.response.defer = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        
        # 創建模擬 bot
        mock_bot = MagicMock()
        mock_bot.user = MagicMock()
        mock_bot.user.id = 123456789
        mock_bot.loop = asyncio.get_event_loop()
        mock_bot.wait_until_ready = AsyncMock()
        
        # 初始化 InfoCommands
        info_commands = InfoCommands(mock_bot)
        
        # 手動設置 session
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=100)
        timeout = aiohttp.ClientTimeout(total=30)
        info_commands.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
        print("✅ 測試環境準備完成")
        
        # 測試 1: 獲取氣象站資料
        print("\n📊 測試 1: 獲取氣象站觀測資料...")
        station_data = await info_commands.fetch_weather_station_data()
        if station_data:
            print("✅ 成功獲取氣象站觀測資料")
            print(f"   資料結構: {list(station_data.keys()) if isinstance(station_data, dict) else 'Not dict'}")
            
            if 'records' in station_data and 'Station' in station_data['records']:
                stations = station_data['records']['Station']
                print(f"   找到 {len(stations)} 個氣象站")
                
                # 顯示前3個測站的基本資訊
                for i, station in enumerate(stations[:3]):
                    station_name = station.get('StationName', '未知')
                    station_id = station.get('StationId', '未知')
                    print(f"   測站{i+1}: {station_name} ({station_id})")
            else:
                print("   ❌ 資料結構不符合預期")
                return False
        else:
            print("❌ 無法獲取氣象站觀測資料")
            return False
        
        # 測試 2: 格式化全台概況
        print("\n🗺️ 測試 2: 格式化全台概況...")
        overview_embed = await info_commands.format_weather_station_data()
        
        if overview_embed:
            print("✅ 成功生成全台概況 Embed")
            print(f"   標題: {overview_embed.title}")
            print(f"   描述: {overview_embed.description}")
            print(f"   欄位數量: {len(overview_embed.fields)}")
        else:
            print("❌ 無法生成全台概況 Embed")
            return False
        
        # 測試 3: 指定地區查詢
        print("\n📍 測試 3: 指定地區查詢...")
        location_embed = await info_commands.format_weather_station_data(location="台北")
        
        if location_embed:
            print("✅ 成功生成台北地區 Embed")
            print(f"   標題: {location_embed.title}")
            print(f"   描述: {location_embed.description}")
        else:
            print("❌ 無法生成台北地區 Embed")
            return False
        
        # 測試 4: Discord 指令測試
        print("\n💬 測試 4: Discord 指令測試...")
        
        # 測試全台概況指令
        await info_commands.weather_station.callback(info_commands, mock_interaction)
        
        if mock_interaction.followup.send.called:
            call_args = mock_interaction.followup.send.call_args
            if call_args and len(call_args[1]) > 0 and 'embed' in call_args[1]:
                embed = call_args[1]['embed']
                print("✅ 氣象站指令成功生成 Discord Embed")
                print(f"   標題: {embed.title}")
                print(f"   欄位數量: {len(embed.fields)}")
            else:
                print("❌ 氣象站指令沒有生成有效的 Discord Embed")
                return False
        else:
            print("❌ 氣象站指令沒有發送任何訊息")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 所有氣象站功能測試通過！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if 'info_commands' in locals() and hasattr(info_commands, 'session'):
            if info_commands.session and not info_commands.session.closed:
                await info_commands.session.close()
                print("🧹 已清理網路會話資源")

async def main():
    """主函數"""
    success = await test_weather_station_functionality()
    
    if success:
        print("\n🎯 測試結果: ✅ 氣象站觀測資料功能完全正常")
        print("💡 可以在 Discord 中使用 /weather_station 指令了！")
        print("\n📋 指令使用方式:")
        print("   /weather_station - 查看全台主要氣象站概況")
        print("   /weather_station location:台北 - 查看台北地區氣象站")
        print("   /weather_station station_id:466920 - 查看特定測站資料")
    else:
        print("\n🎯 測試結果: ❌ 氣象站功能還有問題需要解決")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
