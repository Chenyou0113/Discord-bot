#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDX API 認證測試腳本
"""
import asyncio
import aiohttp
import ssl
import base64
import time
from dotenv import load_dotenv
import os

load_dotenv()

async def test_tdx_auth():
    """測試 TDX API 認證"""
    try:
        # 讀取憑證
        client_id = os.getenv('TDX_CLIENT_ID')
        client_secret = os.getenv('TDX_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("❌ 錯誤: 找不到 TDX_CLIENT_ID 或 TDX_CLIENT_SECRET")
            return
        
        print(f"📋 使用憑證:")
        print(f"   Client ID: {client_id}")
        print(f"   Client Secret: {client_secret[:10]}...")
        
        # 建立 SSL 上下文
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=10)
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=connector
        ) as session:
            
            # 第一步：取得存取權杖
            print("\n🔐 正在取得 TDX 存取權杖...")
            
            auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
            
            # 建立 Basic Authentication
            credentials = f"{client_id}:{client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {encoded_credentials}'
            }
            
            data = 'grant_type=client_credentials'
            
            async with session.post(auth_url, headers=headers, data=data) as response:
                print(f"   認證回應狀態: {response.status}")
                
                if response.status == 200:
                    token_data = await response.json()
                    access_token = token_data.get('access_token')
                    expires_in = token_data.get('expires_in', 3600)
                    
                    print(f"✅ 成功取得存取權杖")
                    print(f"   權杖: {access_token[:20]}...")
                    print(f"   有效期限: {expires_in} 秒")
                    
                    # 第二步：測試台鐵事故 API
                    print("\n🚆 測試台鐵事故 API...")
                    
                    tra_url = "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/Alert?$top=5&$format=JSON"
                    api_headers = {
                        'Authorization': f'Bearer {access_token}',
                        'Accept': 'application/json'
                    }
                    
                    async with session.get(tra_url, headers=api_headers) as api_response:
                        print(f"   台鐵 API 回應狀態: {api_response.status}")
                        
                        if api_response.status == 200:
                            tra_data = await api_response.json()
                            print(f"✅ 成功取得台鐵事故資料")
                            print(f"   資料筆數: {len(tra_data) if isinstance(tra_data, list) else '非列表格式'}")
                            
                            if isinstance(tra_data, list) and len(tra_data) > 0:
                                print(f"   第一筆事故標題: {tra_data[0].get('Title', '無標題')}")
                            elif len(tra_data) == 0:
                                print("   ✅ 目前沒有台鐵事故通報")
                        else:
                            error_text = await api_response.text()
                            print(f"❌ 台鐵 API 請求失敗: {error_text[:200]}")
                    
                    # 第三步：測試高鐵事故 API
                    print("\n🚄 測試高鐵事故 API...")
                    
                    thsr_url = "https://tdx.transportdata.tw/api/basic/v2/Rail/THSR/AlertInfo?$top=5&$format=JSON"
                    
                    async with session.get(thsr_url, headers=api_headers) as api_response:
                        print(f"   高鐵 API 回應狀態: {api_response.status}")
                        
                        if api_response.status == 200:
                            thsr_data = await api_response.json()
                            print(f"✅ 成功取得高鐵事故資料")
                            print(f"   資料筆數: {len(thsr_data) if isinstance(thsr_data, list) else '非列表格式'}")
                            
                            if isinstance(thsr_data, list) and len(thsr_data) > 0:
                                print(f"   第一筆事故標題: {thsr_data[0].get('Title', '無標題')}")
                            elif len(thsr_data) == 0:
                                print("   ✅ 目前沒有高鐵事故通報")
                        else:
                            error_text = await api_response.text()
                            print(f"❌ 高鐵 API 請求失敗: {error_text[:200]}")
                    
                else:
                    error_text = await response.text()
                    print(f"❌ 認證失敗: {error_text}")
                    
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        print(f"詳細錯誤: {traceback.format_exc()}")

if __name__ == "__main__":
    print("🧪 TDX API 認證測試開始...")
    asyncio.run(test_tdx_auth())
    print("\n🏁 測試完成")
