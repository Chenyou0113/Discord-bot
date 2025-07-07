#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 TDX API 回應結構
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def analyze_tdx_response():
    """分析 TDX API 回應結構"""
    try:
        # TDX 憑證
        client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
        client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
        
        # 授權 API
        token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=5&%24format=JSON"
        
        # SSL 設定
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
            token_headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            async with session.post(token_url, data=token_data, headers=token_headers) as token_resp:
                if token_resp.status != 200:
                    print(f"❌ 取得 Token 失敗: {token_resp.status}")
                    return
                
                token_json = await token_resp.json()
                access_token = token_json['access_token']
                print(f"✅ 成功取得 access token")
            
            # 查詢 API 並分析回應結構
            api_headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            async with session.get(api_url, headers=api_headers, timeout=aiohttp.ClientTimeout(total=30)) as api_resp:
                if api_resp.status != 200:
                    print(f"❌ API 請求失敗: {api_resp.status}")
                    return
                
                api_data = await api_resp.json()
                
                print(f"📊 API 回應分析:")
                print(f"   回應類型: {type(api_data)}")
                
                if isinstance(api_data, dict):
                    print(f"   頂層鍵: {list(api_data.keys())}")
                    
                    # 尋找監視器資料
                    camera_data = None
                    cameras_key = None
                    
                    # 常見的可能鍵名
                    possible_keys = ['CCTVs', 'CCTV', 'Data', 'Items', 'Results', 'cameras', 'value']
                    
                    for key in api_data.keys():
                        if isinstance(api_data[key], list) and len(api_data[key]) > 0:
                            # 檢查第一個元素是否像監視器資料
                            first_item = api_data[key][0]
                            if isinstance(first_item, dict) and any(field in first_item for field in ['CCTVID', 'CCTVName', 'VideoStreamURL']):
                                camera_data = api_data[key]
                                cameras_key = key
                                break
                    
                    if camera_data:
                        print(f"✅ 找到監視器資料在鍵: '{cameras_key}'")
                        print(f"   監視器數量: {len(camera_data)}")
                        
                        if len(camera_data) > 0:
                            first_camera = camera_data[0]
                            print(f"\n📹 第一個監視器的欄位:")
                            
                            for key, value in first_camera.items():
                                if value:
                                    value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                                    print(f"   ✅ {key}: {value_str}")
                                else:
                                    print(f"   ⚪ {key}: (空值)")
                            
                            # 檢查關鍵欄位
                            print(f"\n🔍 關鍵欄位檢查:")
                            print(f"   監視器 ID: {first_camera.get('CCTVID', 'N/A')}")
                            print(f"   監視器名稱: {first_camera.get('CCTVName', 'N/A')}")
                            print(f"   道路名稱: {first_camera.get('RoadName', 'N/A')}")
                            print(f"   縣市: {first_camera.get('County', 'N/A')}")
                            print(f"   影像 URL: {first_camera.get('VideoStreamURL', 'N/A')}")
                            
                    else:
                        print(f"❌ 無法找到監視器資料")
                        print(f"   可能需要檢查的鍵:")
                        for key, value in api_data.items():
                            print(f"   - {key}: {type(value)} ({len(value) if isinstance(value, (list, dict)) else 'N/A'})")
                
                elif isinstance(api_data, list):
                    print(f"   直接是監視器列表，數量: {len(api_data)}")
                    
                    if len(api_data) > 0:
                        first_camera = api_data[0]
                        print(f"\n📹 第一個監視器的欄位:")
                        
                        for key, value in first_camera.items():
                            if value:
                                value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                                print(f"   ✅ {key}: {value_str}")
                            else:
                                print(f"   ⚪ {key}: (空值)")
                
                # 顯示完整的 JSON 結構（截短）
                json_str = json.dumps(api_data, ensure_ascii=False, indent=2)
                print(f"\n📄 完整回應 JSON（前1000字元）:")
                print(json_str[:1000] + "..." if len(json_str) > 1000 else json_str)
                    
    except Exception as e:
        print(f"❌ 分析過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    print("🔍 分析 TDX API 回應結構")
    print("=" * 50)
    
    asyncio.run(analyze_tdx_response())
    
    print("\n" + "=" * 50)
    print("✅ 分析完成")
