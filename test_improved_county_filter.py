#!/usr/bin/env python3
"""
測試修正後的公路監視器縣市篩選功能
"""

import asyncio
import aiohttp
import ssl
import json

async def test_improved_county_filter():
    """測試改善後的縣市篩選功能"""
    
    print("=== 測試改善後的縣市篩選功能 ===")
    
    try:
        # 1. 取得 TDX access token
        token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
        client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=100&%24format=JSON"

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
                
                # 處理回應格式
                if isinstance(data, dict) and 'CCTVs' in data:
                    cctv_list = data['CCTVs']
                elif isinstance(data, list):
                    cctv_list = data
                else:
                    print("❌ 未知的資料格式")
                    return
                
                if not cctv_list:
                    print("❌ 沒有監視器資料")
                    return
                
                print(f"共取得 {len(cctv_list)} 個監視器資料")
                
                # 3. 測試改善後的縣市篩選
                print("\n3. 測試改善後的縣市篩選...")
                test_counties = ['基隆', '新北', '台北', '桃園']
                
                for test_county in test_counties:
                    print(f"\n測試縣市: {test_county}")
                    
                    # 縣市關鍵字對應 - 包含更多地名
                    county_keywords = {
                        '基隆': ['基隆', '暖暖', '七堵', '安樂', '中正', '仁愛', '信義'],
                        '台北': ['台北', '北市', '臺北', '大安', '中山', '信義', '松山', '中正', '萬華', '大同', '南港', '內湖', '士林', '北投', '文山', '木柵', '景美', '天母', '社子', '關渡'],
                        '新北': ['新北', '板橋', '三重', '中和', '永和', '新店', '新莊', '土城', '蘆洲', '樹林', '汐止', '鶯歌', '三峽', '淡水', '瑞芳', '五股', '泰山', '林口', '深坑', '石碇', '坪林', '三芝', '石門', '八里', '平溪', '雙溪', '貢寮', '金山', '萬里', '烏來', '中山', '重陽', '大華', '重新'],
                        '桃園': ['桃園', '中壢', '平鎮', '八德', '楊梅', '蘆竹', '大溪', '龜山', '大園', '觀音', '新屋', '復興', '龍潭', '青埔']
                    }
                    
                    search_keywords = county_keywords.get(test_county, [test_county])
                    matched_cameras = []
                    
                    for cctv in cctv_list:
                        name = cctv.get('SurveillanceDescription', '')
                        road = cctv.get('RoadName', '')
                        county_field = cctv.get('County', '')
                        
                        # 改善的搜尋方式 - 合併所有文字進行搜尋
                        search_text = f"{name} {road} {county_field}".lower()
                        
                        # 檢查是否包含任何關鍵字
                        found_match = False
                        matched_keyword = None
                        for keyword in search_keywords:
                            if keyword.lower() in search_text:
                                found_match = True
                                matched_keyword = keyword
                                break
                        
                        if found_match:
                            matched_cameras.append({
                                'name': name,
                                'road': road,
                                'county': county_field,
                                'matched_keyword': matched_keyword,
                                'search_text': search_text[:100] + '...' if len(search_text) > 100 else search_text
                            })
                    
                    print(f"  搜尋關鍵字: {search_keywords[:5]}{'...' if len(search_keywords) > 5 else ''}")
                    print(f"  找到 {len(matched_cameras)} 個匹配的監視器")
                    
                    if matched_cameras:
                        for i, cam in enumerate(matched_cameras[:5]):  # 顯示前 5 個
                            print(f"    {i+1}. {cam['name'][:50]}{'...' if len(cam['name']) > 50 else ''}")
                            print(f"       道路: {cam['road']}, 匹配關鍵字: {cam['matched_keyword']}")
                    else:
                        print("    ❌ 沒有找到匹配的監視器")
                        
                        # 顯示前 3 個監視器名稱供參考
                        print("    前 3 個監視器名稱:")
                        for i, cctv in enumerate(cctv_list[:3]):
                            name = cctv.get('SurveillanceDescription', '')
                            print(f"      {i+1}. {name}")
                
                print("\n=== 測試完成 ===")
                
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_improved_county_filter())
