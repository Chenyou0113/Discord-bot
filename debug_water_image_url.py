#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析水利防災監控影像 API 的實際影像 URL 欄位
"""

import requests
import json

def analyze_image_url_fields():
    """分析 API 中的影像 URL 欄位"""
    
    url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
    
    try:
        print("🔍 分析水利防災監控影像 API 的影像 URL 欄位...")
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            content = response.text
            if content.startswith('\ufeff'):
                content = content[1:]
            
            data = json.loads(content)
            print(f"總共 {len(data)} 筆資料")
            
            if data:
                # 分析第一筆資料的所有欄位
                first_item = data[0]
                print("\n📋 第一筆資料的所有欄位:")
                for key, value in first_item.items():
                    if value:  # 只顯示有值的欄位
                        if len(str(value)) > 100:
                            display_value = str(value)[:100] + "..."
                        else:
                            display_value = value
                        print(f"  {key}: {display_value}")
                
                # 尋找可能的影像 URL 欄位
                print("\n🔗 尋找影像 URL 相關欄位:")
                url_candidates = []
                for key, value in first_item.items():
                    key_lower = key.lower()
                    if any(keyword in key_lower for keyword in ['url', 'image', 'video', 'stream', 'link', 'http']):
                        url_candidates.append((key, value))
                        print(f"  {key}: {value}")
                
                if not url_candidates:
                    print("  ❌ 未找到明顯的 URL 欄位")
                    print("\n  📋 所有欄位名稱:")
                    for key in first_item.keys():
                        print(f"    - {key}")
                
                # 檢查宜蘭的資料
                print("\n🏞️ 檢查宜蘭縣的監視器資料:")
                yilan_cameras = []
                for item in data:
                    county = item.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
                    if '宜蘭' in county:
                        yilan_cameras.append(item)
                
                print(f"宜蘭縣監視器數量: {len(yilan_cameras)}")
                
                if yilan_cameras:
                    print("\n前3筆宜蘭監視器資料:")
                    for i, camera in enumerate(yilan_cameras[:3], 1):
                        name = camera.get('VideoSurveillanceStationName', camera.get('CameraName', '未知'))
                        county = camera.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '未知')
                        district = camera.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '未知')
                        
                        print(f"\n  {i}. {name}")
                        print(f"     位置: {county} {district}")
                        
                        # 檢查所有可能的 URL 欄位
                        print("     所有欄位:")
                        for key, value in camera.items():
                            if value:
                                if len(str(value)) > 50:
                                    display_value = str(value)[:50] + "..."
                                else:
                                    display_value = value
                                print(f"       {key}: {display_value}")
        else:
            print(f"❌ API 請求失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 分析失敗: {e}")

if __name__ == "__main__":
    analyze_image_url_fields()
