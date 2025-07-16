#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import ssl
import json

async def test_provincial_highway_api():
    """測試省道監視器 API"""
    
    print("🔍 測試省道監視器 API...")
    print("=" * 40)
    
    # 目前使用的 API
    api_url = "https://tisvcloud.freeway.gov.tw/api/v1/road/camera/snapshot/info/all"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            print(f"📡 測試 API: {api_url}")
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                print(f"   狀態碼: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   回應類型: {type(data)}")
                    print(f"   資料長度: {len(data) if isinstance(data, list) else 'N/A'}")
                    
                    if isinstance(data, list) and len(data) > 0:
                        # 檢查前幾個項目
                        for i, item in enumerate(data[:3]):
                            print(f"\n項目 {i+1}:")
                            print(f"   類型: {type(item)}")
                            
                            if isinstance(item, dict):
                                print(f"   欄位: {list(item.keys())}")
                                
                                # 檢查 Devices
                                if 'Devices' in item:
                                    devices = item.get('Devices', [])
                                    print(f"   Devices 數量: {len(devices)}")
                                    
                                    if devices:
                                        device = devices[0]
                                        print(f"   第一個設備:")
                                        for key, value in device.items():
                                            print(f"     {key}: {value}")
                                else:
                                    # 顯示完整項目內容
                                    print(f"   完整內容: {json.dumps(item, ensure_ascii=False, indent=2)[:300]}...")
                        
                        # 測試縣市提取
                        print("\n🔍 測試縣市提取:")
                        county_count = {}
                        
                        for item in data[:10]:  # 只檢查前 10 個
                            if isinstance(item, dict) and 'Devices' in item:
                                devices = item.get('Devices', [])
                                for device in devices:
                                    location_desc = device.get('LocationDescription', '')
                                    county = extract_county_from_location(location_desc)
                                    county_count[county] = county_count.get(county, 0) + 1
                                    
                                    print(f"   位置: {location_desc} -> 縣市: {county}")
                        
                        print(f"\n📊 縣市統計:")
                        for county, count in county_count.items():
                            print(f"   {county}: {count} 個")
                        
                        # 測試篩選邏輯
                        print(f"\n🎯 測試篩選邏輯:")
                        test_county = "新北市"
                        matched = 0
                        
                        for item in data:
                            if isinstance(item, dict) and 'Devices' in item:
                                devices = item.get('Devices', [])
                                for device in devices:
                                    location_desc = device.get('LocationDescription', '')
                                    extracted_county = extract_county_from_location(location_desc)
                                    
                                    # 檢查篩選邏輯
                                    if test_county in extracted_county or test_county.replace('市', '').replace('縣', '') in extracted_county:
                                        matched += 1
                        
                        print(f"   測試縣市: {test_county}")
                        print(f"   匹配的監視器: {matched} 個")
                    
                    else:
                        print("   ❌ 回應資料格式異常")
                else:
                    print(f"   ❌ API 請求失敗")
                    print(f"   回應內容: {await response.text()}")
        
        except Exception as e:
            print(f"   ❌ 測試失敗: {e}")
            import traceback
            traceback.print_exc()

def extract_county_from_location(location_description):
    """從位置描述中提取縣市"""
    county_keywords = {
        '基隆': '基隆市', '台北': '台北市', '新北': '新北市',
        '桃園': '桃園市', '新竹': '新竹市', '苗栗': '苗栗縣',
        '台中': '台中市', '彰化': '彰化縣', '南投': '南投縣',
        '雲林': '雲林縣', '嘉義': '嘉義市', '台南': '台南市',
        '高雄': '高雄市', '屏東': '屏東縣', '宜蘭': '宜蘭縣',
        '花蓮': '花蓮縣', '台東': '台東縣'
    }
    
    for keyword, county in county_keywords.items():
        if keyword in location_description:
            return county
    
    return '未知'

if __name__ == "__main__":
    asyncio.run(test_provincial_highway_api())
