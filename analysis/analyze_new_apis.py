#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析新增的 API 資料結構
1. 警戒水位 API
2. 河川資料 API  
3. 公路總局監視器 API
"""

import asyncio
import aiohttp
import json
import ssl
import xml.etree.ElementTree as ET

async def analyze_alert_water_level_api():
    """分析警戒水位 API"""
    print("🚨 分析警戒水位 API")
    print("=" * 50)
    
    api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=D2A498A6-8706-42FB-B623-C08C9665BDFD"
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"狀態碼: {response.status}")
                
                if response.status == 200:
                    content = await response.text()
                    if content.startswith('\ufeff'):
                        content = content[1:]
                    
                    data = json.loads(content)
                    print(f"資料筆數: {len(data)}")
                    
                    if data:
                        first = data[0]
                        print("\n第一筆警戒水位資料欄位:")
                        for key, value in first.items():
                            print(f"  {key}: {value}")
                        
                        print("\n前3筆資料摘要:")
                        for i, item in enumerate(data[:3], 1):
                            station = item.get('StationNo', item.get('ST_NO', 'Unknown'))
                            name = item.get('StationName', item.get('Name', 'Unknown'))
                            alert_level = item.get('AlertLevel', item.get('WaterLevel', 'Unknown'))
                            print(f"  {i}. [{station}] {name} - 警戒水位: {alert_level}")
                
    except Exception as e:
        print(f"❌ 警戒水位 API 分析失敗: {e}")

async def analyze_river_data_api():
    """分析河川資料 API"""
    print("\n🏞️ 分析河川資料 API")
    print("=" * 50)
    
    api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=336F84F7-7CFF-4084-9698-813DD1A916FE"
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"狀態碼: {response.status}")
                
                if response.status == 200:
                    content = await response.text()
                    if content.startswith('\ufeff'):
                        content = content[1:]
                    
                    data = json.loads(content)
                    print(f"資料筆數: {len(data)}")
                    
                    if data:
                        first = data[0]
                        print("\n第一筆河川資料欄位:")
                        for key, value in first.items():
                            print(f"  {key}: {value}")
                        
                        print("\n前3筆資料摘要:")
                        for i, item in enumerate(data[:3], 1):
                            river_name = item.get('RiverName', item.get('Name', 'Unknown'))
                            basin = item.get('Basin', item.get('BasinName', 'Unknown'))
                            print(f"  {i}. 河川: {river_name} - 流域: {basin}")
                
    except Exception as e:
        print(f"❌ 河川資料 API 分析失敗: {e}")

async def analyze_highway_camera_api():
    """分析公路總局監視器 API"""
    print("\n🛣️ 分析公路總局監視器 API")
    print("=" * 50)
    
    api_url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"狀態碼: {response.status}")
                
                if response.status == 200:
                    content = await response.text()
                    
                    # 解析 XML
                    try:
                        root = ET.fromstring(content)
                        print("✅ XML 解析成功")
                        
                        # 找出所有的監視器記錄
                        cameras = []
                        for item in root.findall('.//item'):
                            camera_info = {}
                            for child in item:
                                camera_info[child.tag] = child.text
                            cameras.append(camera_info)
                        
                        print(f"監視器數量: {len(cameras)}")
                        
                        if cameras:
                            first = cameras[0]
                            print("\n第一筆公路監視器資料欄位:")
                            for key, value in first.items():
                                if value and len(str(value)) > 100:
                                    value = str(value)[:100] + "..."
                                print(f"  {key}: {value}")
                            
                            print("\n前3筆資料摘要:")
                            for i, camera in enumerate(cameras[:3], 1):
                                name = camera.get('title', camera.get('name', 'Unknown'))
                                location = camera.get('description', camera.get('location', 'Unknown'))
                                link = camera.get('link', 'No link')
                                print(f"  {i}. {name}")
                                print(f"     位置: {location[:50]}...")
                                print(f"     連結: {link}")
                        
                    except ET.ParseError as e:
                        print(f"❌ XML 解析失敗: {e}")
                        print("內容前500字元:")
                        print(content[:500])
                
    except Exception as e:
        print(f"❌ 公路監視器 API 分析失敗: {e}")

async def main():
    """主分析函數"""
    print("🔍 新增 API 資料結構分析")
    print("=" * 60)
    
    await analyze_alert_water_level_api()
    await analyze_river_data_api()
    await analyze_highway_camera_api()
    
    print("\n" + "=" * 60)
    print("📋 分析完成")
    print("下一步: 整合警戒水位檢查和公路監視器功能")

if __name__ == "__main__":
    asyncio.run(main())
