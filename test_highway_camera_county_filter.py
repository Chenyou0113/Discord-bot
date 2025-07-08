#!/usr/bin/env python3
"""
測試公路監視器縣市篩選功能
"""

import asyncio
import aiohttp
import ssl
import json

async def test_highway_cameras_data():
    """測試 TDX 公路監視器 API 資料結構"""
    
    print("=== 測試 TDX 公路監視器 API ===")
    
    try:
        # 1. 取得 TDX access token
        token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
        client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=50&%24format=JSON"

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(connector=connector) as session:
            # 取得 access token
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret
            }
            token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            
            print("1. 取得 TDX access token...")
            async with session.post(token_url, data=token_data, headers=token_headers) as token_resp:
                if token_resp.status != 200:
                    print(f"❌ 無法取得 TDX Token，狀態碼: {token_resp.status}")
                    return
                
                token_json = await token_resp.json()
                access_token = token_json.get('access_token')
                if not access_token:
                    print("❌ 無法取得 TDX access_token")
                    return
                
                print("✅ TDX Token 取得成功")
            
            # 2. 查詢監視器 API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            print("2. 查詢公路監視器資料...")
            async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    return
                
                try:
                    data = await response.json()
                    print("✅ API 資料取得成功")
                except Exception as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    return
                
                # 3. 分析資料結構
                print("\n3. 分析資料結構...")
                
                # 檢查回應格式
                if isinstance(data, dict) and 'CCTVs' in data:
                    cctv_list = data['CCTVs']
                    print(f"資料格式: dict 包含 'CCTVs' 鍵，監視器數量: {len(cctv_list)}")
                elif isinstance(data, list):
                    cctv_list = data
                    print(f"資料格式: list，監視器數量: {len(cctv_list)}")
                else:
                    print("❌ 未知的資料格式")
                    return
                
                if not cctv_list:
                    print("❌ 沒有監視器資料")
                    return
                
                # 4. 分析前 5 個監視器的縣市資訊
                print("\n4. 分析監視器縣市資訊...")
                county_info = {}
                
                for i, cctv in enumerate(cctv_list[:10]):  # 檢查前 10 個
                    camera_data = {
                        'name': cctv.get('SurveillanceDescription', '未知監視器'),
                        'road': cctv.get('RoadName', '未知道路'),
                        'county': cctv.get('County', ''),
                        'location_desc': cctv.get('SurveillanceDescription', ''),
                        'road_class': cctv.get('RoadClass', ''),
                        'all_fields': list(cctv.keys())
                    }
                    
                    print(f"\n監視器 {i+1}:")
                    print(f"  名稱: {camera_data['name']}")
                    print(f"  道路: {camera_data['road']}")
                    print(f"  縣市: {camera_data['county']}")
                    print(f"  位置描述: {camera_data['location_desc']}")
                    print(f"  道路類別: {camera_data['road_class']}")
                    
                    # 統計縣市
                    county = camera_data['county']
                    if county:
                        county_info[county] = county_info.get(county, 0) + 1
                
                # 5. 顯示縣市統計
                print("\n5. 縣市統計:")
                if county_info:
                    for county, count in sorted(county_info.items()):
                        print(f"  {county}: {count} 個監視器")
                else:
                    print("  沒有找到縣市資訊")
                
                # 6. 測試縣市篩選
                print("\n6. 測試縣市篩選邏輯...")
                test_counties = ['台北', '新北', '桃園', '台中', '高雄']
                
                for test_county in test_counties:
                    matched_cameras = []
                    
                    # 縣市關鍵字對應
                    county_keywords = {
                        '台北': ['台北', '北市', '臺北'],
                        '新北': ['新北'],
                        '桃園': ['桃園'],
                        '台中': ['台中', '臺中'],
                        '高雄': ['高雄']
                    }
                    
                    search_keywords = county_keywords.get(test_county, [test_county])
                    
                    for cctv in cctv_list[:20]:  # 檢查前 20 個
                        search_fields = [
                            cctv.get('SurveillanceDescription', '').lower(),
                            cctv.get('RoadName', '').lower(),
                            cctv.get('County', '').lower()
                        ]
                        
                        # 檢查是否包含任何關鍵字
                        found_match = False
                        for keyword in search_keywords:
                            if any(keyword.lower() in field for field in search_fields):
                                found_match = True
                                break
                        
                        if found_match:
                            matched_cameras.append({
                                'name': cctv.get('SurveillanceDescription', ''),
                                'county': cctv.get('County', ''),
                                'road': cctv.get('RoadName', '')
                            })
                    
                    print(f"\n測試縣市 '{test_county}':")
                    print(f"  關鍵字: {search_keywords}")
                    print(f"  找到 {len(matched_cameras)} 個匹配的監視器")
                    
                    if matched_cameras:
                        for i, cam in enumerate(matched_cameras[:3]):  # 顯示前 3 個
                            print(f"    {i+1}. {cam['name']} (縣市: {cam['county']}, 道路: {cam['road']})")
                    else:
                        print("    ❌ 沒有找到匹配的監視器")
                
                print("\n=== 測試完成 ===")
                
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_highway_cameras_data())
