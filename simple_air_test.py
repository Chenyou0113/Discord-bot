#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的空氣品質連線測試
"""

import requests
import json

def test_simple_connection():
    """使用 requests 進行簡單連線測試"""
    print("=== 簡單空氣品質 API 測試 ===")
    
    api_url = "https://data.epa.gov.tw/api/v2/aqx_p_432"
    params = {
        "api_key": "94650864-6a80-4c58-83ce-fd13e7ef0504",
        "limit": 1,
        "format": "JSON"
    }
    
    try:
        print(f"測試 URL: {api_url}")
        
        # 嘗試連線
        response = requests.get(api_url, params=params, timeout=10, verify=False)
        
        print(f"狀態碼: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            print(f"✅ 成功! 獲取 {len(records)} 筆資料")
            
            if records:
                sample = records[0]
                print(f"範例測站: {sample.get('sitename', 'N/A')}")
                print(f"AQI: {sample.get('aqi', 'N/A')}")
            
            return True
        else:
            print(f"❌ HTTP 錯誤: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 連線錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_connection()
    print(f"\n結果: {'成功' if success else '失敗'}")
