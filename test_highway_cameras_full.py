#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 highway_cameras 指令的完整功能
"""

import asyncio
import aiohttp
import json
import ssl
import datetime
from datetime import datetime

async def test_highway_cameras_full():
    """測試 highway_cameras 指令的完整功能"""
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
            
            print("🚗 步驟 2: 使用 access token 查詢公路監視器")
            
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
                
                print("🔍 步驟 3: 分析 API 回應結構")
                
                # 處理 TDX API 回應結構
                if isinstance(data, dict) and 'CCTVs' in data:
                    cctv_list = data['CCTVs']
                    print(f"📹 找到 CCTVs 鍵，監視器數量: {len(cctv_list)}")
                elif isinstance(data, list):
                    cctv_list = data
                    print(f"📹 直接陣列格式，監視器數量: {len(cctv_list)}")
                else:
                    print(f"❌ API 回應格式錯誤: {type(data)}")
                    return
                
                if not cctv_list:
                    print("❌ 無法解析公路監視器資料")
                    return
                
                print("📊 步驟 4: 處理監視器資料")
                
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
                
                # 顯示前幾個監視器的詳細資訊
                print("\n📹 前 3 個監視器詳細資訊:")
                for i, camera in enumerate(cameras[:3], 1):
                    print(f"\n{i}. {camera['name']}")
                    print(f"   ID: {camera['id']}")
                    print(f"   道路: {camera['road']}")
                    print(f"   方向: {camera['direction']}")
                    print(f"   縣市: {camera['county']}")
                    print(f"   里程: {camera['mile']}")
                    print(f"   座標: {camera['lat']}, {camera['lon']}")
                    print(f"   影像 URL: {camera['image_url']}")
                    print(f"   影片 URL: {camera['video_url']}")
                    print(f"   更新時間: {camera['update_time']}")
                
                # 測試搜尋功能
                print("\n🔍 步驟 5: 測試搜尋功能")
                
                # 搜尋台北
                taipei_cameras = []
                for cam in cameras:
                    search_fields = [
                        cam['name'].lower(),
                        cam['road'].lower(),
                        cam['direction'].lower(),
                        cam['location_desc'].lower(),
                        cam.get('mile', '').lower(),
                        cam.get('county', '').lower()
                    ]
                    if any('台北' in field for field in search_fields):
                        taipei_cameras.append(cam)
                
                print(f"🏙️ 台北地區監視器: {len(taipei_cameras)} 個")
                
                # 搜尋國道一號
                highway1_cameras = []
                for cam in cameras:
                    search_fields = [
                        cam['name'].lower(),
                        cam['road'].lower(),
                        cam['direction'].lower(),
                        cam['location_desc'].lower(),
                        cam.get('mile', '').lower(),
                        cam.get('county', '').lower()
                    ]
                    if any('國道一號' in field or '國1' in field or '中山高' in field for field in search_fields):
                        highway1_cameras.append(cam)
                
                print(f"🛣️ 國道一號監視器: {len(highway1_cameras)} 個")
                
                # 統計有影像連結的監視器
                cameras_with_image = sum(1 for cam in cameras if cam['image_url'])
                cameras_with_video = sum(1 for cam in cameras if cam['video_url'])
                
                print(f"\n📊 統計資訊:")
                print(f"   總監視器數量: {len(cameras)}")
                print(f"   有影像快照的監視器: {cameras_with_image}")
                print(f"   有影片串流的監視器: {cameras_with_video}")
                
                # 模擬 Discord embed 顯示
                print("\n💬 模擬 Discord embed 顯示:")
                display_cameras = cameras[:5]
                
                for i, camera in enumerate(display_cameras, 1):
                    name = camera['name']
                    road = camera['road']
                    direction = camera['direction']
                    video_url = camera['video_url']
                    image_url = camera['image_url']
                    mile = camera.get('mile', '')
                    county = camera.get('county', '')
                    
                    # 組合位置資訊
                    location_info = road
                    if direction:
                        location_info += f" {direction}向"
                    if county:
                        location_info += f"\n🏛️ {county}"
                    if mile:
                        location_info += f"\n📏 {mile}"
                    
                    # 處理影像 URL
                    if image_url:
                        timestamp = int(datetime.now().timestamp())
                        cache_busted_url = f"{image_url}?t={timestamp}"
                        url_text = f"🔗 [查看影像]({cache_busted_url})"
                    elif video_url:
                        timestamp = int(datetime.now().timestamp())
                        cache_busted_url = f"{video_url}?t={timestamp}"
                        url_text = f"🔗 [查看影像]({cache_busted_url})"
                    else:
                        url_text = "🔗 影像連結暫不可用"
                    
                    # 座標資訊
                    lat = camera.get('lat', '')
                    lon = camera.get('lon', '')
                    if lat and lon:
                        url_text += f"\n📍 座標: {lat}, {lon}"
                    
                    print(f"\n{i}. {name[:40]}{'...' if len(name) > 40 else ''}")
                    print(f"   🛣️ {location_info}")
                    print(f"   {url_text}")
                
                print(f"\n📊 共找到 {len(cameras)} 個監視器，顯示前 {len(display_cameras)} 個")
                
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    print("🔍 測試 highway_cameras 指令的完整功能")
    print("=" * 60)
    
    asyncio.run(test_highway_cameras_full())
    
    print("\n" + "=" * 60)
    print("✅ 測試完成")
