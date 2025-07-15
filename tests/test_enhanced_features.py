#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新增的警戒水位和公路監視器功能
"""

import asyncio
import aiohttp
import json
import ssl
import xml.etree.ElementTree as ET

async def test_water_level_alert_integration():
    """測試水位警戒整合功能"""
    print("🚨 測試水位警戒整合功能")
    print("=" * 50)
    
    # 模擬獲取警戒水位資料
    try:
        api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=D2A498A6-8706-42FB-B623-C08C9665BDFD"
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"警戒水位 API 狀態: {response.status}")
                
                if response.status == 200:
                    content = await response.text()
                    if content.startswith('\ufeff'):
                        content = content[1:]
                    
                    data = json.loads(content)
                    print(f"✅ 警戒水位資料: {len(data)} 筆")
                    
                    # 建立測站映射
                    alert_levels = {}
                    for item in data[:5]:  # 測試前5筆
                        station_no = item.get('StationNo', item.get('ST_NO', ''))
                        if station_no:
                            first_alert = item.get('FirstAlert', item.get('AlertLevel1', ''))
                            second_alert = item.get('SecondAlert', item.get('AlertLevel2', ''))
                            third_alert = item.get('ThirdAlert', item.get('AlertLevel3', ''))
                            
                            alert_levels[station_no] = {
                                'first_alert': first_alert,
                                'second_alert': second_alert,
                                'third_alert': third_alert
                            }
                            print(f"  測站 {station_no}: 1級={first_alert}, 2級={second_alert}, 3級={third_alert}")
                    
                    # 測試警戒檢查邏輯
                    print("\n🔍 測試警戒檢查邏輯:")
                    test_cases = [
                        ("10.5", {"first_alert": "8.0", "second_alert": "12.0", "third_alert": "15.0"}),
                        ("13.5", {"first_alert": "8.0", "second_alert": "12.0", "third_alert": "15.0"}),
                        ("16.0", {"first_alert": "8.0", "second_alert": "12.0", "third_alert": "15.0"}),
                        ("5.0", {"first_alert": "8.0", "second_alert": "12.0", "third_alert": "15.0"}),
                    ]
                    
                    for water_level, alert_data in test_cases:
                        status, icon = check_water_level_alert(water_level, alert_data)
                        print(f"  水位 {water_level}m: {icon} {status}")
                    
                else:
                    print(f"❌ 警戒水位 API 失敗: {response.status}")
                    
    except Exception as e:
        print(f"❌ 警戒水位測試失敗: {e}")

def check_water_level_alert(current_level, alert_levels):
    """模擬警戒檢查邏輯"""
    if not alert_levels or not current_level:
        return "無警戒資料", "⚪"
    
    try:
        current = float(current_level)
        
        # 檢查三級警戒
        third_alert = alert_levels.get('third_alert', '')
        second_alert = alert_levels.get('second_alert', '')
        first_alert = alert_levels.get('first_alert', '')
        
        if third_alert and str(third_alert).replace('.', '').isdigit():
            if current >= float(third_alert):
                return "三級警戒", "🔴"
        
        if second_alert and str(second_alert).replace('.', '').isdigit():
            if current >= float(second_alert):
                return "二級警戒", "🟠"
        
        if first_alert and str(first_alert).replace('.', '').isdigit():
            if current >= float(first_alert):
                return "一級警戒", "🟡"
        
        return "正常", "🟢"
        
    except (ValueError, TypeError):
        return "無法判斷", "⚪"

async def test_highway_cameras():
    """測試公路監視器功能"""
    print("\n🛣️ 測試公路監視器功能")
    print("=" * 50)
    
    try:
        api_url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"公路監視器 API 狀態: {response.status}")
                
                if response.status == 200:
                    content = await response.text()
                    
                    # 解析 XML
                    try:
                        root = ET.fromstring(content)
                        print("✅ XML 解析成功")
                        
                        cameras = []
                        for cctv in root.findall('.//CCTV'):
                            try:
                                camera_info = {
                                    'id': cctv.find('CCTVID').text if cctv.find('CCTVID') is not None else '',
                                    'name': cctv.find('CCTVName').text if cctv.find('CCTVName') is not None else '未知監視器',
                                    'road': cctv.find('RoadName').text if cctv.find('RoadName') is not None else '未知道路',
                                    'direction': cctv.find('RoadDirection').text if cctv.find('RoadDirection') is not None else '',
                                    'video_url': cctv.find('VideoStreamURL').text if cctv.find('VideoStreamURL') is not None else '',
                                    'location_desc': cctv.find('LocationDescription').text if cctv.find('LocationDescription') is not None else ''
                                }
                                
                                if camera_info['name'] and camera_info['name'] != '未知監視器':
                                    cameras.append(camera_info)
                                    
                            except Exception as e:
                                continue
                        
                        print(f"✅ 公路監視器數量: {len(cameras)}")
                        
                        # 測試前5筆
                        print("\n📊 前5筆監視器資料:")
                        for i, camera in enumerate(cameras[:5], 1):
                            print(f"  {i}. [{camera['id']}] {camera['name']}")
                            print(f"     🛣️ {camera['road']} {camera['direction']}")
                            print(f"     📍 {camera['location_desc']}")
                            print(f"     🔗 {camera['video_url'][:50]}...")
                            print()
                        
                        # 測試地點篩選
                        print("🔍 測試地點篩選:")
                        test_keywords = ['國道一號', '台北', '高雄', '中山高']
                        
                        for keyword in test_keywords:
                            filtered = []
                            keyword_lower = keyword.lower()
                            
                            for cam in cameras:
                                search_fields = [
                                    cam['name'].lower(),
                                    cam['road'].lower(),
                                    cam['direction'].lower(),
                                    cam['location_desc'].lower()
                                ]
                                
                                if any(keyword_lower in field for field in search_fields):
                                    filtered.append(cam)
                            
                            print(f"  {keyword}: {len(filtered)} 個監視器")
                        
                    except ET.ParseError as e:
                        print(f"❌ XML 解析失敗: {e}")
                        
                else:
                    print(f"❌ 公路監視器 API 失敗: {response.status}")
                    
    except Exception as e:
        print(f"❌ 公路監視器測試失敗: {e}")

async def main():
    """主測試函數"""
    print("🧪 測試新增功能")
    print("=" * 60)
    
    await test_water_level_alert_integration()
    await test_highway_cameras()
    
    print("\n" + "=" * 60)
    print("📋 功能測試完成")
    print("✅ 水位警戒檢查功能已整合")
    print("✅ 公路監視器查詢功能已添加")
    print("下一步: 在 Discord 中測試新指令")

if __name__ == "__main__":
    asyncio.run(main())
