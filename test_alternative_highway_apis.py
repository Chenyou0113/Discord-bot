#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試其他公開的公路監視器 API
"""

import asyncio
import aiohttp
import json
import ssl
import xml.etree.ElementTree as ET
from datetime import datetime

async def test_alternative_apis():
    """測試其他可能的公開 API"""
    try:
        # 嘗試不同的API端點
        api_configs = [
            {
                'name': '公路總局原始XML API',
                'url': 'https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml',
                'format': 'xml'
            },
            {
                'name': '高速公路局 API',
                'url': 'https://tisvcloud.freeway.gov.tw/api/v1/highway/camera/snapshot/info/all',
                'format': 'json'
            },
            {
                'name': '省道 API',
                'url': 'https://tisvcloud.freeway.gov.tw/api/v1/road/camera/snapshot/info/all',
                'format': 'json'
            },
            {
                'name': '交通部公路監理站 API',
                'url': 'https://traffic.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway',
                'format': 'json'
            }
        ]
        
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            for config in api_configs:
                print(f"\n🔍 測試 {config['name']}: {config['url']}")
                
                try:
                    async with session.get(config['url'], timeout=aiohttp.ClientTimeout(total=30)) as response:
                        print(f"回應狀態碼: {response.status}")
                        
                        if response.status == 200:
                            content = await response.text()
                            
                            # 檢查回應是否為空
                            if not content or len(content.strip()) == 0:
                                print("❌ API 回應為空")
                                continue
                            
                            # 處理 BOM
                            if content.startswith('\ufeff'):
                                content = content[1:]
                            
                            if config['format'] == 'json':
                                try:
                                    data = json.loads(content)
                                    print(f"✅ JSON 解析成功")
                                    print(f"📊 回應資料類型: {type(data)}")
                                    
                                    if isinstance(data, list):
                                        print(f"📊 資料筆數: {len(data)}")
                                        
                                        if len(data) > 0:
                                            first_item = data[0]
                                            print(f"\n📋 第一筆資料的欄位:")
                                            
                                            for key, value in first_item.items():
                                                if value:
                                                    print(f"  ✅ {key}")
                                                else:
                                                    print(f"  ⚪ {key}")
                                            
                                            print(f"\n✅ 找到有效的 JSON API: {config['url']}")
                                            return config
                                            
                                    else:
                                        print(f"❌ 資料格式不是列表，而是: {type(data)}")
                                        
                                except json.JSONDecodeError as e:
                                    print(f"❌ JSON 解析失敗: {e}")
                                    print(f"前200個字元: {content[:200]}")
                                    
                            elif config['format'] == 'xml':
                                try:
                                    root = ET.fromstring(content)
                                    print(f"✅ XML 解析成功")
                                    
                                    # 尋找 CCTV 元素
                                    cctv_elements = root.findall('.//CCTV')
                                    print(f"📊 CCTV 元素數量: {len(cctv_elements)}")
                                    
                                    if len(cctv_elements) > 0:
                                        first_cctv = cctv_elements[0]
                                        print(f"\n📋 第一個 CCTV 元素的子元素:")
                                        
                                        for child in first_cctv:
                                            if child.text:
                                                print(f"  ✅ {child.tag}: {child.text}")
                                            else:
                                                print(f"  ⚪ {child.tag}")
                                        
                                        print(f"\n✅ 找到有效的 XML API: {config['url']}")
                                        return config
                                        
                                except ET.ParseError as e:
                                    print(f"❌ XML 解析失敗: {e}")
                                    print(f"前200個字元: {content[:200]}")
                                    
                        else:
                            print(f"❌ 請求失敗，狀態碼: {response.status}")
                            if response.status == 401:
                                print("  需要 API 金鑰或授權")
                            elif response.status == 404:
                                print("  API 端點不存在")
                            elif response.status == 403:
                                print("  禁止存取")
                            
                except Exception as e:
                    print(f"❌ 請求 {config['url']} 時發生錯誤: {str(e)}")
                    
        print("\n❌ 沒有找到有效的 API")
        return None
                    
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        return None

if __name__ == "__main__":
    print("🔍 測試其他公開的公路監視器 API")
    print("=" * 50)
    
    result = asyncio.run(test_alternative_apis())
    
    if result:
        print(f"\n✅ 推薦使用: {result['name']}")
        print(f"URL: {result['url']}")
        print(f"格式: {result['format']}")
    else:
        print("\n❌ 未找到可用的公開 API")
    
    print("\n" + "=" * 50)
    print("✅ 測試完成")
