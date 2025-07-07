#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 TDX 不同參數設定以獲取更多監視器資料
"""

import asyncio
import aiohttp
import ssl
import json
import datetime

async def test_tdx_parameters():
    """測試 TDX 不同參數設定"""
    
    # TDX API 設定
    token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
    client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
    
    # 不同的 API URL 測試
    test_urls = [
        {
            "name": "基本查詢 (top=30)",
            "url": "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=30&%24format=JSON"
        },
        {
            "name": "增加數量 (top=100)",
            "url": "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=100&%24format=JSON"
        },
        {
            "name": "依縣市篩選 (基隆市)",
            "url": "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=50&%24filter=County%20eq%20%27基隆市%27&%24format=JSON"
        },
        {
            "name": "依縣市篩選 (台北市)",
            "url": "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=50&%24filter=County%20eq%20%27台北市%27&%24format=JSON"
        },
        {
            "name": "依縣市篩選 (新北市)",
            "url": "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=50&%24filter=County%20eq%20%27新北市%27&%24format=JSON"
        },
        {
            "name": "依道路篩選 (台1線)",
            "url": "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=50&%24filter=contains(RoadName,%27台1線%27)&%24format=JSON"
        },
        {
            "name": "依道路篩選 (台3線)",
            "url": "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=50&%24filter=contains(RoadName,%27台3線%27)&%24format=JSON"
        },
        {
            "name": "依道路篩選 (台9線)",
            "url": "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=50&%24filter=contains(RoadName,%27台9線%27)&%24format=JSON"
        },
        {
            "name": "省道監視器 (Provincial)",
            "url": "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Provincial?%24top=50&%24format=JSON"
        },
        {
            "name": "市區道路監視器 (City)",
            "url": "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/City?%24top=50&%24format=JSON"
        }
    ]
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        print("=== 測試 TDX 不同參數設定 ===")
        
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
        
        # 2. 測試不同的 API URL
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        for test_case in test_urls:
            print(f"\n--- 測試: {test_case['name']} ---")
            print(f"URL: {test_case['url']}")
            
            try:
                async with session.get(test_case['url'], headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        print(f"❌ API 請求失敗，狀態碼: {response.status}")
                        continue
                    
                    try:
                        data = await response.json()
                    except Exception as e:
                        print(f"❌ JSON 解析失敗: {e}")
                        continue
                    
                    # 處理不同的回應結構
                    if isinstance(data, dict):
                        if 'CCTVs' in data:
                            cctv_list = data['CCTVs']
                        elif 'ProvincialCCTVs' in data:
                            cctv_list = data['ProvincialCCTVs']
                        elif 'CityCCTVs' in data:
                            cctv_list = data['CityCCTVs']
                        else:
                            cctv_list = []
                    elif isinstance(data, list):
                        cctv_list = data
                    else:
                        cctv_list = []
                    
                    print(f"✅ 成功取得 {len(cctv_list)} 筆監視器資料")
                    
                    if cctv_list:
                        # 分析前 3 筆資料
                        road_types = set()
                        counties = set()
                        
                        for cctv in cctv_list[:3]:
                            road_name = cctv.get('RoadName', '')
                            county = cctv.get('County', '')
                            description = cctv.get('SurveillanceDescription', '')
                            
                            if road_name:
                                road_types.add(road_name)
                            if county:
                                counties.add(county)
                            
                            print(f"  範例: {description[:60]}...")
                            print(f"    道路: {road_name}")
                            print(f"    縣市: {county}")
                            print(f"    ID: {cctv.get('CCTVID', '')}")
                        
                        # 統計所有資料
                        all_roads = set()
                        all_counties = set()
                        
                        for cctv in cctv_list:
                            road_name = cctv.get('RoadName', '')
                            county = cctv.get('County', '')
                            
                            if road_name:
                                all_roads.add(road_name)
                            if county:
                                all_counties.add(county)
                        
                        print(f"  道路類型: {sorted(list(all_roads))}")
                        print(f"  縣市: {sorted(list(all_counties))}")
                    else:
                        print("❌ 無監視器資料")
                
            except Exception as e:
                print(f"❌ 測試失敗: {e}")
        
        print(f"\n✅ 測試完成！")

if __name__ == "__main__":
    asyncio.run(test_tdx_parameters())
