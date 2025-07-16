#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公路監視器縣市快速分析
根據經緯度座標推測監視器所在縣市
"""

import asyncio
import aiohttp
import ssl
import xml.etree.ElementTree as ET
import json
from collections import defaultdict

class SimpleCityMapper:
    """簡化的縣市映射器"""
    
    def __init__(self):
        # 台灣主要縣市經緯度範圍
        self.city_bounds = {
            "台北市": {"lat": (25.0, 25.3), "lon": (121.4, 121.7)},
            "新北市": {"lat": (24.6, 25.3), "lon": (121.2, 122.0)},
            "桃園市": {"lat": (24.8, 25.1), "lon": (121.0, 121.5)},
            "台中市": {"lat": (24.0, 24.5), "lon": (120.4, 121.0)},
            "台南市": {"lat": (22.9, 23.4), "lon": (120.0, 120.5)},
            "高雄市": {"lat": (22.4, 23.1), "lon": (120.1, 120.7)},
            "基隆市": {"lat": (25.1, 25.2), "lon": (121.6, 121.8)},
            "新竹市": {"lat": (24.7, 24.9), "lon": (120.9, 121.1)},
            "新竹縣": {"lat": (24.4, 25.0), "lon": (120.7, 121.2)},
            "苗栗縣": {"lat": (24.2, 24.8), "lon": (120.5, 121.1)},
            "彰化縣": {"lat": (23.8, 24.3), "lon": (120.3, 120.8)},
            "雲林縣": {"lat": (23.4, 23.9), "lon": (120.1, 120.6)},
            "嘉義縣": {"lat": (23.2, 23.7), "lon": (120.1, 120.7)},
            "屏東縣": {"lat": (22.0, 23.0), "lon": (120.2, 120.9)},
            "宜蘭縣": {"lat": (24.2, 24.8), "lon": (121.3, 122.0)},
            "花蓮縣": {"lat": (23.0, 24.5), "lon": (121.0, 121.8)},
            "台東縣": {"lat": (22.3, 23.5), "lon": (120.8, 121.6)}
        }
    
    def get_city_by_coordinates(self, lat, lon):
        """根據經緯度獲取縣市"""
        try:
            lat = float(lat)
            lon = float(lon)
            
            # 檢查每個縣市的範圍
            for city, bounds in self.city_bounds.items():
                lat_min, lat_max = bounds["lat"]
                lon_min, lon_max = bounds["lon"]
                
                if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                    return city
            
            return "其他"
            
        except (ValueError, TypeError):
            return "未知"

async def quick_city_analysis():
    """快速分析縣市分布"""
    
    print("🗺️ 公路監視器縣市分析")
    print("=" * 40)
    
    url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
    mapper = SimpleCityMapper()
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📡 正在獲取監視器資料...")
            
            async with session.get(url, ssl=ssl_context, timeout=30) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    print(f"✅ 資料獲取成功")
                    
                    # 解析 XML
                    root = ET.fromstring(xml_data)
                    namespace = {'ns': 'http://traffic.transportdata.tw/standard/traffic/schema/'}
                    cctvs = root.findall('.//ns:CCTV', namespace)
                    
                    print(f"📊 總監視器數量: {len(cctvs)}")
                    
                    city_count = defaultdict(int)
                    
                    for cctv in cctvs:
                        try:
                            camera_data = {}
                            for child in cctv:
                                tag_name = child.tag.replace('{http://traffic.transportdata.tw/standard/traffic/schema/}', '')
                                camera_data[tag_name] = child.text
                            
                            lat = camera_data.get('PositionLat')
                            lon = camera_data.get('PositionLon')
                            
                            if lat and lon:
                                city = mapper.get_city_by_coordinates(lat, lon)
                                city_count[city] += 1
                        
                        except Exception:
                            continue
                    
                    # 顯示結果
                    print(f"\n📊 縣市分布統計:")
                    print("=" * 30)
                    
                    sorted_cities = sorted(city_count.items(), key=lambda x: x[1], reverse=True)
                    
                    available_cities = []
                    for city, count in sorted_cities:
                        print(f"   {city}: {count} 個")
                        if city not in ["未知", "其他"] and count >= 10:
                            available_cities.append(city)
                    
                    print(f"\n🎯 建議的縣市選項 (≥10個監視器):")
                    for city in available_cities:
                        print(f"   • {city}")
                    
                    # 保存結果
                    result = {
                        "analysis_time": "2025-06-29",
                        "total_cameras": len(cctvs),
                        "city_distribution": dict(city_count),
                        "available_cities": available_cities
                    }
                    
                    with open("highway_cameras_city_analysis.json", "w", encoding="utf-8") as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    print(f"\n💾 分析結果已保存")
                    return available_cities
                
                else:
                    print(f"❌ API 請求失敗: {response.status}")
                    return []
    
    except Exception as e:
        print(f"❌ 分析失敗: {str(e)}")
        return []

if __name__ == "__main__":
    asyncio.run(quick_city_analysis())
