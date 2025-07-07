#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修改後的單一監視器顯示功能
"""

import asyncio
import aiohttp
import ssl
import json
import datetime
import random

async def test_single_camera_display():
    """測試單一監視器顯示功能"""
    
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
        print("=== 測試單一監視器顯示功能 ===")
        
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
            
            # 4. 測試篩選功能
            print("\n4. 測試篩選功能...")
            
            # 縣市關鍵字對應
            county_keywords = {
                '新北': ['新北', '板橋', '三重', '中和', '永和', '新店', '新莊', '土城', '蘆洲', '樹林', '汐止', '鶯歌', '三峽', '淡水', '瑞芳', '五股', '泰山', '林口', '深坑', '石碇', '坪林', '三芝', '石門', '八里', '平溪', '雙溪', '貢寮', '金山', '萬里', '烏來']
            }
            
            # 測試新北市 + 台62線的篩選
            county = "新北"
            road_type = "台62線"
            
            print(f"篩選條件: 縣市={county}, 道路={road_type}")
            
            # 進行篩選
            filtered_cameras = []
            search_keywords = county_keywords.get(county, [county])
            
            for cam in cameras:
                include_camera = True
                
                # 縣市篩選
                if county:
                    search_fields = [
                        cam['name'].lower(),
                        cam['road'].lower(),
                        cam['location_desc'].lower(),
                        cam.get('county', '').lower()
                    ]
                    
                    found_match = False
                    for keyword in search_keywords:
                        if any(keyword.lower() in field for field in search_fields):
                            found_match = True
                            break
                    
                    if not found_match:
                        include_camera = False
                
                # 道路類型篩選
                if road_type and include_camera:
                    road_name = cam['road'].lower()
                    if road_type.lower() not in road_name:
                        include_camera = False
                
                if include_camera:
                    filtered_cameras.append(cam)
            
            print(f"篩選結果: {len(filtered_cameras)} 個監視器")
            
            if not filtered_cameras:
                print("❌ 沒有符合條件的監視器")
                return
            
            # 5. 模擬單一監視器顯示
            print("\n5. 模擬單一監視器顯示...")
            
            # 隨機選擇一支監視器
            selected_camera = random.choice(filtered_cameras)
            
            print("🛣️ 公路監視器")
            print("=" * 60)
            
            name = selected_camera['name']
            road = selected_camera['road']
            direction = selected_camera['direction']
            video_url = selected_camera['video_url']
            image_url = selected_camera['image_url']
            mile = selected_camera.get('mile', '')
            county_info = selected_camera.get('county', '')
            update_time = selected_camera.get('update_time', '')
            lat = selected_camera.get('lat', '')
            lon = selected_camera.get('lon', '')
            
            print(f"📍 監視器名稱: {name}")
            print()
            
            # 篩選條件
            filter_conditions = []
            if county:
                filter_conditions.append(f"縣市: {county}")
            if road_type:
                filter_conditions.append(f"道路: {road_type}")
            
            if filter_conditions:
                print(f"🔍 篩選條件: {' | '.join(filter_conditions)}")
                print()
            
            # 道路資訊
            road_info = f"🛣️ 道路: {road}"
            if direction:
                road_info += f" ({direction}向)"
            if mile:
                road_info += f"\n📏 里程: {mile}"
            print(road_info)
            print()
            
            # 位置資訊
            if lat and lon:
                print(f"📍 座標: {lat}, {lon}")
            if county_info:
                print(f"🏛️ 縣市: {county_info}")
            print()
            
            # 影像連結
            if video_url:
                print(f"🎥 即時影像: {video_url}")
            if image_url:
                timestamp = int(datetime.datetime.now().timestamp())
                cache_busted_url = f"{image_url}?t={timestamp}"
                print(f"📸 快照圖片: {cache_busted_url}")
            print()
            
            # 統計資訊
            print(f"📊 統計資訊:")
            print(f"   共找到 {len(filtered_cameras)} 個符合條件的監視器")
            print(f"   目前顯示：隨機選擇的 1 個監視器")
            print()
            
            # 更新時間
            if update_time:
                print(f"⏰ 更新時間: {update_time}")
            print(f"💡 資料來源：TDX 運輸資料流通服務平臺")
            
            print("=" * 60)
            
            # 6. 測試多次隨機選擇
            print("\n6. 測試多次隨機選擇（展示隨機性）...")
            
            for i in range(3):
                random_camera = random.choice(filtered_cameras)
                print(f"{i+1}. {random_camera['name'][:60]}...")
                print(f"   道路: {random_camera['road']}, 里程: {random_camera.get('mile', 'N/A')}")
                if random_camera['image_url']:
                    print(f"   圖片: {random_camera['image_url']}")
                print()
            
            print(f"✅ 測試完成！")

if __name__ == "__main__":
    asyncio.run(test_single_camera_display())
