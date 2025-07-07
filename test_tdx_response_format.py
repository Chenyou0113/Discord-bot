#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 TDX API 回應格式
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def test_tdx_response_format():
    """測試 TDX API 回應格式"""
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
                
                token_json = await token_resp.json()
                access_token = token_json['access_token']
                print(f"✅ 成功取得 access token")
            
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
                
                # 先取得文字回應
                response_text = await api_resp.text()
                print(f"\n📝 API 回應文字（前500字元）:")
                print(response_text[:500])
                
                # 嘗試解析 JSON
                try:
                    api_data = json.loads(response_text)
                    print(f"\n✅ API 回應格式: {type(api_data)}")
                    
                    if isinstance(api_data, dict):
                        print(f"📊 字典的鍵: {list(api_data.keys())}")
                        
                        # 檢查是否有 CCTVs 鍵
                        if 'CCTVs' in api_data:
                            cctv_list = api_data['CCTVs']
                            print(f"📹 CCTVs 陣列長度: {len(cctv_list)}")
                            
                            if len(cctv_list) > 0:
                                first_cctv = cctv_list[0]
                                print(f"\n📹 第一個 CCTV 資訊:")
                                print(f"   類型: {type(first_cctv)}")
                                print(f"   鍵: {list(first_cctv.keys())}")
                                print(f"   CCTVID: {first_cctv.get('CCTVID', 'N/A')}")
                                print(f"   SurveillanceDescription: {first_cctv.get('SurveillanceDescription', 'N/A')}")
                                print(f"   RoadName: {first_cctv.get('RoadName', 'N/A')}")
                                print(f"   VideoImageURL: {first_cctv.get('VideoImageURL', 'N/A')}")
                                print(f"   VideoStreamURL: {first_cctv.get('VideoStreamURL', 'N/A')}")
                                
                        else:
                            print("❌ 沒有找到 CCTVs 鍵")
                            
                    elif isinstance(api_data, list):
                        print(f"📊 陣列長度: {len(api_data)}")
                        
                        if len(api_data) > 0:
                            first_item = api_data[0]
                            print(f"\n📹 第一個項目:")
                            print(f"   類型: {type(first_item)}")
                            if isinstance(first_item, dict):
                                print(f"   鍵: {list(first_item.keys())}")
                                
                    else:
                        print(f"❌ 未知的回應格式: {type(api_data)}")
                        
                except Exception as e:
                    print(f"❌ 解析 JSON 失敗: {e}")
                    
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    print("🔍 測試 TDX API 回應格式")
    print("=" * 60)
    
    asyncio.run(test_tdx_response_format())
    
    print("\n" + "=" * 60)
    print("✅ 測試完成")
