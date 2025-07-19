#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試鐵路事故API連接
"""

import asyncio
import aiohttp
import json

async def test_rail_apis():
    """測試台鐵和高鐵API連接"""
    
    # API URLs
    tra_url = "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/Alert?$top=30&$format=JSON"
    thsr_url = "https://tdx.transportdata.tw/api/basic/v2/Rail/THSR/AlertInfo?$top=30&$format=JSON"
    
    async with aiohttp.ClientSession() as session:
        print("測試台鐵事故API...")
        try:
            async with session.get(tra_url, timeout=10) as response:
                print(f"台鐵API狀態碼: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"台鐵API回應類型: {type(data)}")
                    print(f"台鐵事故數量: {len(data) if isinstance(data, list) else '不是列表格式'}")
                    if isinstance(data, list) and len(data) > 0:
                        print("台鐵第一筆事故資料欄位:")
                        for key in data[0].keys():
                            print(f"  - {key}")
                else:
                    text = await response.text()
                    print(f"台鐵API錯誤回應: {text[:200]}...")
        except Exception as e:
            print(f"台鐵API測試失敗: {str(e)}")
        
        print("\n" + "="*50 + "\n")
        
        print("測試高鐵事故API...")
        try:
            async with session.get(thsr_url, timeout=10) as response:
                print(f"高鐵API狀態碼: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"高鐵API回應類型: {type(data)}")
                    print(f"高鐵事故數量: {len(data) if isinstance(data, list) else '不是列表格式'}")
                    if isinstance(data, list) and len(data) > 0:
                        print("高鐵第一筆事故資料欄位:")
                        for key in data[0].keys():
                            print(f"  - {key}")
                else:
                    text = await response.text()
                    print(f"高鐵API錯誤回應: {text[:200]}...")
        except Exception as e:
            print(f"高鐵API測試失敗: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_rail_apis())
