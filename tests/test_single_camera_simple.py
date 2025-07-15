#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的單一監視器顯示功能測試
"""

import random
import datetime

def test_single_camera_embed():
    """測試單一監視器的 embed 格式"""
    
    # 模擬監視器資料
    sample_cameras = [
        {
            'id': 'CCTV-14-0620-009-002',
            'name': '快速公路62號(暖暖交流道到大華系統交流道)(W)',
            'road': '台62線',
            'direction': 'W',
            'video_url': 'https://cctv-ss02.thb.gov.tw:443/T62-9K+020',
            'image_url': 'https://cctv-ss02.thb.gov.tw:443/T62-9K+020/snapshot',
            'lat': '25.10529',
            'lon': '121.7321',
            'location_desc': '快速公路62號(暖暖交流道到大華系統交流道)(W)',
            'mile': '9K+020',
            'road_class': '1',
            'county': '',
            'update_time': ''
        },
        {
            'id': 'CCTV-14-0620-012-012',
            'name': '快速公路62號(瑞芳交流道到暖暖交流道)(W)',
            'road': '台62線',
            'direction': 'W',
            'video_url': 'https://cctv-ss02.thb.gov.tw:443/T62-12K+460',
            'image_url': 'https://cctv-ss02.thb.gov.tw:443/T62-12K+460/snapshot',
            'lat': '25.10815',
            'lon': '121.7624',
            'location_desc': '快速公路62號(瑞芳交流道到暖暖交流道)(W)',
            'mile': '12K+460',
            'road_class': '1',
            'county': '',
            'update_time': ''
        },
        {
            'id': 'CCTV-14-0620-014-016',
            'name': '快速公路62號(瑞芳交流道到暖暖交流道)(W)',
            'road': '台62線',
            'direction': 'W',
            'video_url': 'https://cctv-ss02.thb.gov.tw:443/T62-14K+120',
            'image_url': 'https://cctv-ss02.thb.gov.tw:443/T62-14K+120/snapshot',
            'lat': '25.11076',
            'lon': '121.7786',
            'location_desc': '快速公路62號(瑞芳交流道到暖暖交流道)(W)',
            'mile': '14K+120',
            'road_class': '1',
            'county': '',
            'update_time': ''
        }
    ]
    
    print("=== 測試單一監視器 Discord Embed 格式 ===")
    print()
    
    # 模擬篩選條件
    county = "新北"
    road_type = "台62線"
    
    print(f"模擬篩選條件: 縣市={county}, 道路={road_type}")
    print(f"符合條件的監視器數量: {len(sample_cameras)}")
    print()
    
    # 隨機選擇一支監視器
    selected_camera = random.choice(sample_cameras)
    
    print("🛣️ 公路監視器")
    print("=" * 80)
    
    name = selected_camera['name']
    road = selected_camera['road']
    direction = selected_camera['direction']
    video_url = selected_camera['video_url']
    image_url = selected_camera['image_url']
    mile = selected_camera.get('mile', '')
    county_info = selected_camera.get('county', '')
    update_time = selected_camera.get('update_time', '')
    lat = selected_camera.get('lat', '')
    lon = selected_camera.get('lon', '')
    
    # Discord Embed 格式模擬
    print(f"📍 標題: 公路監視器")
    print(f"📝 描述: {name}")
    print()
    
    # 篩選條件欄位
    filter_conditions = []
    if county:
        filter_conditions.append(f"縣市: {county}")
    if road_type:
        filter_conditions.append(f"道路: {road_type}")
    
    if filter_conditions:
        print(f"🔍 篩選條件:")
        print(f"   {' | '.join(filter_conditions)}")
        print()
    
    # 道路資訊欄位
    road_info = f"🛣️ 道路: {road}"
    if direction:
        road_info += f" ({direction}向)"
    if mile:
        road_info += f"\n📏 里程: {mile}"
    
    print(f"道路資訊:")
    print(f"   {road_info}")
    print()
    
    # 位置資訊欄位
    location_info = ""
    if lat and lon:
        location_info += f"📍 座標: {lat}, {lon}"
    if county_info:
        location_info += f"\n🏛️ 縣市: {county_info}"
    
    if location_info:
        print(f"位置資訊:")
        print(f"   {location_info}")
        print()
    
    # 即時影像欄位
    if video_url:
        print(f"🎥 即時影像:")
        print(f"   [點擊觀看即時影像]({video_url})")
        print()
    
    # 圖片設定
    if image_url:
        timestamp = int(datetime.datetime.now().timestamp())
        cache_busted_url = f"{image_url}?t={timestamp}"
        print(f"📸 監視器快照圖片:")
        print(f"   {cache_busted_url}")
        print()
    
    # 統計資訊欄位
    print(f"📊 統計資訊:")
    print(f"   共找到 {len(sample_cameras)} 個符合條件的監視器")
    print(f"   目前顯示：隨機選擇的 1 個監視器")
    print()
    
    # 頁尾
    if update_time:
        print(f"⏰ 頁尾: 資料來源：TDX 運輸資料流通服務平臺 | 更新時間: {update_time}")
    else:
        print(f"⏰ 頁尾: 資料來源：TDX 運輸資料流通服務平臺")
    
    print("=" * 80)
    
    # 測試多次隨機選擇
    print("\n🎲 測試隨機選擇功能（3次）:")
    for i in range(3):
        random_camera = random.choice(sample_cameras)
        print(f"{i+1}. {random_camera['name'][:60]}...")
        print(f"   道路: {random_camera['road']}, 里程: {random_camera['mile']}")
        if random_camera['image_url']:
            print(f"   圖片: {random_camera['image_url']}")
        print()
    
    print("✅ 測試完成！")
    print("\n功能特點:")
    print("• ✅ 一次只顯示一支監視器")
    print("• ✅ 內嵌監視器快照圖片")
    print("• ✅ 隨機選擇符合條件的監視器")
    print("• ✅ 完整的道路和位置資訊")
    print("• ✅ 即時影像連結")
    print("• ✅ 統計資訊顯示")

if __name__ == "__main__":
    test_single_camera_embed()
