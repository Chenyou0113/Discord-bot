#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空氣品質 API 修復腳本
專門修復空氣品質連線問題
"""

import asyncio
import aiohttp
import ssl
import json
import logging

logger = logging.getLogger(__name__)

async def test_air_quality_connection():
    """測試空氣品質API連線"""
    
    # API 配置
    api_endpoints = [
        "https://data.epa.gov.tw/api/v2/aqx_p_432",
        "https://data.moenv.gov.tw/api/v2/aqx_p_432"
    ]
    api_key = "94650864-6a80-4c58-83ce-fd13e7ef0504"
    
    params = {
        "api_key": api_key,
        "limit": 10,
        "sort": "ImportDate desc",
        "format": "JSON"
    }
    
    # 設定 SSL 上下文
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    print("🌬️ 測試空氣品質 API 連線")
    print("=" * 40)
    
    for i, api_endpoint in enumerate(api_endpoints, 1):
        print(f"\n{i}. 測試端點: {api_endpoint}")
        
        try:
            # 建立連接器
            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                limit=10,
                force_close=True,
                enable_cleanup_closed=True
            )
            
            # 設定超時
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            
            async with aiohttp.ClientSession(
                connector=connector, 
                timeout=timeout
            ) as session:
                async with session.get(api_endpoint, params=params) as response:
                    print(f"   HTTP 狀態碼: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        records = data.get('records', [])
                        print(f"   ✅ 連線成功！獲得 {len(records)} 筆記錄")
                        
                        if records:
                            first_record = records[0]
                            site_name = first_record.get('sitename', 'N/A')
                            aqi = first_record.get('aqi', 'N/A')
                            print(f"   範例: {site_name}, AQI: {aqi}")
                            
                        return True
                    else:
                        print(f"   ❌ HTTP 錯誤: {response.status}")
                        
        except asyncio.TimeoutError:
            print("   ❌ 連線超時")
        except Exception as e:
            print(f"   ❌ 連線錯誤: {e}")
    
    print("\n❌ 所有端點都無法連線")
    return False

async def main():
    """主函數"""
    success = await test_air_quality_connection()
    
    if success:
        print("\n✅ 空氣品質 API 連線正常")
        print("修復建議：SSL 設定和多端點機制可以解決連線問題")
    else:
        print("\n❌ 空氣品質 API 連線失敗")
        print("建議：檢查網路連線或嘗試使用代理伺服器")

if __name__ == "__main__":
    asyncio.run(main())
