#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試公路監視器功能
"""

import asyncio
import aiohttp
import ssl
import xml.etree.ElementTree as ET
from datetime import datetime

async def test_highway_cameras():
    """測試公路監視器功能"""
    
    print("🛣️ 測試公路監視器功能")
    print("=" * 60)
    
    # 測試 API 連線
    url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📡 正在連接 API...")
            
            async with session.get(url, ssl=ssl_context, timeout=30) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    print(f"✅ API 連線成功 (狀態碼: {response.status})")
                    print(f"📄 資料長度: {len(xml_data)} 字元")
                    
                    # 解析 XML
                    try:
                        root = ET.fromstring(xml_data)
                        namespace = {'ns': 'http://traffic.transportdata.tw/standard/traffic/schema/'}
                        
                        # 獲取監視器列表
                        cctvs = root.findall('.//ns:CCTV', namespace)
                        print(f"🎥 總監視器數量: {len(cctvs)}")
                        
                        # 測試不同的篩選條件
                        test_cases = [
                            {"location": "台62", "direction": None},
                            {"location": "國道一號", "direction": "N"},
                            {"location": "基隆", "direction": None},
                            {"location": "新北", "direction": "S"}
                        ]
                        
                        for test_case in test_cases:
                            print(f"\n🔍 測試條件: 位置='{test_case['location']}', 方向='{test_case['direction']}'")
                            
                            # 篩選監視器
                            filtered_cameras = []
                            
                            for cctv in cctvs:
                                camera_data = {}
                                
                                # 解析監視器資料
                                for child in cctv:
                                    tag_name = child.tag.replace('{http://traffic.transportdata.tw/standard/traffic/schema/}', '')
                                    camera_data[tag_name] = child.text
                                
                                # 套用篩選條件
                                location_match = True
                                direction_match = True
                                
                                if test_case['location']:
                                    location_lower = test_case['location'].lower()
                                    location_match = any([
                                        location_lower in camera_data.get('RoadName', '').lower(),
                                        location_lower in camera_data.get('SurveillanceDescription', '').lower(),
                                        location_lower in camera_data.get('CCTVID', '').lower()
                                    ])
                                
                                if test_case['direction']:
                                    direction_upper = test_case['direction'].upper()
                                    direction_match = camera_data.get('RoadDirection', '').upper() == direction_upper
                                
                                if location_match and direction_match:
                                    filtered_cameras.append(camera_data)
                            
                            print(f"   📊 符合條件的監視器: {len(filtered_cameras)} 個")
                            
                            # 顯示前3個結果
                            if filtered_cameras:
                                for i, camera in enumerate(filtered_cameras[:3]):
                                    print(f"   {i+1}. {camera.get('SurveillanceDescription', '未知位置')}")
                                    print(f"      道路: {camera.get('RoadName', '未知')}")
                                    print(f"      方向: {camera.get('RoadDirection', '未知')}")
                                    print(f"      圖片: {camera.get('VideoImageURL', '無')}")
                                    
                                    # 測試圖片 URL
                                    image_url = camera.get('VideoImageURL')
                                    if image_url:
                                        image_status = await test_image_url(image_url)
                                        print(f"      圖片狀態: {image_status}")
                                    print()
                            else:
                                print("   ❌ 沒有找到符合條件的監視器")
                        
                        print(f"\n" + "=" * 60)
                        print("📊 統計資訊")
                        print("=" * 60)
                        
                        # 統計道路分布
                        road_stats = {}
                        direction_stats = {}
                        
                        for cctv in cctvs[:500]:  # 只統計前500個避免太慢
                            camera_data = {}
                            for child in cctv:
                                tag_name = child.tag.replace('{http://traffic.transportdata.tw/standard/traffic/schema/}', '')
                                camera_data[tag_name] = child.text
                            
                            road_name = camera_data.get('RoadName', '未知')
                            direction = camera_data.get('RoadDirection', '未知')
                            
                            road_stats[road_name] = road_stats.get(road_name, 0) + 1
                            direction_stats[direction] = direction_stats.get(direction, 0) + 1
                        
                        print("🛣️ 道路分布 (前10名):")
                        sorted_roads = sorted(road_stats.items(), key=lambda x: x[1], reverse=True)
                        for road, count in sorted_roads[:10]:
                            print(f"   {road}: {count} 個")
                        
                        print(f"\n🧭 方向分布:")
                        for direction, count in sorted(direction_stats.items()):
                            print(f"   {direction}: {count} 個")
                        
                    except ET.ParseError as e:
                        print(f"❌ XML 解析失敗: {str(e)}")
                    
                else:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    print(f"錯誤內容: {await response.text()}")
    
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_image_url(image_url):
    """測試圖片 URL 可用性"""
    if not image_url:
        return "❌ 無 URL"
    
    # 確保 URL 有 /snapshot 後綴
    if not image_url.endswith('/snapshot'):
        if not image_url.endswith('/'):
            image_url += '/snapshot'
        else:
            image_url += 'snapshot'
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(image_url, ssl=ssl_context, timeout=5) as response:
                if response.status == 200:
                    return "✅ 可用"
                else:
                    return f"⚠️ 狀態碼 {response.status}"
    except asyncio.TimeoutError:
        return "⏱️ 超時"
    except Exception as e:
        return f"❌ 錯誤: {str(e)[:30]}"

def main():
    """主函數"""
    asyncio.run(test_highway_cameras())

if __name__ == "__main__":
    main()
