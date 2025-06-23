#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單氣象站API檢查
"""

import sys
import os
import asyncio
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def simple_check():
    from cogs.info_commands_fixed_v4_clean import InfoCommands
    from unittest.mock import MagicMock, AsyncMock
    import aiohttp
    import ssl
    
    mock_bot = MagicMock()
    mock_bot.user = MagicMock()
    mock_bot.user.id = 123456789
    mock_bot.loop = asyncio.get_event_loop()
    mock_bot.wait_until_ready = AsyncMock()
    
    info_commands = InfoCommands(mock_bot)
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context, limit=100)
    timeout = aiohttp.ClientTimeout(total=30)
    info_commands.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    
    try:
        data = await info_commands.fetch_weather_station_data()
        
        if data and 'records' in data:
            records = data['records']
            print(f"records keys: {list(records.keys())}")
            
            if 'Station' in records:
                stations = records['Station']
                print(f"Found {len(stations)} stations")
                
                if len(stations) > 0:
                    first = stations[0]
                    print("First station keys:")
                    for key in first.keys():
                        print(f"  {key}: {type(first[key])}")
                        
                    # 儲存第一筆完整資料到檔案
                    with open('sample_station_data.json', 'w', encoding='utf-8') as f:
                        json.dump(first, f, ensure_ascii=False, indent=2)
                    print("完整資料已儲存到 sample_station_data.json")
        
    finally:
        if info_commands.session and not info_commands.session.closed:
            await info_commands.session.close()

if __name__ == "__main__":
    asyncio.run(simple_check())
