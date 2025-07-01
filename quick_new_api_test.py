#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速新 API 測試
"""

import requests
import json

try:
    print("正在請求新水利防災監控影像 API...")
    url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
    response = requests.get(url, timeout=60)
    
    print(f"狀態碼: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        if content.startswith('\ufeff'):
            content = content[1:]
        
        data = json.loads(content)
        print(f"資料筆數: {len(data)}")
        
        if data:
            first = data[0]
            print("第一筆資料欄位:")
            for k, v in first.items():
                if len(str(v)) > 50:
                    v = str(v)[:50] + "..."
                print(f"  {k}: {v}")
            
            # 檢查是否有名稱
            name_fields = ['VideoSurveillanceStationName', 'CameraName', 'name', 'title']
            found_name = False
            for field in name_fields:
                if first.get(field):
                    print(f"\n找到名稱欄位: {field} = {first[field]}")
                    found_name = True
                    break
            
            if not found_name:
                print("\n未找到名稱欄位")
            
            # 檢查縣市資訊
            county_field = 'CountiesAndCitiesWhereTheMonitoringPointsAreLocated'
            if first.get(county_field):
                print(f"縣市欄位: {county_field} = {first[county_field]}")
            
except Exception as e:
    print(f"錯誤: {e}")

print("測試完成")
