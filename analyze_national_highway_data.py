#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析公路監視器資料格式，檢查國道資料
"""

import asyncio
import aiohttp
import ssl
import xml.etree.ElementTree as ET
from collections import defaultdict

async def analyze_highway_data():
    """分析公路監視器資料格式"""
    print("🔍 分析公路監視器資料格式")
    print("=" * 50)
    
    url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📡 正在獲取監視器資料...")
            
            async with session.get(url, ssl=ssl_context, timeout=30) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    print("✅ 資料獲取成功")
                    
                    # 解析 XML
                    root = ET.fromstring(xml_data)
                    namespace = {'ns': 'http://traffic.transportdata.tw/standard/traffic/schema/'}
                    cctvs = root.findall('.//ns:CCTV', namespace)
                    
                    print(f"📊 總監視器數量: {len(cctvs)}")
                    
                    # 分析道路名稱
                    road_names = defaultdict(int)
                    national_highways = []
                    
                    for i, cctv in enumerate(cctvs[:100]):  # 分析前100個
                        try:
                            camera_data = {}
                            for child in cctv:
                                tag_name = child.tag.replace('{http://traffic.transportdata.tw/standard/traffic/schema/}', '')
                                camera_data[tag_name] = child.text
                            
                            road_name = camera_data.get('RoadName', '')
                            surveillance_desc = camera_data.get('SurveillanceDescription', '')
                            
                            # 統計道路名稱
                            if road_name:
                                road_names[road_name] += 1
                            
                            # 找國道相關的監視器
                            if ('國道' in road_name or '國道' in surveillance_desc or 
                                'highway' in road_name.lower() or 'freeway' in road_name.lower()):
                                national_highways.append({
                                    'CCTVID': camera_data.get('CCTVID', ''),
                                    'RoadName': road_name,
                                    'SurveillanceDescription': surveillance_desc,
                                    'RoadClass': camera_data.get('RoadClass', ''),
                                    'RoadID': camera_data.get('RoadID', '')
                                })
                        
                        except Exception as e:
                            print(f"處理監視器 {i} 時發生錯誤: {str(e)}")
                    
                    # 顯示分析結果
                    print(f"\n🛣️ 道路名稱統計（前20個）:")
                    sorted_roads = sorted(road_names.items(), key=lambda x: x[1], reverse=True)
                    for road, count in sorted_roads[:20]:
                        print(f"   {road}: {count} 個")
                    
                    print(f"\n🏛️ 國道相關監視器:")
                    for highway in national_highways:
                        print(f"   ID: {highway['CCTVID']}")
                        print(f"   道路: {highway['RoadName']}")
                        print(f"   描述: {highway['SurveillanceDescription']}")
                        print(f"   等級: {highway['RoadClass']}")
                        print(f"   道路ID: {highway['RoadID']}")
                        print("   " + "-" * 40)
                    
                    if not national_highways:
                        print("   ❌ 在前100個監視器中未找到明確的國道資料")
                        print("   💡 可能需要檢查其他關鍵字")
                    
                    # 尋找可能的國道關鍵字
                    print(f"\n🔍 搜尋可能的國道關鍵字:")
                    possible_keywords = ['國道', '高速', 'freeway', 'highway', '國1', '國3', '國5', 'N1', 'N3', 'N5']
                    
                    for keyword in possible_keywords:
                        matches = 0
                        for road in road_names.keys():
                            if keyword.lower() in road.lower():
                                matches += 1
                        print(f"   {keyword}: {matches} 個道路包含此關鍵字")
                    
                    # 檢查 RoadClass 和 RoadID 格式
                    print(f"\n📋 道路分類統計:")
                    road_classes = defaultdict(int)
                    road_id_patterns = defaultdict(int)
                    
                    for cctv in cctvs[:200]:  # 檢查前200個
                        try:
                            camera_data = {}
                            for child in cctv:
                                tag_name = child.tag.replace('{http://traffic.transportdata.tw/standard/traffic/schema/}', '')
                                camera_data[tag_name] = child.text
                            
                            road_class = camera_data.get('RoadClass', '')
                            road_id = camera_data.get('RoadID', '')
                            
                            if road_class:
                                road_classes[road_class] += 1
                            
                            if road_id:
                                # 取 RoadID 的前幾個字符作為模式
                                pattern = road_id[:3] if len(road_id) >= 3 else road_id
                                road_id_patterns[pattern] += 1
                        
                        except Exception:
                            continue
                    
                    print("   道路分類 (RoadClass):")
                    for class_code, count in sorted(road_classes.items(), key=lambda x: x[1], reverse=True)[:10]:
                        print(f"      {class_code}: {count} 個")
                    
                    print("   道路ID模式 (RoadID 前3字符):")
                    for pattern, count in sorted(road_id_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
                        print(f"      {pattern}*: {count} 個")
                    
                    return True
                
                else:
                    print(f"❌ API 請求失敗: {response.status}")
                    return False
    
    except Exception as e:
        print(f"❌ 分析失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(analyze_highway_data())
