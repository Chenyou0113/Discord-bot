#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
氣象站API資料結構檢查
檢查氣象站API返回的實際資料結構
"""

import sys
import os
import asyncio
import logging
import json

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_weather_station_api():
    """檢查氣象站API資料結構"""
    print("🔍 檢查氣象站API資料結構")
    print("=" * 50)
    
    try:
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        from unittest.mock import MagicMock, AsyncMock
        import aiohttp
        import ssl
        
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
        
        # 獲取資料
        station_data = await info_commands.fetch_weather_station_data()
        
        if station_data:
            print("✅ 成功獲取資料")
            print(f"✅ 頂層結構: {list(station_data.keys())}")
            
            # 檢查 records 是否存在
            if 'records' in station_data:
                records = station_data['records']
                print(f"✅ records 結構: {list(records.keys()) if isinstance(records, dict) else type(records)}")
                
                # 檢查 location 資料
                if 'location' in records:
                    locations = records['location']
                    print(f"✅ 找到 {len(locations)} 個測站")
                    if len(locations) > 0:
                        first_station = locations[0]
                        print(f"✅ 第一個測站結構: {list(first_station.keys())}")
                        print(f"✅ 測站名稱: {first_station.get('StationName', 'N/A')}")
                        print(f"✅ 測站ID: {first_station.get('StationId', 'N/A')}")
                        
                        # 顯示完整的第一個測站資料
                        print("📋 完整測站資料:")
                        for key, value in first_station.items():
                            if isinstance(value, dict):
                                print(f"   {key}: {list(value.keys())}")
                            else:
                                print(f"   {key}: {value}")
                        
                        # 檢查觀測時間結構
                        if 'ObsTime' in first_station:
                            print(f"✅ ObsTime: {first_station['ObsTime']}")
                        
                        # 檢查主要氣象要素
                        weather_fields = ['AirTemperature', 'RelativeHumidity', 'AirPressure', 'WindDirection', 'WindSpeed']
                        for field in weather_fields:
                            if field in first_station:
                                print(f"✅ {field}: {first_station[field]}")
                            else:
                                print(f"❌ 缺少 {field}")
                    else:
                        print("❌ locations 是空的")
                else:
                    print("❌ records 中沒有 location")
                    print(f"   records 的實際內容: {list(records.keys())}")
            else:
                print("❌ 沒有找到 records")
                
                # 檢查是否有 result 結構
                if 'result' in station_data:
                    result = station_data['result']
                    print(f"✅ result 結構: {list(result.keys()) if isinstance(result, dict) else type(result)}")
                    
                    if 'records' in result:
                        records = result['records']
                        print(f"✅ result.records 結構: {list(records.keys()) if isinstance(records, dict) else type(records)}")
        else:
            print("❌ 無法獲取資料")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 檢查過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if 'info_commands' in locals() and hasattr(info_commands, 'session'):
            if info_commands.session and not info_commands.session.closed:
                await info_commands.session.close()

async def main():
    """主函數"""
    success = await check_weather_station_api()
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
