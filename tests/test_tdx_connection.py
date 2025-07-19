#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試TDX API連接和捷運指令功能
"""

import os
import sys
import asyncio
import aiohttp
import ssl
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

async def test_tdx_connection():
    """測試TDX API連接"""
    print("🔗 測試TDX API連接...")
    
    # 檢查環境變數
    client_id = os.getenv('TDX_CLIENT_ID')
    client_secret = os.getenv('TDX_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ TDX API 憑證未設定！")
        print("請確認 .env 檔案中有設定:")
        print("TDX_CLIENT_ID=你的CLIENT_ID")
        print("TDX_CLIENT_SECRET=你的CLIENT_SECRET")
        return False
    
    print(f"✅ TDX_CLIENT_ID: {client_id[:10]}...")
    print(f"✅ TDX_CLIENT_SECRET: {client_secret[:10]}...")
    
    # 設定SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=ssl_context)
    ) as session:
        
        # 測試取得token
        print("\n🔑 測試取得Access Token...")
        token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        try:
            async with session.post(token_url, data=token_data) as response:
                if response.status == 200:
                    token_info = await response.json()
                    access_token = token_info.get('access_token')
                    if access_token:
                        print(f"✅ 成功取得Access Token: {access_token[:20]}...")
                        
                        # 測試台北捷運API
                        print("\n🚇 測試台北捷運API...")
                        metro_url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/AlertInfo/TRTC"
                        headers = {
                            'Authorization': f'Bearer {access_token}',
                            'Accept': 'application/json'
                        }
                        
                        async with session.get(metro_url, headers=headers) as metro_response:
                            if metro_response.status == 200:
                                metro_data = await metro_response.json()
                                print(f"✅ 成功取得台北捷運資料，共 {len(metro_data)} 筆")
                                
                                if metro_data:
                                    first_alert = metro_data[0]
                                    print(f"📋 範例資料: {list(first_alert.keys())}")
                                else:
                                    print("ℹ️ 目前沒有捷運事故資料")
                                
                                return True
                            else:
                                print(f"❌ 台北捷運API請求失敗: {metro_response.status}")
                                text = await metro_response.text()
                                print(f"回應內容: {text[:200]}...")
                    else:
                        print("❌ Token回應中沒有access_token")
                else:
                    print(f"❌ Token請求失敗: {response.status}")
                    text = await response.text()
                    print(f"回應內容: {text}")
                    
        except Exception as e:
            print(f"❌ 連接錯誤: {str(e)}")
    
    return False

async def test_metro_systems():
    """測試所有捷運系統的API端點"""
    print("\n🚇 測試所有捷運系統API端點...")
    
    metro_systems = {
        'TRTC': '台北捷運',
        'KRTC': '高雄捷運', 
        'TYMC': '桃園捷運',
        'KLRT': '高雄輕軌',
        'TMRT': '台中捷運'
    }
    
    # 檢查環境變數
    client_id = os.getenv('TDX_CLIENT_ID')
    client_secret = os.getenv('TDX_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ TDX API 憑證未設定！")
        return
    
    # 設定SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=ssl_context)
    ) as session:
        
        # 取得token
        token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        async with session.post(token_url, data=token_data) as response:
            if response.status != 200:
                print("❌ 無法取得Access Token")
                return
                
            token_info = await response.json()
            access_token = token_info.get('access_token')
            
            if not access_token:
                print("❌ Token回應無效")
                return
        
        # 測試各個捷運系統
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        for system_code, system_name in metro_systems.items():
            print(f"\n📍 測試 {system_name} ({system_code})...")
            metro_url = f"https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/AlertInfo/{system_code}"
            
            try:
                async with session.get(metro_url, headers=headers) as metro_response:
                    if metro_response.status == 200:
                        metro_data = await metro_response.json()
                        print(f"  ✅ API回應正常，資料筆數: {len(metro_data)}")
                        
                        if metro_data and len(metro_data) > 0:
                            sample = metro_data[0]
                            print(f"  📊 資料欄位: {list(sample.keys())}")
                        else:
                            print(f"  ℹ️ 目前 {system_name} 沒有警示資料")
                    else:
                        print(f"  ❌ API請求失敗: {metro_response.status}")
                        if metro_response.status == 404:
                            print(f"  ⚠️ {system_name} 可能不支援此API端點")
                        
            except Exception as e:
                print(f"  ❌ 連接錯誤: {str(e)}")

if __name__ == "__main__":
    print("🧪 開始TDX API連接測試...")
    
    # 測試基本連接
    success = asyncio.run(test_tdx_connection())
    
    if success:
        # 測試所有捷運系統
        asyncio.run(test_metro_systems())
    
    print("\n🏁 測試完成")
