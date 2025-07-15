#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試各個指令的 API 可用性
"""

import aiohttp
import asyncio
import ssl
import json

async def test_api_endpoint(name, url, headers=None):
    """測試 API 端點是否可用"""
    print(f"\n🔍 測試 {name}...")
    print(f"URL: {url}")
    
    try:
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                print(f"狀態碼: {response.status}")
                print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                
                if response.status == 200:
                    try:
                        # 嘗試讀取前 500 字元
                        text = await response.text()
                        if text.startswith('\ufeff'):
                            text = text[1:]
                        
                        print(f"回應長度: {len(text)} 字元")
                        print(f"前 200 字元: {text[:200]}...")
                        
                        # 嘗試解析 JSON
                        if 'json' in response.headers.get('Content-Type', '').lower():
                            data = json.loads(text)
                            if isinstance(data, dict):
                                print(f"JSON 鍵: {list(data.keys())[:5]}")
                            elif isinstance(data, list):
                                print(f"JSON 陣列長度: {len(data)}")
                                if data:
                                    print(f"第一個元素鍵: {list(data[0].keys())[:5] if isinstance(data[0], dict) else 'N/A'}")
                        
                        return True
                    except Exception as e:
                        print(f"解析回應時發生錯誤: {e}")
                        return False
                else:
                    print(f"❌ API 請求失敗")
                    return False
                    
    except Exception as e:
        print(f"❌ 連線錯誤: {e}")
        return False

async def main():
    """測試所有 API 端點"""
    print("🚀 開始測試 Discord Bot 指令的 API 可用性")
    
    # 定義要測試的 API
    apis = [
        {
            "name": "河川水位資料 (water_level)",
            "url": "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=2D09DB8B-6A1B-485E-88B5-923A462F475C"
        },
        {
            "name": "警戒水位資料",
            "url": "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=D2A498A6-8706-42FB-B623-C08C9665BDFD"
        },
        {
            "name": "水利防災監控影像 (water_cameras)",
            "url": "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=5f46ee50-7e82-46c6-9fe1-c6ea4416451f"
        },
        {
            "name": "TDX Freeway API (national_highway_cameras)",
            "url": "https://tdx.transportdata.tw/api/basic/v2/Road/Live/Traffic/CCTV/Freeway?$format=JSON&$top=5"
        },
        {
            "name": "TDX Provincial Highway API (highway_cameras)",
            "url": "https://tdx.transportdata.tw/api/basic/v2/Road/Live/Traffic/CCTV/Provincial?$format=JSON&$top=5"
        },
        {
            "name": "省道監視器 API (general_road_cameras)",
            "url": "https://alerts.ncdr.nat.gov.tw/RssAtomFeed/GetVideoSummaryApi?PTYPE=camera&ContentType=json"
        },
        {
            "name": "縣道監視器 API (general_road_cameras)",
            "url": "https://alerts.ncdr.nat.gov.tw/RssAtomFeed/GetVideoSummaryApi?PTYPE=ccamera&ContentType=json"
        }
    ]
    
    # 測試結果統計
    results = {}
    
    for api in apis:
        result = await test_api_endpoint(api["name"], api["url"], api.get("headers"))
        results[api["name"]] = result
        await asyncio.sleep(1)  # 避免請求過於頻繁
    
    # 輸出測試總結
    print("\n" + "="*60)
    print("📊 API 可用性測試總結")
    print("="*60)
    
    working_apis = []
    failed_apis = []
    
    for name, status in results.items():
        status_emoji = "✅" if status else "❌"
        print(f"{status_emoji} {name}")
        
        if status:
            working_apis.append(name)
        else:
            failed_apis.append(name)
    
    print(f"\n📈 統計:")
    print(f"✅ 可用: {len(working_apis)}/{len(results)}")
    print(f"❌ 失效: {len(failed_apis)}/{len(results)}")
    
    if failed_apis:
        print(f"\n⚠️ 需要檢查或移除的 API:")
        for api in failed_apis:
            print(f"   - {api}")

if __name__ == "__main__":
    asyncio.run(main())
