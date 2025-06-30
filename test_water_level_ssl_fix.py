#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水位查詢SSL修復
"""

import sys
import os
import asyncio
import ssl
import aiohttp
from datetime import datetime

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_water_level_ssl_fix():
    """測試水位查詢SSL修復"""
    print("🔧 測試水位查詢SSL修復...")
    print("=" * 50)
    
    try:
        # 導入修復後的模組
        from cogs.reservoir_commands import ReservoirCommands
        print("✅ ReservoirCommands 模組導入成功")
        
        # 模擬機器人
        class MockBot:
            pass
        
        # 創建實例
        bot = MockBot()
        reservoir_cog = ReservoirCommands(bot)
        print("✅ ReservoirCommands 實例創建成功")
        
        # 測試水位資料獲取
        print("\n🌊 測試水位資料獲取...")
        water_data = await reservoir_cog.get_water_level_data()
        
        if water_data:
            print(f"✅ 成功獲取 {len(water_data)} 筆水位資料")
            
            # 顯示前3筆資料
            print("\n📊 前3筆資料範例:")
            for i, data in enumerate(water_data[:3]):
                station_name = data.get('StationName', 'N/A')
                basin_name = data.get('BasinName', 'N/A')
                station_town = data.get('StationTown', 'N/A')
                water_level = data.get('WaterLevel', 'N/A')
                
                print(f"  {i+1}. {station_name} ({station_town})")
                print(f"     河川：{basin_name}")
                print(f"     水位：{water_level} 公尺")
            
            # 測試縣市統計
            counties = {}
            for data in water_data:
                county = reservoir_cog._normalize_county_name(data.get('StationTown', '未知'))
                if county not in counties:
                    counties[county] = 0
                counties[county] += 1
            
            print(f"\n📍 縣市分布統計:")
            for county, count in sorted(counties.items())[:10]:  # 顯示前10個
                print(f"  {county}: {count} 個測站")
            
            return True
        else:
            print("❌ 無法獲取水位資料")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

async def test_direct_ssl_connection():
    """直接測試SSL連接"""
    print("\n🔒 直接測試SSL連接...")
    
    try:
        url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=2D09DB8B-6A1B-485E-88B5-923A462F475C"
        
        # 設定SSL上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 設定連接器和超時
        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Cache-Control': 'no-cache'
            }
            
            print("📡 正在連接 opendata.wra.gov.tw...")
            async with session.get(url, headers=headers, ssl=False) as response:
                print(f"📶 回應狀態: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ SSL連接成功，獲取 {len(data)} 筆資料")
                    return True
                else:
                    print(f"❌ API回應錯誤: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ SSL連接失敗: {str(e)}")
        return False

async def main():
    """主函數"""
    print("🚀 水位查詢SSL修復驗證")
    print("=" * 50)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 測試1：直接SSL連接
    ssl_success = await test_direct_ssl_connection()
    
    # 測試2：模組整合測試
    module_success = await test_water_level_ssl_fix()
    
    print("\n" + "=" * 50)
    print("📊 測試結果:")
    print("-" * 30)
    print(f"SSL連接測試: {'✅ 通過' if ssl_success else '❌ 失敗'}")
    print(f"模組整合測試: {'✅ 通過' if module_success else '❌ 失敗'}")
    
    overall_success = ssl_success and module_success
    success_rate = (int(ssl_success) + int(module_success)) / 2 * 100
    
    print(f"整體通過率: {success_rate:.1f}%")
    print("-" * 30)
    
    if overall_success:
        print("🎉 SSL修復成功！水位查詢功能已恢復正常")
        
        print("\n💡 修復內容:")
        print("✅ 禁用SSL證書驗證")
        print("✅ 設定自定義SSL上下文") 
        print("✅ 添加適當的請求標頭")
        print("✅ 設定連接超時和限制")
        
        print("\n🎯 現在可以使用:")
        print("  /water_level city:台南")
        print("  /water_level river:曾文溪")
        print("  /water_level station:永康")
    else:
        print("❌ 部分測試失敗，需要進一步檢查")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
