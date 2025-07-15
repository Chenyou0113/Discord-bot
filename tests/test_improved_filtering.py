#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修改後的 highway_cameras 指令縣市篩選功能
"""

import asyncio
import aiohttp
import ssl
import json
import datetime

async def test_improved_filtering():
    """測試改進後的縣市篩選功能"""
    
    # TDX API 設定
    token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
    client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
    api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=200&%24format=JSON"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        print("=== 測試改進後的縣市篩選功能 ===")
        
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
            
            # 3. 處理監視器資料
            cameras = []
            for cctv in cctv_list:
                try:
                    camera_info = {
                        'id': cctv.get('CCTVID', ''),
                        'name': cctv.get('SurveillanceDescription', '未知監視器'),
                        'road': cctv.get('RoadName', '未知道路'),
                        'direction': cctv.get('RoadDirection', ''),
                        'video_url': cctv.get('VideoStreamURL', ''),
                        'image_url': cctv.get('VideoImageURL', ''),
                        'lat': str(cctv.get('PositionLat', '')),
                        'lon': str(cctv.get('PositionLon', '')),
                        'location_desc': cctv.get('SurveillanceDescription', ''),
                        'mile': cctv.get('LocationMile', ''),
                        'road_class': cctv.get('RoadClass', ''),
                        'county': cctv.get('County', ''),
                        'update_time': cctv.get('UpdateTime', '')
                    }
                    
                    if camera_info['name'] and camera_info['name'] != '未知監視器':
                        cameras.append(camera_info)
                        
                except Exception as e:
                    print(f"處理監視器資料時發生錯誤: {e}")
                    continue
            
            print(f"✅ 處理完成，共 {len(cameras)} 個有效監視器")
            
            # 4. 測試改進後的縣市篩選
            print("\n4. 測試改進後的縣市篩選...")
            
            # 縣市關鍵字對應
            county_keywords = {
                '基隆': ['基隆', '暖暖', '七堵', '安樂'],
                '新北': ['新北', '板橋', '三重', '中和', '永和', '新店', '新莊', '土城', '蘆洲', '樹林', '汐止', '鶯歌', '三峽', '淡水', '瑞芳', '五股', '泰山', '林口', '深坑', '石碇', '坪林', '三芝', '石門', '八里', '平溪', '雙溪', '貢寮', '金山', '萬里', '烏來'],
                '桃園': ['桃園', '中壢', '平鎮', '八德', '楊梅', '蘆竹', '大溪', '龜山', '大園', '觀音', '新屋', '復興', '龍潭'],
            }
            
            # 測試不同縣市
            test_counties = ['基隆', '新北', '桃園', '台北', '宜蘭']
            
            for county in test_counties:
                print(f"\n--- 測試 {county} 篩選 ---")
                
                # 取得查詢縣市的關鍵字
                search_keywords = county_keywords.get(county, [county])
                
                filtered_cameras = []
                for cam in cameras:
                    # 在監視器資料中搜尋
                    search_fields = [
                        cam['name'].lower(),
                        cam['road'].lower(),
                        cam['location_desc'].lower(),
                        cam.get('county', '').lower()
                    ]
                    
                    # 檢查是否包含任何關鍵字
                    found_match = False
                    for keyword in search_keywords:
                        if any(keyword.lower() in field for field in search_fields):
                            found_match = True
                            break
                    
                    if found_match:
                        filtered_cameras.append(cam)
                
                print(f"找到 {len(filtered_cameras)} 個監視器")
                
                # 顯示前 3 個結果
                for i, cam in enumerate(filtered_cameras[:3], 1):
                    print(f"  {i}. {cam['name'][:60]}...")
                    print(f"     道路: {cam['road']}")
                    print(f"     里程: {cam['mile']}")
            
            # 5. 測試道路類型篩選
            print(f"\n5. 測試道路類型篩選...")
            
            # 統計道路類型
            road_types = {}
            for cam in cameras:
                road = cam['road']
                if road not in road_types:
                    road_types[road] = 0
                road_types[road] += 1
            
            print("道路類型分布:")
            for road, count in sorted(road_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {road}: {count} 個")
            
            # 測試台62線篩選
            print(f"\n測試台62線篩選:")
            tai62_cameras = [cam for cam in cameras if '台62線' in cam['road']]
            print(f"台62線監視器: {len(tai62_cameras)} 個")
            
            # 6. 測試組合篩選
            print(f"\n6. 測試組合篩選 (新北 + 台62線)...")
            
            # 新北 + 台62線
            combined_cameras = []
            search_keywords = county_keywords.get('新北', ['新北'])
            
            for cam in cameras:
                # 道路類型篩選
                if '台62線' in cam['road']:
                    # 縣市篩選
                    search_fields = [
                        cam['name'].lower(),
                        cam['road'].lower(),
                        cam['location_desc'].lower(),
                        cam.get('county', '').lower()
                    ]
                    
                    # 檢查是否包含任何關鍵字
                    found_match = False
                    for keyword in search_keywords:
                        if any(keyword.lower() in field for field in search_fields):
                            found_match = True
                            break
                    
                    if found_match:
                        combined_cameras.append(cam)
            
            print(f"新北 + 台62線監視器: {len(combined_cameras)} 個")
            
            # 顯示結果
            for i, cam in enumerate(combined_cameras[:5], 1):
                print(f"  {i}. {cam['name'][:60]}...")
                print(f"     道路: {cam['road']}")
                print(f"     里程: {cam['mile']}")
            
            print(f"\n✅ 測試完成！")

if __name__ == "__main__":
    asyncio.run(test_improved_filtering())
