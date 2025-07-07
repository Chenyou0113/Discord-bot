#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 TDX API 授權和公路監視器查詢
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def test_tdx_authentication():
    """測試 TDX 授權流程"""
    try:
        # TDX 憑證
        client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
        client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
        
        # 授權 API
        token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=10&%24format=JSON"
        
        # SSL 設定
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # 步驟 1: 取得 access token
            print("🔑 步驟 1: 取得 TDX access token")
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret
            }
            token_headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            async with session.post(token_url, data=token_data, headers=token_headers) as token_resp:
                print(f"Token 請求狀態碼: {token_resp.status}")
                
                if token_resp.status != 200:
                    error_text = await token_resp.text()
                    print(f"❌ 取得 Token 失敗: {error_text}")
                    return
                
                try:
                    token_json = await token_resp.json()
                    print(f"✅ Token 回應格式: {type(token_json)}")
                    
                    if 'access_token' in token_json:
                        access_token = token_json['access_token']
                        token_type = token_json.get('token_type', 'Bearer')
                        expires_in = token_json.get('expires_in', 'Unknown')
                        
                        print(f"✅ 成功取得 access token")
                        print(f"   Token 類型: {token_type}")
                        print(f"   有效期限: {expires_in} 秒")
                        print(f"   Token 前10字元: {access_token[:10]}...")
                        
                    else:
                        print(f"❌ 回應中沒有 access_token: {token_json}")
                        return
                        
                except Exception as e:
                    print(f"❌ 解析 Token 回應失敗: {e}")
                    return
            
            # 步驟 2: 使用 access token 查詢 API
            print(f"\n🚗 步驟 2: 使用 access token 查詢公路監視器")
            
            api_headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            async with session.get(api_url, headers=api_headers, timeout=aiohttp.ClientTimeout(total=30)) as api_resp:
                print(f"API 請求狀態碼: {api_resp.status}")
                
                if api_resp.status != 200:
                    error_text = await api_resp.text()
                    print(f"❌ API 請求失敗: {error_text}")
                    return
                
                try:
                    api_data = await api_resp.json()
                    print(f"✅ API 回應格式: {type(api_data)}")
                    
                    if isinstance(api_data, list):
                        print(f"📊 監視器數量: {len(api_data)}")
                        
                        if len(api_data) > 0:
                            first_camera = api_data[0]
                            print(f"\n📹 第一個監視器資訊:")
                            print(f"   ID: {first_camera.get('CCTVID', 'N/A')}")
                            print(f"   名稱: {first_camera.get('CCTVName', 'N/A')}")
                            print(f"   道路: {first_camera.get('RoadName', 'N/A')}")
                            print(f"   方向: {first_camera.get('RoadDirection', 'N/A')}")
                            print(f"   縣市: {first_camera.get('County', 'N/A')}")
                            print(f"   影像 URL: {first_camera.get('VideoStreamURL', 'N/A')}")
                            print(f"   更新時間: {first_camera.get('UpdateTime', 'N/A')}")
                            
                            # 統計有影像連結的監視器
                            cameras_with_url = sum(1 for cam in api_data if cam.get('VideoStreamURL'))
                            print(f"\n📈 統計:")
                            print(f"   總監視器數量: {len(api_data)}")
                            print(f"   有影像連結的監視器: {cameras_with_url}")
                            
                        else:
                            print("❌ 沒有監視器資料")
                    else:
                        print(f"❌ API 回應格式錯誤: {api_data}")
                        
                except Exception as e:
                    print(f"❌ 解析 API 回應失敗: {e}")
                    
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    print("🔍 測試 TDX API 授權和公路監視器查詢")
    print("=" * 60)
    
    asyncio.run(test_tdx_authentication())
    
    print("\n" + "=" * 60)
    print("✅ 測試完成")
