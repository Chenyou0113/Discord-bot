#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
專門分析宜蘭縣監視器影像 URL 問題
"""

import requests
import json

def analyze_yilan_cameras():
    """分析宜蘭縣監視器資料"""
    
    url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
    
    try:
        print("🔍 分析宜蘭縣監視器影像 URL 問題...")
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            content = response.text
            if content.startswith('\ufeff'):
                content = content[1:]
            
            data = json.loads(content)
            print(f"總共 {len(data)} 筆資料")
            
            # 篩選宜蘭縣的監視器
            yilan_cameras = []
            for item in data:
                location = item.get('LocationDescription', '')
                address = item.get('Address', '')
                county = item.get('County', '')
                
                if ('宜蘭' in location or '宜蘭' in address or '宜蘭' in county):
                    yilan_cameras.append(item)
            
            print(f"\n📍 找到 {len(yilan_cameras)} 個宜蘭縣監視器")
            
            if yilan_cameras:
                print("\n📋 宜蘭縣監視器詳細資料:")
                for i, camera in enumerate(yilan_cameras[:5]):  # 只顯示前5個
                    print(f"\n--- 監視器 {i+1} ---")
                    print(f"CameraID: {camera.get('CameraID', 'N/A')}")
                    print(f"CameraName: {camera.get('CameraName', 'N/A')}")
                    print(f"LocationDescription: {camera.get('LocationDescription', 'N/A')}")
                    print(f"Address: {camera.get('Address', 'N/A')}")
                    print(f"County: {camera.get('County', 'N/A')}")
                    print(f"Longitude: {camera.get('Longitude', 'N/A')}")
                    print(f"Latitude: {camera.get('Latitude', 'N/A')}")
                    
                    # 檢查所有可能的 URL 欄位
                    url_fields = []
                    for key, value in camera.items():
                        if value and isinstance(value, str):
                            key_lower = key.lower()
                            if 'url' in key_lower or 'http' in value.lower() or 'image' in key_lower:
                                url_fields.append((key, value))
                    
                    if url_fields:
                        print("🔗 找到的 URL 相關欄位:")
                        for field_name, field_value in url_fields:
                            print(f"  {field_name}: {field_value}")
                    else:
                        print("❌ 未找到任何 URL 相關欄位")
                    
                    # 顯示所有欄位名稱和值（排除空值）
                    print("📝 所有非空欄位:")
                    for key, value in camera.items():
                        if value and str(value).strip():
                            print(f"  {key}: {value}")
            
            # 也分析一些其他縣市的監視器，比較差異
            print("\n\n🔍 比較其他縣市的監視器結構...")
            other_cameras = []
            for item in data:
                location = item.get('LocationDescription', '')
                county = item.get('County', '')
                
                if county and county != '宜蘭縣' and len(other_cameras) < 3:
                    other_cameras.append(item)
            
            for i, camera in enumerate(other_cameras):
                county = camera.get('County', 'Unknown')
                print(f"\n--- {county} 監視器 {i+1} ---")
                print(f"CameraID: {camera.get('CameraID', 'N/A')}")
                print(f"CameraName: {camera.get('CameraName', 'N/A')}")
                
                # 檢查 URL 欄位
                url_fields = []
                for key, value in camera.items():
                    if value and isinstance(value, str):
                        key_lower = key.lower()
                        if 'url' in key_lower or 'http' in value.lower() or 'image' in key_lower:
                            url_fields.append((key, value))
                
                if url_fields:
                    print("🔗 找到的 URL 相關欄位:")
                    for field_name, field_value in url_fields:
                        print(f"  {field_name}: {field_value}")
                else:
                    print("❌ 未找到任何 URL 相關欄位")
        
        else:
            print(f"❌ API 請求失敗，狀態碼: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 分析失敗: {e}")

if __name__ == "__main__":
    analyze_yilan_cameras()
