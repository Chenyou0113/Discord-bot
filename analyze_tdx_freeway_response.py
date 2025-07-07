#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 TDX Freeway API 回應結構
"""

import asyncio
import aiohttp
import json
import ssl

async def analyze_tdx_freeway_response():
    """分析 TDX Freeway API 回應結構"""
    try:
        # TDX 憑證
        client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
        client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
        
        # 授權 API
        token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Freeway?%24top=5&%24format=JSON"
        
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
                token_json = await token_resp.json()
                access_token = token_json.get('access_token')
                print(f"✅ 成功取得 access token")
            
            print("🛣️ 步驟 2: 查詢 Freeway API 並分析回應")
            
            # 查詢監視器 API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"API 請求狀態碼: {response.status}")
                
                # 先取得文字回應
                response_text = await response.text()
                print(f"\n📝 API 回應文字（前1000字元）:")
                print(response_text[:1000])
                
                # 嘗試解析 JSON
                try:
                    data = json.loads(response_text)
                    print(f"\n✅ JSON 解析成功")
                    print(f"📊 回應類型: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"📋 字典的鍵: {list(data.keys())}")
                        
                        # 檢查每個鍵的內容
                        for key, value in data.items():
                            print(f"\n🔍 鍵 '{key}':")
                            print(f"   類型: {type(value)}")
                            if isinstance(value, list):
                                print(f"   陣列長度: {len(value)}")
                                if len(value) > 0:
                                    first_item = value[0]
                                    print(f"   第一個元素類型: {type(first_item)}")
                                    if isinstance(first_item, dict):
                                        print(f"   第一個元素的鍵: {list(first_item.keys())}")
                                        
                                        # 顯示第一個元素的詳細內容
                                        print(f"\n📄 第一個元素詳細內容:")
                                        for sub_key, sub_value in first_item.items():
                                            if sub_value:
                                                print(f"   ✅ {sub_key}: {sub_value}")
                                            else:
                                                print(f"   ⚪ {sub_key}: (空值)")
                            elif isinstance(value, str):
                                print(f"   值: {value}")
                            elif isinstance(value, (int, float)):
                                print(f"   值: {value}")
                            else:
                                print(f"   值: {str(value)[:100]}...")
                        
                    elif isinstance(data, list):
                        print(f"📊 陣列長度: {len(data)}")
                        if len(data) > 0:
                            first_item = data[0]
                            print(f"📄 第一個元素類型: {type(first_item)}")
                            if isinstance(first_item, dict):
                                print(f"📋 第一個元素的鍵: {list(first_item.keys())}")
                                
                                # 顯示第一個元素的詳細內容
                                print(f"\n📄 第一個元素詳細內容:")
                                for key, value in first_item.items():
                                    if value:
                                        print(f"   ✅ {key}: {value}")
                                    else:
                                        print(f"   ⚪ {key}: (空值)")
                    
                    else:
                        print(f"❓ 未知的回應格式: {type(data)}")
                        
                except Exception as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    print("🔍 分析 TDX Freeway API 回應結構")
    print("=" * 60)
    
    asyncio.run(analyze_tdx_freeway_response())
    
    print("\n" + "=" * 60)
    print("✅ 分析完成")
