#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細分析 TDX 公路監視器的資料結構，特別是縣市資訊
"""

import asyncio
import aiohttp
import ssl
import json
import datetime

async def analyze_highway_cameras_data():
    """詳細分析 TDX 公路監視器資料結構"""
    
    # TDX API 設定
    token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
    client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
    api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=30&%24format=JSON"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        print("=== 詳細分析 TDX 公路監視器資料結構 ===")
        
        # 1. 取得 access token
        print("1. 取得 TDX access token...")
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        async with session.post(token_url, data=token_data, headers=token_headers) as token_resp:
            if token_resp.status != 200:
                print(f"❌ 無法取得 TDX Token，狀態碼: {token_resp.status}")
                return
            
            token_json = await token_resp.json()
            access_token = token_json.get('access_token')
            
            if not access_token:
                print("❌ 無法取得 TDX access_token")
                return
            
            print(f"✅ 成功取得 access_token")
        
        # 2. 查詢監視器 API
        print("\n2. 查詢監視器 API...")
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status != 200:
                print(f"❌ API 請求失敗，狀態碼: {response.status}")
                return
            
            try:
                data = await response.json()
            except Exception as e:
                print(f"❌ JSON 解析失敗: {e}")
                return
            
            # 處理 TDX API 回應結構
            if isinstance(data, dict) and 'CCTVs' in data:
                cctv_list = data['CCTVs']
            elif isinstance(data, list):
                cctv_list = data
            else:
                print("❌ API 回應格式錯誤")
                return
            
            if not cctv_list:
                print("❌ 無法解析公路監視器資料")
                return
            
            print(f"✅ 成功取得 {len(cctv_list)} 筆監視器資料")
            
            # 3. 詳細分析前 5 筆資料
            print("\n3. 詳細分析前 5 筆資料...")
            for i, cctv in enumerate(cctv_list[:5], 1):
                print(f"\n--- 第 {i} 筆監視器資料 ---")
                print(f"CCTVID: {cctv.get('CCTVID', 'N/A')}")
                print(f"SurveillanceDescription: {cctv.get('SurveillanceDescription', 'N/A')}")
                print(f"RoadName: {cctv.get('RoadName', 'N/A')}")
                print(f"RoadDirection: {cctv.get('RoadDirection', 'N/A')}")
                print(f"RoadClass: {cctv.get('RoadClass', 'N/A')}")
                print(f"County: {cctv.get('County', 'N/A')}")
                print(f"LocationMile: {cctv.get('LocationMile', 'N/A')}")
                print(f"PositionLat: {cctv.get('PositionLat', 'N/A')}")
                print(f"PositionLon: {cctv.get('PositionLon', 'N/A')}")
                print(f"VideoStreamURL: {cctv.get('VideoStreamURL', 'N/A')}")
                print(f"VideoImageURL: {cctv.get('VideoImageURL', 'N/A')}")
                print(f"UpdateTime: {cctv.get('UpdateTime', 'N/A')}")
                
                # 檢查所有欄位
                print("所有欄位:")
                for key, value in cctv.items():
                    if isinstance(value, str) and len(value) > 100:
                        print(f"  {key}: {value[:100]}...")
                    else:
                        print(f"  {key}: {value}")
            
            # 4. 分析縣市資訊
            print("\n4. 分析縣市資訊...")
            county_analysis = {}
            
            for cctv in cctv_list:
                # 從各種欄位提取縣市資訊
                county_field = cctv.get('County', '')
                name_field = cctv.get('SurveillanceDescription', '')
                road_field = cctv.get('RoadName', '')
                
                # 檢查不同欄位中的縣市關鍵字
                county_keywords = [
                    '基隆', '台北', '新北', '桃園', '新竹', '苗栗',
                    '台中', '彰化', '南投', '雲林', '嘉義', '台南',
                    '高雄', '屏東', '宜蘭', '花蓮', '台東'
                ]
                
                detected_counties = []
                
                # 從 County 欄位檢查
                if county_field:
                    for keyword in county_keywords:
                        if keyword in county_field:
                            detected_counties.append(f"County:{keyword}")
                
                # 從 SurveillanceDescription 檢查
                if name_field:
                    for keyword in county_keywords:
                        if keyword in name_field:
                            detected_counties.append(f"Name:{keyword}")
                
                # 從 RoadName 檢查
                if road_field:
                    for keyword in county_keywords:
                        if keyword in road_field:
                            detected_counties.append(f"Road:{keyword}")
                
                county_key = f"County:{county_field}|Name:{name_field[:50]}|Road:{road_field}"
                if county_key not in county_analysis:
                    county_analysis[county_key] = {
                        'count': 0,
                        'detected': detected_counties,
                        'sample_id': cctv.get('CCTVID', '')
                    }
                county_analysis[county_key]['count'] += 1
            
            print("縣市分析結果:")
            for key, info in county_analysis.items():
                print(f"  {key}")
                print(f"    數量: {info['count']}")
                print(f"    檢測到的縣市: {info['detected']}")
                print(f"    樣本ID: {info['sample_id']}")
                print()
            
            # 5. 測試不同的篩選策略
            print("\n5. 測試不同的篩選策略...")
            
            # 策略 1: 只根據 County 欄位
            print("策略 1: 只根據 County 欄位篩選")
            county_filter = "新北"
            matched_1 = [cctv for cctv in cctv_list if county_filter in cctv.get('County', '')]
            print(f"  結果: {len(matched_1)} 個監視器")
            
            # 策略 2: 根據 SurveillanceDescription 欄位
            print("策略 2: 根據 SurveillanceDescription 欄位篩選")
            matched_2 = [cctv for cctv in cctv_list if county_filter in cctv.get('SurveillanceDescription', '')]
            print(f"  結果: {len(matched_2)} 個監視器")
            
            # 策略 3: 根據 RoadName 欄位
            print("策略 3: 根據 RoadName 欄位篩選")
            matched_3 = [cctv for cctv in cctv_list if county_filter in cctv.get('RoadName', '')]
            print(f"  結果: {len(matched_3)} 個監視器")
            
            # 策略 4: 組合策略
            print("策略 4: 組合策略篩選")
            matched_4 = []
            for cctv in cctv_list:
                search_fields = [
                    cctv.get('County', ''),
                    cctv.get('SurveillanceDescription', ''),
                    cctv.get('RoadName', '')
                ]
                if any(county_filter in field for field in search_fields):
                    matched_4.append(cctv)
            print(f"  結果: {len(matched_4)} 個監視器")
            
            # 顯示找到的監視器
            if matched_4:
                print("\n找到的監視器:")
                for i, cctv in enumerate(matched_4[:3], 1):
                    print(f"  {i}. {cctv.get('SurveillanceDescription', 'N/A')}")
                    print(f"     縣市: {cctv.get('County', 'N/A')}")
                    print(f"     道路: {cctv.get('RoadName', 'N/A')}")
            
            print(f"\n✅ 分析完成！")

if __name__ == "__main__":
    asyncio.run(analyze_highway_cameras_data())
