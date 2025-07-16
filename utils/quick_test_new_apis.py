#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試新增的 API
"""

import requests
import json
import xml.etree.ElementTree as ET

def test_alert_water_level():
    """測試警戒水位 API"""
    print("🚨 測試警戒水位 API...")
    
    try:
        url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=D2A498A6-8706-42FB-B623-C08C9665BDFD"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            if content.startswith('\ufeff'):
                content = content[1:]
            
            data = json.loads(content)
            print(f"✅ 警戒水位資料: {len(data)} 筆")
            
            if data:
                first = data[0]
                print("欄位:", list(first.keys()))
                return data[:5]  # 回傳前5筆測試
        else:
            print(f"❌ 警戒水位 API 失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 警戒水位測試失敗: {e}")
    
    return []

def test_river_data():
    """測試河川資料 API"""
    print("\n🏞️ 測試河川資料 API...")
    
    try:
        url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=336F84F7-7CFF-4084-9698-813DD1A916FE"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            if content.startswith('\ufeff'):
                content = content[1:]
            
            data = json.loads(content)
            print(f"✅ 河川資料: {len(data)} 筆")
            
            if data:
                first = data[0]
                print("欄位:", list(first.keys()))
                return data[:5]  # 回傳前5筆測試
        else:
            print(f"❌ 河川資料 API 失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 河川資料測試失敗: {e}")
    
    return []

def test_highway_cameras():
    """測試公路監視器 API"""
    print("\n🛣️ 測試公路監視器 API...")
    
    try:
        url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            
            root = ET.fromstring(content)
            cameras = []
            
            # 解析 XML 結構
            for cctv in root.findall('.//CCTV'):
                camera_info = {}
                for child in cctv:
                    camera_info[child.tag] = child.text
                cameras.append(camera_info)
            
            print(f"✅ 公路監視器: {len(cameras)} 筆")
            
            if cameras:
                first = cameras[0]
                print("欄位:", list(first.keys()))
                return cameras[:5]  # 回傳前5筆測試
        else:
            print(f"❌ 公路監視器 API 失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 公路監視器測試失敗: {e}")
    
    return []

if __name__ == "__main__":
    print("🔍 快速測試新增的 API")
    print("=" * 40)
    
    alert_data = test_alert_water_level()
    river_data = test_river_data()
    highway_data = test_highway_cameras()
    
    print("\n📋 測試結果摘要:")
    print(f"警戒水位資料: {len(alert_data)} 筆")
    print(f"河川資料: {len(river_data)} 筆")
    print(f"公路監視器: {len(highway_data)} 筆")
    
    if alert_data:
        print(f"\n警戒水位範例: {alert_data[0]}")
    
    if river_data:
        print(f"\n河川資料範例: {river_data[0]}")
    
    if highway_data:
        print(f"\n公路監視器範例: {highway_data[0]}")
