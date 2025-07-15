#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水位查詢功能
"""

import aiohttp
import asyncio
import json
import ssl
from datetime import datetime

async def test_water_level_api():
    """測試水位查詢API"""
    print("🚀 開始測試水位查詢API...")
    
    # 設定SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=2D09DB8B-6A1B-485E-88B5-923A462F475C"
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📡 正在獲取API資料...")
            async with session.get(url, ssl=ssl_context) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API回應成功，資料筆數: {len(data)}")
                    
                    # 顯示前3筆資料
                    print("\n📊 前3筆資料範例:")
                    for i, item in enumerate(data[:3]):
                        print(f"\n--- 資料 {i+1} ---")
                        for key, value in item.items():
                            print(f"  {key}: {value}")
                    
                    # 測試縣市統計
                    counties = {}
                    for item in data:
                        county = item.get('StationTown', '未知')
                        if county not in counties:
                            counties[county] = 0
                        counties[county] += 1
                    
                    print(f"\n📍 縣市統計:")
                    for county, count in sorted(counties.items()):
                        print(f"  {county}: {count} 個測站")
                    
                    # 測試河川統計
                    rivers = {}
                    for item in data:
                        river = item.get('BasinName', '未知')
                        if river not in rivers:
                            rivers[river] = 0
                        rivers[river] += 1
                    
                    print(f"\n🏞️ 河川統計:")
                    for river, count in sorted(rivers.items()):
                        print(f"  {river}: {count} 個測站")
                    
                    return True
                else:
                    print(f"❌ API回應失敗: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

async def main():
    """主函數"""
    print("=" * 50)
    print("🌊 水位查詢功能測試")
    print("=" * 50)
    
    success = await test_water_level_api()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 測試完成！水位查詢功能正常")
    else:
        print("❌ 測試失敗！請檢查API或網路連接")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
