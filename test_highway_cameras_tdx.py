#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新的公路監視器 TDX API
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def test_highway_cameras_api():
    """測試新的公路監視器 TDX API（含授權）"""
    try:
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=30&%24format=JSON"
        
        # TDX API 授權憑證
        app_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
        app_key = "9946bb49-0cc5-463c-ba79-c669140df4ef"
        
        # 嘗試不同的授權方式
        auth_methods = [
            {
                'name': 'Bearer Token',
                'headers': {
                    'Authorization': f'Bearer {app_id}-{app_key}',
                    'Accept': 'application/json'
                }
            },
            {
                'name': 'App ID & Key Headers',
                'headers': {
                    'X-App-ID': app_id,
                    'X-App-Key': app_key,
                    'Accept': 'application/json'
                }
            },
            {
                'name': 'Basic Auth',
                'headers': {
                    'Authorization': f'Basic {app_id}:{app_key}',
                    'Accept': 'application/json'
                }
            },
            {
                'name': 'Simple Authorization',
                'headers': {
                    'Authorization': f'{app_id}-{app_key}',
                    'Accept': 'application/json'
                }
            },
            {
                'name': 'App-ID and App-Key',
                'headers': {
                    'App-ID': app_id,
                    'App-Key': app_key,
                    'Accept': 'application/json'
                }
            }
        ]
        
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"API 回應狀態碼: {response.status}")
                
                if response.status != 200:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    if response.status == 401:
                        print("  授權失敗，請檢查 App ID 和 App Key")
                    elif response.status == 403:
                        print("  存取被禁止，可能是權限問題")
                    return
                
                content = await response.text()
                
                # 檢查回應是否為空
                if not content or len(content.strip()) == 0:
                    print("❌ API 回應為空")
                    return
                
                # 處理 BOM
                if content.startswith('\ufeff'):
                    content = content[1:]
                
                # 解析 JSON
                try:
                    data = json.loads(content)
                    print(f"✅ JSON 解析成功")
                    print(f"📊 回應資料類型: {type(data)}")
                    
                    if isinstance(data, list):
                        print(f"📊 資料筆數: {len(data)}")
                        
                        if len(data) > 0:
                            # 分析第一筆資料
                            first_item = data[0]
                            print(f"\n📋 第一筆資料結構:")
                            
                            for key, value in first_item.items():
                                if value:
                                    print(f"  ✅ {key}: {value}")
                                else:
                                    print(f"  ⚪ {key}: (空值)")
                            
                            # 測試幾個關鍵欄位
                            print(f"\n🔍 關鍵欄位檢查:")
                            print(f"  監視器名稱: {first_item.get('CCTVName', 'N/A')}")
                            print(f"  道路名稱: {first_item.get('RoadName', 'N/A')}")
                            print(f"  影像連結: {first_item.get('VideoStreamURL', 'N/A')}")
                            print(f"  位置描述: {first_item.get('LocationDescription', 'N/A')}")
                            print(f"  縣市: {first_item.get('County', 'N/A')}")
                            print(f"  更新時間: {first_item.get('UpdateTime', 'N/A')}")
                            
                            # 統計有影像連結的數量
                            cameras_with_url = sum(1 for item in data if item.get('VideoStreamURL'))
                            print(f"\n📈 統計:")
                            print(f"  總監視器數量: {len(data)}")
                            print(f"  有影像連結的監視器: {cameras_with_url}")
                            
                            # 顯示前5個監視器的基本資訊
                            print(f"\n📹 前5個監視器:")
                            for i, camera in enumerate(data[:5], 1):
                                name = camera.get('CCTVName', '未知')
                                road = camera.get('RoadName', '未知道路')
                                county = camera.get('County', '')
                                has_url = "✅" if camera.get('VideoStreamURL') else "❌"
                                
                                print(f"  {i}. {name} - {road} ({county}) - 影像: {has_url}")
                            
                        else:
                            print("❌ 沒有資料")
                    else:
                        print(f"❌ 資料格式不是列表，而是: {type(data)}")
                        if isinstance(data, dict):
                            print(f"回應內容: {data}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    print(f"前200個字元: {content[:200]}")
                    
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    print("🔍 測試新的公路監視器 TDX API（含授權）")
    print("=" * 50)
    
    asyncio.run(test_highway_cameras_api())
    
    print("\n" + "=" * 50)
    print("✅ 測試完成")
