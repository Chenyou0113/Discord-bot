#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的縣市問題診斷
"""

import aiohttp
import asyncio
import json
import ssl

async def simple_county_check():
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    text = await response.text()
                    if text.startswith('\ufeff'):
                        text = text[1:]
                    
                    data = json.loads(text)
                    print(f"取得 {len(data)} 筆資料")
                    
                    # 檢查前5筆資料的縣市欄位
                    for i, item in enumerate(data[:5]):
                        print(f"\n=== 第 {i+1} 筆資料 ===")
                        county_field = item.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '找不到縣市欄位')
                        station_name = item.get('VideoSurveillanceStationName', '未知站名')
                        print(f"監控站: {station_name}")
                        print(f"縣市欄位: '{county_field}'")
                        
                        # 顯示所有可能的縣市相關欄位
                        for key, value in item.items():
                            if any(keyword in key.lower() for keyword in ['count', 'cit', 'location', 'area']):
                                print(f"  {key}: {value}")
                    
                    return True
                else:
                    print(f"API 請求失敗: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"錯誤: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(simple_county_check())
    print(f"\n診斷完成: {'成功' if result else '失敗'}")
