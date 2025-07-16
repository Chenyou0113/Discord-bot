#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析高速公路 XML API 資料結構
測試 https://tisvcloud.freeway.gov.tw/history/motc20/CCTV.xml
"""

import aiohttp
import asyncio
import xml.etree.ElementTree as ET
import json
import ssl
from datetime import datetime

async def analyze_freeway_xml():
    """分析高速公路 XML API 資料結構"""
    print("=" * 60)
    print("分析高速公路 XML API 資料結構")
    print("=" * 60)
    
    # API URL
    api_url = "https://tisvcloud.freeway.gov.tw/history/motc20/CCTV.xml"
    
    # SSL 設定
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            print(f"📡 正在請求 API: {api_url}")
            
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                print(f"📊 HTTP 狀態碼: {response.status}")
                
                if response.status != 200:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    return
                
                # 讀取 XML 內容
                xml_content = await response.text(encoding='utf-8')
                print(f"📄 XML 內容長度: {len(xml_content)} 字元")
                
                # 解析 XML
                try:
                    root = ET.fromstring(xml_content)
                    print(f"✅ XML 解析成功")
                    print(f"🏷️ 根元素標籤: {root.tag}")
                    
                    # 分析根層級結構
                    print("\n" + "=" * 40)
                    print("根層級結構分析")
                    print("=" * 40)
                    
                    for child in root:
                        print(f"📂 子元素: {child.tag}")
                        if child.text and child.text.strip():
                            print(f"   內容: {child.text.strip()}")
                        
                        # 如果是 CCTVs 或類似的監視器列表
                        if 'cctv' in child.tag.lower() or 'camera' in child.tag.lower() or len(list(child)) > 5:
                            print(f"   🎥 可能是監視器列表，包含 {len(list(child))} 個子元素")
                            
                            # 分析前 3 個監視器
                            camera_count = 0
                            for camera in child:
                                if camera_count >= 3:
                                    break
                                
                                print(f"\n   📹 監視器 #{camera_count + 1} ({camera.tag}):")
                                for field in camera:
                                    field_value = field.text.strip() if field.text else ""
                                    if len(field_value) > 100:
                                        field_value = field_value[:100] + "..."
                                    print(f"      {field.tag}: {field_value}")
                                
                                camera_count += 1
                    
                    # 查找所有監視器資料
                    print("\n" + "=" * 40)
                    print("監視器資料統計")
                    print("=" * 40)
                    
                    # 尋找監視器列表（可能在不同層級）
                    camera_elements = []
                    
                    # 方法1：直接在根層級找
                    for child in root:
                        if 'cctv' in child.tag.lower():
                            camera_elements.extend(list(child))
                        elif len(list(child)) > 0 and any('cctv' in grandchild.tag.lower() for grandchild in child):
                            camera_elements.extend(list(child))
                    
                    # 方法2：使用 XPath 風格搜尋
                    if not camera_elements:
                        # 嘗試找到包含 CCTVID 的元素
                        for elem in root.iter():
                            for child in elem:
                                if child.tag == 'CCTVID':
                                    camera_elements.append(elem)
                                    break
                    
                    print(f"📊 總共找到 {len(camera_elements)} 個監視器")
                    
                    if camera_elements:
                        # 分析監視器欄位
                        print("\n" + "=" * 40)
                        print("監視器欄位分析")
                        print("=" * 40)
                        
                        # 統計所有欄位
                        all_fields = set()
                        for camera in camera_elements[:10]:  # 只看前10個
                            for field in camera:
                                all_fields.add(field.tag)
                        
                        print(f"🏷️ 監視器欄位列表 (共 {len(all_fields)} 個):")
                        for field in sorted(all_fields):
                            print(f"   - {field}")
                        
                        # 詳細分析第一個監視器
                        print(f"\n📹 第一個監視器詳細資料:")
                        first_camera = camera_elements[0]
                        camera_data = {}
                        
                        for field in first_camera:
                            field_value = field.text.strip() if field.text else ""
                            camera_data[field.tag] = field_value
                            
                            # 顯示重要欄位
                            if field.tag in ['CCTVID', 'SubAuthorityCode', 'VideoStreamURL', 'PositionLat', 'PositionLon', 'RoadName', 'RoadClass', 'Start', 'End']:
                                if len(field_value) > 80:
                                    display_value = field_value[:80] + "..."
                                else:
                                    display_value = field_value
                                print(f"   {field.tag}: {display_value}")
                        
                        # 分析道路分類分布（RoadClass）
                        print(f"\n🛣️ 道路分類分布 (RoadClass):")
                        road_classes = {}
                        
                        for camera in camera_elements:
                            road_class = None
                            for field in camera:
                                if field.tag == 'RoadClass':
                                    road_class = field.text.strip() if field.text else ""
                                    break
                            
                            if road_class:
                                road_classes[road_class] = road_classes.get(road_class, 0) + 1
                        
                        # 道路分類對照表
                        road_class_mapping = {
                            '0': '國道',
                            '1': '快速道路',
                            '2': '市區快速道路',
                            '3': '省道',
                            '4': '縣道',
                            '5': '鄉道',
                            '6': '市區一般道路',
                            '7': '匝道'
                        }
                        
                        for code, count in sorted(road_classes.items()):
                            road_type = road_class_mapping.get(code, f"未知({code})")
                            print(f"   {code} ({road_type}): {count} 個監視器")
                        
                        # 分析道路名稱
                        print(f"\n🏷️ 道路名稱樣本:")
                        road_names = set()
                        
                        for camera in camera_elements[:20]:
                            for field in camera:
                                if field.tag == 'RoadName' and field.text:
                                    road_names.add(field.text.strip())
                                    break
                        
                        for i, road_name in enumerate(sorted(list(road_names))[:10]):
                            print(f"   {i+1}. {road_name}")
                        
                        # 檢查影像 URL 格式
                        print(f"\n🎥 影像 URL 格式分析:")
                        video_url_samples = []
                        
                        for camera in camera_elements[:5]:
                            for field in camera:
                                if field.tag == 'VideoStreamURL' and field.text:
                                    video_url_samples.append(field.text.strip())
                                    break
                        
                        for i, url in enumerate(video_url_samples):
                            if len(url) > 60:
                                display_url = url[:60] + "..."
                            else:
                                display_url = url
                            print(f"   樣本 {i+1}: {display_url}")
                        
                        # 儲存範例資料到 JSON
                        sample_data = {
                            "total_cameras": len(camera_elements),
                            "fields": list(all_fields),
                            "road_classes": road_classes,
                            "road_class_mapping": road_class_mapping,
                            "road_names": list(road_names),
                            "sample_camera": camera_data,
                            "video_url_samples": video_url_samples,
                            "analysis_time": datetime.now().isoformat()
                        }
                        
                        with open("freeway_xml_analysis.json", "w", encoding="utf-8") as f:
                            json.dump(sample_data, f, indent=2, ensure_ascii=False)
                        
                        print(f"\n💾 分析結果已儲存到 freeway_xml_analysis.json")
                        
                    else:
                        print("❌ 未找到監視器資料")
                
                except ET.ParseError as e:
                    print(f"❌ XML 解析失敗: {e}")
                    # 顯示 XML 開頭用於除錯
                    print(f"XML 開頭內容: {xml_content[:500]}")
                
    except Exception as e:
        print(f"❌ 請求失敗: {e}")

# 執行分析
if __name__ == "__main__":
    asyncio.run(analyze_freeway_xml())
