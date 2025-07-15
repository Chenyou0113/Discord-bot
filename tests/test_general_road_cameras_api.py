#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試一般道路監視器 API
"""

import requests
import json

def test_general_road_cameras_api():
    """測試一般道路監視器 API"""
    
    api_urls = [
        "https://tisvcloud.freeway.gov.tw/api/v1/road/camera/snapshot/info/all",  # 省道
        "https://traffic.transportdata.tw/api/basic/v2/Camera/CameraInfo/Road/City?format=json",  # 備用 API
    ]
    
    for i, api_url in enumerate(api_urls, 1):
        print(f"\n🔍 測試 API {i}: {api_url}")
        
        try:
            response = requests.get(api_url, timeout=30, verify=False)
            
            print(f"狀態碼: {response.status_code}")
            print(f"回應長度: {len(response.text)} 字元")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ JSON 解析成功")
                    print(f"資料類型: {type(data)}")
                    
                    if isinstance(data, list):
                        print(f"清單長度: {len(data)}")
                        if data:
                            print(f"第一筆資料: {json.dumps(data[0], ensure_ascii=False, indent=2)[:500]}...")
                    elif isinstance(data, dict):
                        print(f"字典鍵值: {list(data.keys())}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    print(f"回應內容前 500 字元: {response.text[:500]}")
            else:
                print(f"❌ API 請求失敗")
                print(f"回應內容: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 請求失敗: {e}")

def test_alternative_apis():
    """測試替代的監視器 API"""
    
    alternative_apis = [
        "https://data.gov.tw/api/v2/rest/datastore/116220",  # 政府開放資料
        "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/C-B0025-001?Authorization=&downloadType=WEB&format=JSON",  # 中央氣象局
        "https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_alldesc.json",  # 台北市
    ]
    
    print("\n" + "="*50)
    print("測試替代 API:")
    
    for i, api_url in enumerate(alternative_apis, 1):
        print(f"\n🔍 測試替代 API {i}: {api_url}")
        
        try:
            response = requests.get(api_url, timeout=30, verify=False)
            print(f"狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ API 可用")
                print(f"回應長度: {len(response.text)} 字元")
                
                # 嘗試解析 JSON
                try:
                    data = response.json()
                    print(f"✅ JSON 解析成功")
                    if isinstance(data, dict) and 'result' in data:
                        print(f"找到 result 欄位，內容: {type(data['result'])}")
                except:
                    print("⚠️ 非 JSON 格式或解析失敗")
            else:
                print(f"❌ API 不可用，狀態碼: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 請求失敗: {e}")

if __name__ == "__main__":
    print("🔍 測試一般道路監視器 API 狀況")
    test_general_road_cameras_api()
    test_alternative_apis()
    
    print("\n" + "="*50)
    print("📊 測試完成")
    print("如果所有 API 都無法使用，可能需要:")
    print("1. 檢查網路連線")
    print("2. 尋找新的 API 來源")
    print("3. 聯繫相關單位確認 API 狀態")
