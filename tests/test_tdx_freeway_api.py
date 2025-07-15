#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 TDX Freeway API 國道監視器查詢
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def test_tdx_freeway_api():
    """測試 TDX Freeway API 功能"""
    try:
        # TDX 憑證
        client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
        client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
        
        # 授權 API
        token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Freeway?%24top=30&%24format=JSON"
        
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
            
            print("🛣️ 步驟 2: 使用 access token 查詢國道監視器 (Freeway API)")
            
            # 查詢監視器 API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"API 請求狀態碼: {response.status}")
                
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ API 請求失敗: {error_text}")
                    return
                
                try:
                    data = await response.json()
                    print(f"✅ API 回應解析成功")
                except Exception as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    return
                
                print("🔍 步驟 3: 分析 Freeway API 回應結構")
                
                # 處理 TDX API 回應結構
                if isinstance(data, dict) and 'CCTVs' in data:
                    cctv_list = data['CCTVs']
                    print(f"📹 找到 CCTVs 鍵，國道監視器數量: {len(cctv_list)}")
                    print(f"📊 API 回應結構: dict 包含 CCTVs")
                elif isinstance(data, list):
                    cctv_list = data
                    print(f"📹 直接陣列格式，國道監視器數量: {len(cctv_list)}")
                    print(f"📊 API 回應結構: 直接陣列")
                else:
                    print(f"❌ API 回應格式錯誤: {type(data)}")
                    if isinstance(data, dict):
                        print(f"🔍 字典鍵: {list(data.keys())}")
                    return
                
                if not cctv_list:
                    print("❌ 無法解析國道監視器資料")
                    return
                
                print("📊 步驟 4: 處理國道監視器資料")
                
                cameras = []
                for cctv in cctv_list:
                    try:
                        # 根據分析結果，TDX Freeway API 的實際欄位名稱
                        road_section = cctv.get('RoadSection', {})
                        if isinstance(road_section, dict):
                            location_desc = f"{road_section.get('Start', '')} 到 {road_section.get('End', '')}"
                        else:
                            location_desc = str(road_section) if road_section else ""
                        
                        camera_info = {
                            'id': cctv.get('CCTVID', ''),
                            'name': location_desc or f"{cctv.get('RoadName', '')} {cctv.get('LocationMile', '')}",
                            'highway': cctv.get('RoadName', '未知道路'),
                            'direction': cctv.get('RoadDirection', ''),
                            'location': location_desc,
                            'video_url': cctv.get('VideoStreamURL', ''),
                            'image_url': cctv.get('VideoImageURL', ''),  # 可能沒有此欄位
                            'lat': str(cctv.get('PositionLat', '')),
                            'lon': str(cctv.get('PositionLon', '')),
                            'mile': cctv.get('LocationMile', ''),
                            'county': '',  # Freeway API 可能沒有縣市資訊
                            'update_time': '',  # 個別 CCTV 可能沒有更新時間
                            'road_section': road_section
                        }
                        
                        # 只要有基本資訊就加入
                        if camera_info['highway'] != '未知道路':
                            cameras.append(camera_info)
                            
                    except Exception as e:
                        print(f"❌ 處理國道監視器資料時發生錯誤: {e}")
                        continue
                
                print(f"✅ 成功處理 {len(cameras)} 個國道監視器")
                
                # 顯示前幾個監視器的詳細資訊
                print("\n📹 前 3 個國道監視器詳細資訊:")
                for i, camera in enumerate(cameras[:3], 1):
                    print(f"\n{i}. {camera['name']}")
                    print(f"   ID: {camera['id']}")
                    print(f"   道路: {camera['highway']}")
                    print(f"   方向: {camera['direction']}")
                    print(f"   縣市: {camera['county']}")
                    print(f"   里程: {camera['mile']}")
                    print(f"   座標: {camera['lat']}, {camera['lon']}")
                    print(f"   影像 URL: {camera['image_url']}")
                    print(f"   影片 URL: {camera['video_url']}")
                    print(f"   更新時間: {camera['update_time']}")
                
                # 統計有影像連結的監視器
                cameras_with_image = sum(1 for cam in cameras if cam['image_url'])
                cameras_with_video = sum(1 for cam in cameras if cam['video_url'])
                
                print(f"\n📊 統計資訊:")
                print(f"   總國道監視器數量: {len(cameras)}")
                print(f"   有影像快照的監視器: {cameras_with_image}")
                print(f"   有影片串流的監視器: {cameras_with_video}")
                
                # 分析道路分布
                road_distribution = {}
                for cam in cameras:
                    road = cam['highway']
                    if road in road_distribution:
                        road_distribution[road] += 1
                    else:
                        road_distribution[road] = 1
                
                print(f"\n🛣️ 道路分布:")
                for road, count in sorted(road_distribution.items()):
                    print(f"   {road}: {count} 個監視器")
                
                # 測試搜尋功能 - 國道一號
                print("\n🔍 步驟 5: 測試搜尋功能")
                
                # 搜尋國道一號
                highway1_cameras = []
                for cam in cameras:
                    if '國道1號' in cam['highway'] or '國1' in cam['highway'] or '中山高' in cam['highway']:
                        highway1_cameras.append(cam)
                
                print(f"🛣️ 國道一號監視器: {len(highway1_cameras)} 個")
                
                # 模擬 Discord embed 顯示
                print("\n💬 模擬 Discord embed 顯示 (前 3 個):")
                display_cameras = cameras[:3]
                
                for i, camera in enumerate(display_cameras, 1):
                    name = camera['name']
                    highway_info = camera['highway']
                    direction = camera['direction']
                    location_desc = camera['location']
                    video_url = camera['video_url']
                    image_url = camera['image_url']
                    mile = camera.get('mile', '')
                    county = camera.get('county', '')
                    
                    # 組合位置資訊
                    location_info = highway_info
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
                    
                    print(f"\n{i}. {name[:35]}{'...' if len(name) > 35 else ''}")
                    print(f"   🛣️ {location_info}")
                    print(f"   📍 {location_desc}")
                    print(f"   {url_text}")
                
                print(f"\n📊 共找到 {len(cameras)} 個國道監視器，顯示前 {len(display_cameras)} 個")
                
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    print("🔍 測試 TDX Freeway API 國道監視器查詢")
    print("=" * 60)
    
    asyncio.run(test_tdx_freeway_api())
    
    print("\n" + "=" * 60)
    print("✅ 測試完成")
