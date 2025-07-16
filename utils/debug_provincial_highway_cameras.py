#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import ssl
import json
from collections import defaultdict

async def debug_provincial_highway_cameras():
    """檢查省道監視器 API 回應並分析縣市顯示問題"""
    
    print("🔍 開始檢查省道監視器 API...")
    print("=" * 50)
    
    # 省道監視器 API URLs
    api_urls = [
        "https://data.epa.gov.tw/api/v2/aqx_p_432?api_key=9be7b239-557b-4c10-9775-78cadfc555e9&limit=1000&sort=ImportDate%20desc&format=json",
        "https://opendata.wra.gov.tw/api/v1/RiverWaterLevel",
        "https://fhy.wra.gov.tw/WraApi/v1/Camera/Live"
    ]
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        
        # 測試省道監視器專用 API
        provincial_api = "https://traffic.transportdata.tw/MOTC?format=JSON"
        
        print(f"📡 測試 API: {provincial_api}")
        
        try:
            async with session.get(provincial_api, timeout=aiohttp.ClientTimeout(total=20)) as response:
                print(f"   狀態碼: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   回應類型: {type(data)}")
                    
                    if isinstance(data, list) and len(data) > 0:
                        print(f"   陣列長度: {len(data)}")
                        
                        # 分析前 5 個項目
                        print("\n📋 資料結構分析:")
                        for i, item in enumerate(data[:5]):
                            print(f"\n項目 {i+1}:")
                            print(f"   類型: {type(item)}")
                            
                            if isinstance(item, dict):
                                print(f"   欄位: {list(item.keys())}")
                                
                                # 檢查是否有 Devices
                                if 'Devices' in item:
                                    devices = item.get('Devices', [])
                                    print(f"   Devices 數量: {len(devices)}")
                                    
                                    if devices:
                                        device = devices[0]
                                        print(f"   第一個設備:")
                                        for key, value in device.items():
                                            print(f"     {key}: {value}")
                                        
                                        # 測試縣市提取
                                        location_desc = device.get('LocationDescription', '')
                                        county = extract_county_from_location(location_desc)
                                        print(f"   提取的縣市: {county}")
                        
                        # 統計所有縣市
                        print("\n📊 縣市統計:")
                        county_stats = defaultdict(int)
                        
                        for item in data:
                            if isinstance(item, dict) and 'Devices' in item:
                                devices = item.get('Devices', [])
                                for device in devices:
                                    location_desc = device.get('LocationDescription', '')
                                    county = extract_county_from_location(location_desc)
                                    county_stats[county] += 1
                        
                        for county, count in sorted(county_stats.items()):
                            print(f"   {county}: {count} 個監視器")
                        
                        # 測試篩選邏輯
                        print("\n🔍 測試縣市篩選邏輯:")
                        test_counties = ['台北', '新北', '桃園', '基隆']
                        
                        for test_county in test_counties:
                            print(f"\n測試縣市: {test_county}")
                            
                            matched_cameras = []
                            for item in data:
                                if isinstance(item, dict) and 'Devices' in item:
                                    devices = item.get('Devices', [])
                                    for device in devices:
                                        location_desc = device.get('LocationDescription', '')
                                        extracted_county = extract_county_from_location(location_desc)
                                        
                                        # 目前的篩選邏輯
                                        matches = False
                                        if test_county in extracted_county:
                                            matches = True
                                        elif test_county.replace('市', '').replace('縣', '') in extracted_county:
                                            matches = True
                                        
                                        if matches:
                                            matched_cameras.append({
                                                'name': device.get('DeviceName', ''),
                                                'location': location_desc,
                                                'county': extracted_county
                                            })
                            
                            print(f"   找到 {len(matched_cameras)} 個匹配的監視器")
                            
                            if matched_cameras:
                                for i, cam in enumerate(matched_cameras[:3], 1):
                                    print(f"     {i}. {cam['name']}")
                                    print(f"        位置: {cam['location']}")
                                    print(f"        縣市: {cam['county']}")
                    else:
                        print("   ❌ 非預期的資料格式")
                else:
                    print(f"   ❌ API 請求失敗")
                    
        except Exception as e:
            print(f"   ❌ 測試失敗: {e}")

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
    asyncio.run(debug_provincial_highway_cameras())
