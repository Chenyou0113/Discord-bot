#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析公路總局監視器 API 資料結構
"""

import aiohttp
import asyncio
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import ssl

async def analyze_highway_cameras():
    """分析公路總局監視器 API"""
    
    url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
    
    # 設定 SSL 上下文
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"🔍 正在分析公路總局監視器 API...")
            print(f"URL: {url}")
            print("=" * 80)
            
            async with session.get(url, ssl=ssl_context) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    print(f"✅ API 回應成功 (狀態碼: {response.status})")
                    print(f"📄 資料長度: {len(xml_data)} 字元")
                    
                    # 解析 XML
                    try:
                        root = ET.fromstring(xml_data)
                        
                        # 獲取命名空間
                        namespace = {'ns': 'http://traffic.transportdata.tw/standard/traffic/schema/'}
                        
                        # 基本資訊
                        update_time = root.find('ns:UpdateTime', namespace)
                        update_interval = root.find('ns:UpdateInterval', namespace)
                        authority_code = root.find('ns:AuthorityCode', namespace)
                        
                        print(f"\n📊 API 基本資訊:")
                        print(f"   更新時間: {update_time.text if update_time is not None else 'N/A'}")
                        print(f"   更新間隔: {update_interval.text if update_interval is not None else 'N/A'} 秒")
                        print(f"   機關代碼: {authority_code.text if authority_code is not None else 'N/A'}")
                        
                        # 獲取所有監視器
                        cctvs = root.findall('.//ns:CCTV', namespace)
                        print(f"\n🎥 監視器總數: {len(cctvs)}")
                        
                        if cctvs:
                            # 分析第一個監視器的結構
                            first_cctv = cctvs[0]
                            print(f"\n🔍 監視器資料結構分析 (第一筆資料):")
                            
                            sample_data = {}
                            
                            # 遍歷所有子元素
                            for child in first_cctv:
                                tag_name = child.tag.replace('{http://traffic.transportdata.tw/standard/traffic/schema/}', '')
                                sample_data[tag_name] = child.text
                                print(f"   {tag_name}: {child.text}")
                            
                            # 統計不同類型的監視器
                            locations = {}
                            road_sections = {}
                            
                            print(f"\n📍 正在統計監視器分布...")
                            
                            for i, cctv in enumerate(cctvs[:100]):  # 只分析前100個避免太慢
                                try:
                                    location_info = cctv.find('ns:LocationInfo', namespace)
                                    if location_info is not None:
                                        city = location_info.find('ns:City', namespace)
                                        district = location_info.find('ns:District', namespace)
                                        
                                        if city is not None:
                                            city_name = city.text
                                            if city_name not in locations:
                                                locations[city_name] = 0
                                            locations[city_name] += 1
                                    
                                    road_section = cctv.find('ns:RoadSection', namespace)
                                    if road_section is not None:
                                        section_name = road_section.text
                                        if section_name and section_name not in road_sections:
                                            road_sections[section_name] = 0
                                        if section_name:
                                            road_sections[section_name] += 1
                                
                                except Exception as e:
                                    print(f"   處理監視器 {i} 時發生錯誤: {str(e)}")
                            
                            # 顯示統計結果
                            print(f"\n🏙️ 監視器地區分布 (前10名):")
                            sorted_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)
                            for city, count in sorted_locations[:10]:
                                print(f"   {city}: {count} 個")
                            
                            print(f"\n🛣️ 路段分布 (前10名):")
                            sorted_sections = sorted(road_sections.items(), key=lambda x: x[1], reverse=True)
                            for section, count in sorted_sections[:10]:
                                print(f"   {section}: {count} 個")
                            
                            # 檢查圖片 URL 格式
                            print(f"\n🖼️ 圖片 URL 分析:")
                            image_urls = []
                            for cctv in cctvs[:5]:  # 分析前5個
                                image_url = cctv.find('ns:VideoImageURL', namespace)
                                if image_url is not None and image_url.text:
                                    image_urls.append(image_url.text)
                                    print(f"   {image_url.text}")
                            
                            # 保存範例資料
                            sample_file = {
                                "api_info": {
                                    "url": url,
                                    "update_time": update_time.text if update_time is not None else None,
                                    "total_cameras": len(cctvs),
                                    "analysis_time": datetime.now().isoformat()
                                },
                                "sample_camera": sample_data,
                                "locations": dict(sorted_locations[:20]),
                                "road_sections": dict(sorted_sections[:20]),
                                "sample_image_urls": image_urls
                            }
                            
                            with open("highway_cameras_analysis.json", "w", encoding="utf-8") as f:
                                json.dump(sample_file, f, ensure_ascii=False, indent=2)
                            
                            print(f"\n💾 分析結果已保存到 highway_cameras_analysis.json")
                        
                    except ET.ParseError as e:
                        print(f"❌ XML 解析失敗: {str(e)}")
                        print(f"📄 原始資料前500字元:")
                        print(xml_data[:500])
                    
                else:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    print(f"錯誤內容: {await response.text()}")
    
    except Exception as e:
        print(f"❌ 分析過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    asyncio.run(analyze_highway_cameras())

if __name__ == "__main__":
    main()
