#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析公路監視器的縣市分布
根據經緯度座標推測監視器所在縣市
"""

import asyncio
import aiohttp
import ssl
import xml.etree.ElementTree as ET
import json
from collections import defaultdict

class LocationMapper:
    """縣市定位映射器"""
    
    def __init__(self):
        # 台灣縣市經緯度範圍 (粗略範圍)
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
            "南投縣": {"lat": (23.6, 24.1), "lon": (120.6, 121.2)},
            "雲林縣": {"lat": (23.4, 23.9), "lon": (120.1, 120.6)},
            "嘉義市": {"lat": (23.4, 23.5), "lon": (120.4, 120.5)},
            "嘉義縣": {"lat": (23.2, 23.7), "lon": (120.1, 120.7)},
            "屏東縣": {"lat": (22.0, 23.0), "lon": (120.2, 120.9)},
            "宜蘭縣": {"lat": (24.2, 24.8), "lon": (121.3, 122.0)},
            "花蓮縣": {"lat": (23.0, 24.5), "lon": (121.0, 121.8)},
            "台東縣": {"lat": (22.3, 23.5), "lon": (120.8, 121.6)},
            "澎湖縣": {"lat": (23.2, 23.8), "lon": (119.3, 119.8)},
            "金門縣": {"lat": (24.3, 24.6), "lon": (118.2, 118.5)},
            "連江縣": {"lat": (25.9, 26.4), "lon": (119.5, 120.5)}
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
            
            # 如果沒有精確匹配，嘗試找最近的
            min_distance = float('inf')
            closest_city = "未知"
            
            for city, bounds in self.city_bounds.items():
                lat_center = (bounds["lat"][0] + bounds["lat"][1]) / 2
                lon_center = (bounds["lon"][0] + bounds["lon"][1]) / 2
                
                distance = ((lat - lat_center) ** 2 + (lon - lon_center) ** 2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_city = city
            
            # 如果距離太遠，返回未知
            if min_distance > 0.5:  # 約55公里
                return "未知"
            
            return closest_city
            
        except (ValueError, TypeError):
            return "未知"

async def analyze_highway_cameras_by_city():
    """分析公路監視器的縣市分布"""
    
    print("🗺️ 分析公路監視器縣市分布")
    print("=" * 60)
    
    url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
    mapper = LocationMapper()
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📡 正在獲取公路監視器資料...")
            
            async with session.get(url, ssl=ssl_context, timeout=30) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    print(f"✅ 資料獲取成功")
                    
                    # 解析 XML
                    root = ET.fromstring(xml_data)
                    namespace = {'ns': 'http://traffic.transportdata.tw/standard/traffic/schema/'}
                    
                    cctvs = root.findall('.//ns:CCTV', namespace)
                    print(f"📊 總監視器數量: {len(cctvs)}")
                    
                    city_stats = defaultdict(list)
                    road_city_stats = defaultdict(lambda: defaultdict(int))
                    
                    print(f"\n🔍 正在分析縣市分布...")
                    
                    for i, cctv in enumerate(cctvs):
                        try:
                            camera_data = {}
                            for child in cctv:
                                tag_name = child.tag.replace('{http://traffic.transportdata.tw/standard/traffic/schema/}', '')
                                camera_data[tag_name] = child.text
                            
                            # 獲取座標
                            lat = camera_data.get('PositionLat')
                            lon = camera_data.get('PositionLon')
                            road_name = camera_data.get('RoadName', '未知道路')
                            
                            if lat and lon:
                                city = mapper.get_city_by_coordinates(lat, lon)
                                
                                # 添加到統計
                                camera_data['EstimatedCity'] = city
                                city_stats[city].append(camera_data)
                                road_city_stats[city][road_name] += 1
                            
                            # 顯示進度
                            if (i + 1) % 500 == 0:
                                print(f"   處理進度: {i + 1}/{len(cctvs)}")
                        
                        except Exception as e:
                            print(f"   處理監視器 {i} 時發生錯誤: {str(e)}")
                    
                    # 顯示統計結果
                    print(f"\n📊 縣市分布統計:")
                    print("=" * 40)
                    
                    total_located = sum(len(cameras) for city, cameras in city_stats.items() if city != "未知")
                    total_unknown = len(city_stats.get("未知", []))
                    
                    print(f"✅ 成功定位: {total_located} 個監視器")
                    print(f"❓ 未知位置: {total_unknown} 個監視器")
                    print(f"📊 定位成功率: {total_located/(total_located+total_unknown)*100:.1f}%")
                    
                    print(f"\n🏙️ 各縣市監視器數量:")
                    sorted_cities = sorted(city_stats.items(), key=lambda x: len(x[1]), reverse=True)
                    
                    for city, cameras in sorted_cities:
                        if city != "未知":
                            print(f"   {city}: {len(cameras)} 個")
                    
                    if total_unknown > 0:
                        print(f"   未知: {total_unknown} 個")
                    
                    # 顯示各縣市的主要道路
                    print(f"\n🛣️ 各縣市主要道路分布:")
                    for city in sorted([c for c, _ in sorted_cities[:10] if c != "未知"]):
                        roads = road_city_stats[city]
                        top_roads = sorted(roads.items(), key=lambda x: x[1], reverse=True)[:5]
                        
                        print(f"\n   📍 {city}:")
                        for road, count in top_roads:
                            print(f"      {road}: {count} 個")
                    
                    # 保存結果
                    result = {
                        "analysis_time": "2025-06-29",
                        "total_cameras": len(cctvs),
                        "located_cameras": total_located,
                        "unknown_cameras": total_unknown,
                        "city_distribution": {city: len(cameras) for city, cameras in city_stats.items()},
                        "road_city_distribution": dict(road_city_stats),
                        "sample_cameras_by_city": {
                            city: [cameras[0] if cameras else None for city, cameras in sorted_cities[:15]]
                        }
                    }
                    
                    with open("highway_cameras_city_analysis.json", "w", encoding="utf-8") as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    print(f"\n💾 分析結果已保存到 highway_cameras_city_analysis.json")
                    
                    # 生成縣市選項清單
                    available_cities = [city for city, cameras in sorted_cities if city != "未知" and len(cameras) >= 5]
                    
                    print(f"\n🎯 建議的縣市選項 (≥5個監視器):")
                    for city in available_cities:
                        print(f"   • {city}")
                    
                    return available_cities
                
                else:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    return []
    
    except Exception as e:
        print(f"❌ 分析過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """主函數"""
    asyncio.run(analyze_highway_cameras_by_city())

if __name__ == "__main__":
    main()
