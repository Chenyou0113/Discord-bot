#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDX LiveBoard API 測試腳本
根據官方範例代碼優化
"""

import asyncio
import aiohttp
import ssl
import json
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class TDXLiveBoardTester:
    def __init__(self):
        self.client_id = os.getenv('TDX_CLIENT_ID')
        self.client_secret = os.getenv('TDX_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("請設定 TDX_CLIENT_ID 和 TDX_CLIENT_SECRET 環境變數")
            
        # TDX官方認證端點
        self.auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        
        # LiveBoard API端點（根據官方範例）
        self.liveboard_apis = {
            'TRTC': 'https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/TRTC?$top=30&$format=JSON',
            'KRTC': 'https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/KRTC?$top=30&$format=JSON',
            'KLRT': 'https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/KLRT?$top=30&$format=JSON'
        }
        
    async def get_access_token(self):
        """根據TDX官方範例獲取Access Token"""
        print("🔑 正在獲取 Access Token...")
        
        # 根據官方範例設定請求參數
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        # 根據官方範例設定標頭
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'br,gzip'  # 官方建議的壓縮設定
        }
        
        # SSL設定
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.post(self.auth_url, data=data, headers=headers) as response:
                if response.status == 200:
                    token_data = await response.json()
                    print("✅ 成功獲取 Access Token")
                    return token_data.get('access_token')
                else:
                    error_text = await response.text()
                    print(f"❌ 獲取 Access Token 失敗: {response.status}")
                    print(f"錯誤內容: {error_text}")
                    return None
    
    async def test_liveboard_api(self, metro_system, access_token):
        """測試LiveBoard API"""
        print(f"\n🚇 測試 {metro_system} LiveBoard API...")
        
        url = self.liveboard_apis.get(metro_system)
        if not url:
            print(f"❌ 不支援的捷運系統: {metro_system}")
            return None
            
        # 根據官方範例設定標頭
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Accept-Encoding': 'br,gzip',  # 官方建議的壓縮設定
            'User-Agent': 'TDX-LiveBoard-Tester/1.0'
        }
        
        # SSL設定
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                print(f"HTTP狀態碼: {response.status}")
                print(f"回應標頭: {dict(response.headers)}")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        print(f"✅ 成功獲取 {metro_system} 資料")
                        print(f"資料筆數: {len(data) if isinstance(data, list) else '非列表格式'}")
                        
                        # 分析資料結構
                        if isinstance(data, list) and len(data) > 0:
                            print("\n📋 資料結構分析:")
                            sample = data[0]
                            print(f"第一筆資料的欄位: {list(sample.keys()) if isinstance(sample, dict) else '非字典格式'}")
                            
                            # 詳細分析前3筆資料
                            print("\n🔍 前3筆資料詳情:")
                            for i, record in enumerate(data[:3]):
                                if isinstance(record, dict):
                                    station_name = record.get('StationName', {})
                                    if isinstance(station_name, dict):
                                        station_name_zh = station_name.get('Zh_tw', '未知')
                                    else:
                                        station_name_zh = str(station_name)
                                    
                                    print(f"  [{i+1}] 車站: {station_name_zh}")
                                    print(f"      路線: {record.get('LineID', 'N/A')}")
                                    print(f"      目的地: {record.get('TripHeadSign', 'N/A')}")
                                    print(f"      預估時間: {record.get('EstimateTime', 'N/A')}")
                                    print(f"      服務狀態: {record.get('ServiceStatus', 'N/A')}")
                                    print(f"      更新時間: {record.get('UpdateTime', 'N/A')}")
                                    print()
                        
                        return data
                        
                    except Exception as e:
                        error_text = await response.text()
                        print(f"❌ 解析JSON失敗: {str(e)}")
                        print(f"原始回應內容: {error_text[:500]}...")
                        return None
                else:
                    error_text = await response.text()
                    print(f"❌ API請求失敗: {response.status}")
                    print(f"錯誤內容: {error_text}")
                    return None
    
    async def run_tests(self):
        """執行完整測試"""
        print("🧪 開始 TDX LiveBoard API 測試...")
        print("=" * 50)
        
        # 步驟1: 獲取Access Token
        access_token = await self.get_access_token()
        if not access_token:
            print("❌ 無法獲取Access Token，測試中止")
            return
        
        print(f"Access Token (前10字元): {access_token[:10]}...")
        
        # 步驟2: 測試各捷運系統
        results = {}
        for metro_system in ['TRTC', 'KRTC', 'KLRT']:
            result = await self.test_liveboard_api(metro_system, access_token)
            results[metro_system] = result
            await asyncio.sleep(1)  # 避免請求太頻繁
        
        # 步驟3: 總結測試結果
        print("\n" + "=" * 50)
        print("📊 測試結果總結:")
        for metro_system, result in results.items():
            if result is not None:
                count = len(result) if isinstance(result, list) else 0
                print(f"  {metro_system}: ✅ 成功 ({count} 筆資料)")
            else:
                print(f"  {metro_system}: ❌ 失敗")
        
        print("\n🎉 測試完成！")

async def main():
    """主程式"""
    try:
        tester = TDXLiveBoardTester()
        await tester.run_tests()
    except Exception as e:
        print(f"❌ 測試程式發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
