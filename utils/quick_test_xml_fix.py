#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試修改後的水利防災監控影像 API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import xml.etree.ElementTree as ET

def quick_test_xml_api():
    """快速測試 XML API"""
    
    url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=xml&id=362C7288-F378-4BF2-966C-2CD961732C52"
    
    try:
        print("🔍 快速測試水利防災監控影像 XML API...")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ API 請求成功，狀態碼: {response.status_code}")
            
            # 解析 XML
            root = ET.fromstring(response.content)
            
            # 查找 Table 元素
            items = root.findall('.//diffgr:diffgram//NewDataSet//Table', 
                               {'diffgr': 'urn:schemas-microsoft-com:xml-diffgram-v1'})
            if not items:
                items = root.findall('.//Table')
            
            print(f"📋 找到 {len(items)} 個監視器")
            
            # 檢查宜蘭縣監視器
            yilan_count = 0
            with_image_url = 0
            
            def get_xml_text(element, tag_name, default=''):
                elem = element.find(tag_name)
                return elem.text if elem is not None and elem.text else default
            
            for item in items:
                county = get_xml_text(item, 'CountiesAndCitiesWhereTheMonitoringPointsAreLocated')
                if '宜蘭' in county:
                    yilan_count += 1
                    
                    name = get_xml_text(item, 'VideoSurveillanceStationName') or get_xml_text(item, 'CameraName')
                    district = get_xml_text(item, 'AdministrativeDistrictWhereTheMonitoringPointIsLocated')
                    image_url = get_xml_text(item, 'ImageURL')
                    
                    if image_url:
                        with_image_url += 1
                    
                    if yilan_count <= 5:  # 只顯示前5個
                        print(f"\n🎯 宜蘭縣監視器 {yilan_count}:")
                        print(f"  名稱: {name}")
                        print(f"  行政區: {district}")
                        print(f"  影像 URL: {image_url if image_url else '❌ 暫不可用'}")
                        if image_url:
                            print("  ✅ 有影像 URL！")
            
            print(f"\n📊 宜蘭縣監視器統計:")
            print(f"  總數: {yilan_count}")
            print(f"  有影像 URL: {with_image_url}")
            print(f"  無影像 URL: {yilan_count - with_image_url}")
            
            if with_image_url > 0:
                print(f"\n🎉 成功！{with_image_url} 個宜蘭縣監視器現在有影像 URL了！")
            else:
                print(f"\n⚠️ 宜蘭縣監視器仍然沒有影像 URL")
        
        else:
            print(f"❌ API 請求失敗，狀態碼: {response.status_code}")
    
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    quick_test_xml_api()
