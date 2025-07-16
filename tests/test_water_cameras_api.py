#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水利監視器 API 測試腳本
用於診斷為什麼查詢縣市水利監視器時顯示查無監視器
"""

import asyncio
import aiohttp
import ssl
import xml.etree.ElementTree as ET
import json

async def test_water_cameras_api():
    """測試水利監視器 API"""
    print("🔍 開始測試水利防災監視器 API...")
    
    # 使用正確的 XML API
    api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=xml&id=362C7288-F378-4BF2-966C-2CD961732C52"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            print(f"📡 正在請求 API: {api_url}")
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"📊 回應狀態碼: {response.status}")
                
                if response.status != 200:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    return
                
                content = await response.text()
                print(f"📏 回應內容長度: {len(content)} 字元")
                
                # 檢查回應是否為空
                if not content or len(content.strip()) == 0:
                    print("❌ API 回應為空")
                    return
                
                # 處理可能的 BOM
                if content.startswith('\ufeff'):
                    content = content[1:]
                    print("✅ 已移除 BOM")
                
                # 顯示前 500 字元作為樣本
                print("\n📄 回應內容樣本（前 500 字元）:")
                print("=" * 50)
                print(content[:500])
                print("=" * 50)
                
                # 解析 XML
                try:
                    root = ET.fromstring(content)
                    print(f"✅ XML 解析成功，根元素: {root.tag}")
                    
                    # 顯示 XML 結構
                    print("\n🌳 XML 結構分析:")
                    print(f"根元素: {root.tag}")
                    print(f"根元素屬性: {root.attrib}")
                    
                    # 查找所有子元素
                    print("\n📂 子元素:")
                    for child in root:
                        print(f"  - {child.tag} (屬性: {child.attrib})")
                        if len(list(child)) > 0:
                            for grandchild in child:
                                print(f"    - {grandchild.tag}")
                                if len(list(grandchild)) > 0:
                                    for ggchild in grandchild:
                                        print(f"      - {ggchild.tag}")
                    
                    # 查找所有的 Table 元素
                    items = root.findall('.//diffgr:diffgram//NewDataSet//Table', 
                                       {'diffgr': 'urn:schemas-microsoft-com:xml-diffgram-v1'})
                    print(f"\n🔍 使用 diffgr 命名空間找到 {len(items)} 個 Table 元素")
                    
                    if not items:
                        # 嘗試其他可能的路徑
                        items = root.findall('.//Table')
                        print(f"🔍 使用簡單路徑找到 {len(items)} 個 Table 元素")
                    
                    if not items:
                        # 嘗試查找所有可能的資料元素
                        all_elements = []
                        for elem in root.iter():
                            if elem.text and elem.text.strip():
                                all_elements.append((elem.tag, elem.text[:50]))
                        
                        print(f"🔍 找到 {len(all_elements)} 個包含文字的元素")
                        print("前 10 個元素:")
                        for tag, text in all_elements[:10]:
                            print(f"  {tag}: {text}")
                    
                    if items:
                        print(f"\n📊 找到 {len(items)} 個監視器記錄")
                        
                        # 分析第一筆資料的結構
                        if items:
                            first_item = items[0]
                            print(f"\n🔬 第一筆資料結構分析:")
                            print(f"元素標籤: {first_item.tag}")
                            print(f"元素屬性: {first_item.attrib}")
                            
                            print("📋 所有欄位:")
                            for child in first_item:
                                value = child.text if child.text else "(空值)"
                                if len(value) > 50:
                                    value = value[:50] + "..."
                                print(f"  {child.tag}: {value}")
                        
                        # 分析縣市分布
                        counties = {}
                        for item in items:
                            county_elem = item.find('CountiesAndCitiesWhereTheMonitoringPointsAreLocated')
                            if county_elem is not None and county_elem.text:
                                county = county_elem.text
                                counties[county] = counties.get(county, 0) + 1
                        
                        print(f"\n🏛️ 縣市分布 (共 {len(counties)} 個縣市):")
                        for county, count in sorted(counties.items()):
                            print(f"  {county}: {count} 個監視器")
                        
                        # 測試特定縣市查詢
                        test_counties = ["臺北市", "台北市", "新北市", "桃園市"]
                        for test_county in test_counties:
                            filtered_count = 0
                            for item in items:
                                county_elem = item.find('CountiesAndCitiesWhereTheMonitoringPointsAreLocated')
                                if county_elem is not None and county_elem.text:
                                    if test_county in county_elem.text or county_elem.text in test_county:
                                        filtered_count += 1
                            print(f"🎯 {test_county} 搜尋結果: {filtered_count} 個監視器")
                    
                except ET.ParseError as e:
                    print(f"❌ XML 解析失敗: {e}")
                    print("📄 嘗試顯示原始內容:")
                    print(content[:1000])
                    
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_water_cameras_api())
