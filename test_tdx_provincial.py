#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 TDX Provincial 和 City 監視器 API
"""

import asyncio
import aiohttp
import ssl
import json
import datetime

async def test_tdx_provincial():
    """測試 TDX Provincial 監視器 API"""
    
    # TDX API 設定
    token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
    client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        print("=== 測試 TDX Provincial 監視器 API ===")
        
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
        
        # 2. 測試 Provincial API
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        print("\n2. 測試 Provincial 監視器 API...")
        provincial_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Provincial?%24top=50&%24format=JSON"
        
        try:
            async with session.get(provincial_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    print(f"❌ Provincial API 請求失敗，狀態碼: {response.status}")
                    return
                
                try:
                    data = await response.json()
                except Exception as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    return
                
                # 處理回應結構
                if isinstance(data, dict) and 'ProvincialCCTVs' in data:
                    cctv_list = data['ProvincialCCTVs']
                elif isinstance(data, list):
                    cctv_list = data
                else:
                    cctv_list = []
                
                print(f"✅ 成功取得 {len(cctv_list)} 筆省道監視器資料")
                
                if cctv_list:
                    # 分析前 5 筆資料
                    print("\n前 5 筆省道監視器資料:")
                    for i, cctv in enumerate(cctv_list[:5], 1):
                        print(f"\n{i}. {cctv.get('SurveillanceDescription', 'N/A')}")
                        print(f"   道路: {cctv.get('RoadName', 'N/A')}")
                        print(f"   縣市: {cctv.get('County', 'N/A')}")
                        print(f"   ID: {cctv.get('CCTVID', 'N/A')}")
                        print(f"   位置: {cctv.get('LocationMile', 'N/A')}")
                        print(f"   方向: {cctv.get('RoadDirection', 'N/A')}")
                        print(f"   影像: {cctv.get('VideoImageURL', 'N/A')}")
                    
                    # 統計分析
                    roads = {}
                    counties = {}
                    
                    for cctv in cctv_list:
                        road = cctv.get('RoadName', '')
                        county = cctv.get('County', '')
                        
                        if road:
                            roads[road] = roads.get(road, 0) + 1
                        if county:
                            counties[county] = counties.get(county, 0) + 1
                    
                    print(f"\n道路分布 (前 10 名):")
                    for road, count in sorted(roads.items(), key=lambda x: x[1], reverse=True)[:10]:
                        print(f"  {road}: {count} 個")
                    
                    print(f"\n縣市分布:")
                    for county, count in sorted(counties.items(), key=lambda x: x[1], reverse=True):
                        print(f"  {county}: {count} 個")
                    
                    # 測試篩選功能
                    print(f"\n測試篩選功能:")
                    
                    # 測試台1線
                    tai1_cameras = [cctv for cctv in cctv_list if '台1線' in cctv.get('RoadName', '')]
                    print(f"台1線監視器: {len(tai1_cameras)} 個")
                    
                    # 測試台3線
                    tai3_cameras = [cctv for cctv in cctv_list if '台3線' in cctv.get('RoadName', '')]
                    print(f"台3線監視器: {len(tai3_cameras)} 個")
                    
                    # 測試台9線
                    tai9_cameras = [cctv for cctv in cctv_list if '台9線' in cctv.get('RoadName', '')]
                    print(f"台9線監視器: {len(tai9_cameras)} 個")
                    
                    # 測試新北市
                    new_taipei_cameras = [cctv for cctv in cctv_list if '新北' in cctv.get('County', '')]
                    print(f"新北市監視器: {len(new_taipei_cameras)} 個")
                    
                    # 測試台北市
                    taipei_cameras = [cctv for cctv in cctv_list if '台北' in cctv.get('County', '')]
                    print(f"台北市監視器: {len(taipei_cameras)} 個")
                    
                    # 測試組合篩選
                    if tai1_cameras and new_taipei_cameras:
                        combined = []
                        for cctv in cctv_list:
                            if '台1線' in cctv.get('RoadName', '') and '新北' in cctv.get('County', ''):
                                combined.append(cctv)
                        print(f"新北市台1線監視器: {len(combined)} 個")
                        
                        if combined:
                            print("範例:")
                            for i, cctv in enumerate(combined[:3], 1):
                                print(f"  {i}. {cctv.get('SurveillanceDescription', 'N/A')}")
                
                else:
                    print("❌ 無省道監視器資料")
                
        except Exception as e:
            print(f"❌ 測試失敗: {e}")
        
        print(f"\n✅ 測試完成！")

if __name__ == "__main__":
    asyncio.run(test_tdx_provincial())
