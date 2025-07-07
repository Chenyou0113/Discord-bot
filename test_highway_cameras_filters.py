#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修改後的 highway_cameras 指令（縣市 + 台幾線篩選）
"""

import asyncio
import aiohttp
import json
import ssl
import random
from datetime import datetime

async def test_highway_cameras_with_filters():
    """測試帶有縣市和道路類型篩選的 highway_cameras 功能"""
    try:
        # TDX 憑證
        client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
        client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
        
        # 授權 API
        token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=30&%24format=JSON"
        
        # SSL 設定
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            print("🔑 步驟 1: 取得 TDX access token")
            # 取得 access token
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
                
                print(f"✅ 成功取得 access token")
            
            print("🛣️ 步驟 2: 使用 access token 查詢公路監視器")
            
            # 查詢監視器 API
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
                    print(f"✅ API 回應解析成功")
                except Exception as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    return
                
                # 處理 TDX API 回應結構
                if isinstance(data, dict) and 'CCTVs' in data:
                    cctv_list = data['CCTVs']
                elif isinstance(data, list):
                    cctv_list = data
                else:
                    print(f"❌ API 回應格式錯誤")
                    return
                
                if not cctv_list:
                    print("❌ 無法解析公路監視器資料")
                    return
                
                print("📊 步驟 3: 處理監視器資料")
                
                cameras = []
                for cctv in cctv_list:
                    try:
                        # TDX API 的欄位名稱
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
                        print(f"❌ 處理監視器資料時發生錯誤: {e}")
                        continue
                
                print(f"✅ 成功處理 {len(cameras)} 個監視器")
                
                # 分析道路分布
                road_distribution = {}
                for cam in cameras:
                    road = cam['road']
                    if road in road_distribution:
                        road_distribution[road] += 1
                    else:
                        road_distribution[road] = 1
                
                print(f"\n🛣️ 道路分布:")
                for road, count in sorted(road_distribution.items()):
                    print(f"   {road}: {count} 個監視器")
                
                # 測試縣市篩選功能
                print("\n🔍 步驟 4: 測試縣市篩選功能")
                
                def filter_by_county(cameras, county):
                    """根據縣市篩選監視器"""
                    filtered = []
                    for cam in cameras:
                        search_fields = [
                            cam['name'].lower(),
                            cam['road'].lower(),
                            cam['location_desc'].lower(),
                            cam.get('county', '').lower()
                        ]
                        if any(county.lower() in field for field in search_fields):
                            filtered.append(cam)
                    return filtered
                
                # 測試台北
                taipei_cameras = filter_by_county(cameras, "台北")
                print(f"🏙️ 台北地區監視器: {len(taipei_cameras)} 個")
                
                # 測試新北
                new_taipei_cameras = filter_by_county(cameras, "新北")
                print(f"🏙️ 新北地區監視器: {len(new_taipei_cameras)} 個")
                
                # 測試道路類型篩選功能
                print("\n🔍 步驟 5: 測試道路類型篩選功能")
                
                def filter_by_road_type(cameras, road_type):
                    """根據道路類型篩選監視器"""
                    filtered = []
                    for cam in cameras:
                        road_name = cam['road'].lower()
                        if road_type.lower() in road_name:
                            filtered.append(cam)
                    return filtered
                
                # 測試台62線
                tai62_cameras = filter_by_road_type(cameras, "台62線")
                print(f"🛣️ 台62線監視器: {len(tai62_cameras)} 個")
                
                # 測試台1線
                tai1_cameras = filter_by_road_type(cameras, "台1線")
                print(f"🛣️ 台1線監視器: {len(tai1_cameras)} 個")
                
                # 組合篩選測試
                print("\n🔍 步驟 6: 測試組合篩選功能")
                
                def filter_combined(cameras, county=None, road_type=None):
                    """組合篩選"""
                    filtered = []
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
                            if not any(county.lower() in field for field in search_fields):
                                include_camera = False
                        
                        # 道路類型篩選
                        if road_type and include_camera:
                            road_name = cam['road'].lower()
                            if road_type.lower() not in road_name:
                                include_camera = False
                        
                        if include_camera:
                            filtered.append(cam)
                    
                    return filtered
                
                # 測試：新北 + 台62線
                combined_cameras = filter_combined(cameras, county="新北", road_type="台62線")
                print(f"🎯 新北 + 台62線監視器: {len(combined_cameras)} 個")
                
                if combined_cameras:
                    print("\n📹 符合條件的監視器:")
                    for i, cam in enumerate(combined_cameras[:3], 1):
                        print(f"   {i}. {cam['name']}")
                        print(f"      道路: {cam['road']}")
                        print(f"      里程: {cam['mile']}")
                
                # 模擬 Discord embed 顯示
                print("\n💬 模擬 Discord embed 顯示 (縣市: 新北, 道路: 台62線):")
                
                if combined_cameras:
                    # 隨機選擇一支監視器（模擬新的單一顯示功能）
                    selected_camera = random.choice(combined_cameras)
                    
                    name = selected_camera['name']
                    road = selected_camera['road']
                    direction = selected_camera['direction']
                    video_url = selected_camera['video_url']
                    image_url = selected_camera['image_url']
                    mile = selected_camera.get('mile', '')
                    county = selected_camera.get('county', '')
                    update_time = selected_camera.get('update_time', '')
                    lat = selected_camera.get('lat', '')
                    lon = selected_camera.get('lon', '')
                    
                    print("🛣️ 公路監視器")
                    print(f"📍 標題描述: {name}")
                    print("🔍 篩選條件: 縣市: 新北 | 道路: 台62線")
                    print()
                    
                    # 道路資訊
                    road_info = f"🛣️ 道路: {road}"
                    if direction:
                        road_info += f" ({direction}向)"
                    if mile:
                        road_info += f"\n📏 里程: {mile}"
                    print(f"道路資訊:")
                    print(f"   {road_info}")
                    print()
                    
                    # 位置資訊
                    if lat and lon:
                        location_info = f"📍 座標: {lat}, {lon}"
                        if county:
                            location_info += f"\n🏛️ 縣市: {county}"
                        print(f"位置資訊:")
                        print(f"   {location_info}")
                        print()
                    
                    # 即時影像
                    if video_url:
                        print(f"🎥 即時影像:")
                        print(f"   [點擊觀看即時影像]({video_url})")
                        print()
                    
                    # 監視器快照圖片
                    if image_url:
                        timestamp = int(datetime.now().timestamp())
                        cache_busted_url = f"{image_url}?t={timestamp}"
                        print(f"📸 監視器快照:")
                        print(f"   {cache_busted_url}")
                        print()
                    
                    # 統計資訊
                    print(f"📊 統計資訊:")
                    print(f"   共找到 {len(combined_cameras)} 個符合條件的監視器")
                    print(f"   目前顯示：隨機選擇的 1 個監視器")
                    print()
                    
                    print("⏰ 資料來源：TDX 運輸資料流通服務平臺")
                else:
                    print("❌ 找不到符合條件的監視器")
                
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    print("🔍 測試修改後的 highway_cameras 指令（縣市 + 台幾線篩選）")
    print("=" * 80)
    
    asyncio.run(test_highway_cameras_with_filters())
    
    print("\n" + "=" * 80)
    print("✅ 測試完成")
