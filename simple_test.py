#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的TDX LiveBoard API 測試腳本
"""

import asyncio
import aiohttp
import ssl
import json
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

async def test_simple():
    """簡化測試"""
    print("🧪 開始簡化測試...")
    
    client_id = os.getenv('TDX_CLIENT_ID')
    client_secret = os.getenv('TDX_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ 請設定 TDX_CLIENT_ID 和 TDX_CLIENT_SECRET 環境變數")
        return
    
    # 步驟1: 獲取Access Token
    print("🔑 正在獲取 Access Token...")
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # SSL設定
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    timeout = aiohttp.ClientTimeout(total=30)
    
    try:
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.post(auth_url, data=data, headers=headers) as response:
                if response.status == 200:
                    token_data = await response.json()
                    access_token = token_data.get('access_token')
                    print("✅ 成功獲取 Access Token")
                else:
                    error_text = await response.text()
                    print(f"❌ 獲取 Access Token 失敗: {response.status}")
                    print(f"錯誤內容: {error_text}")
                    return
        
        # 步驟2: 測試LiveBoard API
        print("🚇 測試台北捷運 LiveBoard API...")
        
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/TRTC?$top=10&$format=JSON"
        
        api_headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(api_url, headers=api_headers) as response:
                print(f"HTTP狀態碼: {response.status}")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        print(f"✅ 成功獲取資料")
                        print(f"資料筆數: {len(data) if isinstance(data, list) else '非列表格式'}")
                        
                        if isinstance(data, list) and len(data) > 0:
                            print("\n📋 第一筆資料:")
                            sample = data[0]
                            if isinstance(sample, dict):
                                for key, value in sample.items():
                                    print(f"  {key}: {value}")
                        
                        # 儲存資料
                        with open('liveboard_test_result.json', 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        print("📄 資料已儲存到 liveboard_test_result.json")
                        
                    except Exception as e:
                        error_text = await response.text()
                        print(f"❌ 解析JSON失敗: {str(e)}")
                        print(f"原始回應: {error_text[:200]}...")
                else:
                    error_text = await response.text()
                    print(f"❌ API請求失敗: {response.status}")
                    print(f"錯誤內容: {error_text}")
        
    except Exception as e:
        print(f"❌ 測試發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("🎉 測試完成！")

if __name__ == "__main__":
    asyncio.run(test_simple())
