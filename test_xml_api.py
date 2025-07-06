#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水利署河川監視器 XML API
"""

import requests
import xml.etree.ElementTree as ET

def test_xml_api():
    """測試 XML 格式的 API"""
    
    xml_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=xml&id=362C7288-F378-4BF2-966C-2CD961732C52"
    
    try:
        print("🔍 測試水利署河川監視器 XML API...")
        response = requests.get(xml_url, timeout=60)
        
        if response.status_code == 200:
            # 解析 XML
            root = ET.fromstring(response.content)
            
            print(f"✅ API 請求成功，狀態碼: {response.status_code}")
            print(f"📊 根元素: {root.tag}")
            
            # 找到所有的資料項目
            items = root.findall('.//diffgr:diffgram//NewDataSet//Table', {'diffgr': 'urn:schemas-microsoft-com:xml-diffgram-v1'})
            if not items:
                # 嘗試其他可能的路徑
                items = root.findall('.//Table')
            if not items:
                items = root.findall('.//*')[:10]  # 取前10個元素作為樣本
            
            print(f"📋 找到 {len(items)} 筆資料")
            
            if items:
                # 分析前幾筆宜蘭縣的資料
                yilan_count = 0
                for i, item in enumerate(items):
                    if i >= 20:  # 限制檢查數量
                        break
                    
                    # 提取各個欄位
                    fields = {}
                    for child in item:
                        fields[child.tag] = child.text if child.text else ''
                    
                    county = fields.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
                    district = fields.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '')
                    
                    if '宜蘭' in county or '宜蘭' in district:
                        yilan_count += 1
                        if yilan_count <= 3:  # 只顯示前3個宜蘭的監視器
                            print(f"\n--- 宜蘭縣監視器 {yilan_count} ---")
                            print(f"CameraID: {fields.get('CameraID', 'N/A')}")
                            print(f"CameraName: {fields.get('CameraName', 'N/A')}")
                            print(f"VideoSurveillanceStationName: {fields.get('VideoSurveillanceStationName', 'N/A')}")
                            print(f"CountiesAndCities: {fields.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', 'N/A')}")
                            print(f"AdministrativeDistrict: {fields.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', 'N/A')}")
                            print(f"ImageURL: {fields.get('ImageURL', 'N/A')}")
                            print(f"Status: {fields.get('Status', 'N/A')}")
                            print(f"Latitude: {fields.get('latitude_4326', 'N/A')}")
                            print(f"Longitude: {fields.get('Longitude_4326', 'N/A')}")
                            
                            # 檢查 ImageURL 是否有效
                            image_url = fields.get('ImageURL', '')
                            if image_url and 'http' in image_url:
                                print(f"✅ 影像 URL 可用: {image_url}")
                            else:
                                print(f"❌ 影像 URL 不可用: {image_url}")
                
                print(f"\n📊 總共找到 {yilan_count} 個宜蘭縣監視器")
                
                # 顯示第一筆資料的所有欄位作為範例
                if items:
                    first_item = items[0]
                    print(f"\n📋 第一筆資料的所有欄位:")
                    for child in first_item:
                        value = child.text if child.text else ''
                        if len(value) > 100:
                            value = value[:100] + "..."
                        print(f"  {child.tag}: {value}")
        
        else:
            print(f"❌ API 請求失敗，狀態碼: {response.status_code}")
            print(f"回應內容: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_xml_api()
