#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新水利防災監控影像 API
"""

import requests
import json

def test_new_water_cameras_api():
    url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
    
    try:
        print("🔍 測試新的水利防災監控影像 JSON API...")
        print(f"URL: {url}")
        print("-" * 60)
        
        response = requests.get(url, timeout=30)
        print(f"HTTP 狀態碼: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        
        if response.status_code == 200:
            content = response.text
            print(f"回應長度: {len(content)} 字元")
            
            # 處理 BOM
            if content.startswith('\ufeff'):
                content = content[1:]
                print("✅ 移除 UTF-8 BOM")
            
            data = json.loads(content)
            print(f"✅ JSON 解析成功")
            print(f"資料筆數: {len(data)}")
            
            if len(data) > 0:
                first = data[0]
                print("\n📋 第一筆資料的所有欄位:")
                for key, value in first.items():
                    if len(str(value)) > 80:
                        display_value = str(value)[:80] + "..."
                    else:
                        display_value = value
                    print(f"  {key}: {display_value}")
                
                print("\n📊 前 5 筆資料摘要:")
                for i, item in enumerate(data[:5]):
                    name = item.get('VideoSurveillanceStationName', item.get('CameraName', 'Unknown'))
                    county = item.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', 'Unknown')
                    district = item.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', 'Unknown')
                    camera_id = item.get('CameraID', 'Unknown')
                    print(f"  {i+1}. [{camera_id}] {name} - {county} {district}")
                    
                # 分析縣市分布
                counties = {}
                for item in data:
                    county = item.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '未知')
                    counties[county] = counties.get(county, 0) + 1
                
                print(f"\n🏛️ 縣市分布 (共 {len(counties)} 個縣市):")
                for county, count in sorted(counties.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"  {county}: {count} 個監視器")
                    
        else:
            print(f"❌ API 請求失敗，狀態碼: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    test_new_water_cameras_api()
